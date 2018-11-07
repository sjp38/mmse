#!/usr/bin/env python

import argparse
import re

def get_obj_info_daphic(obj_path):
    obj_size = {}
    obj_addr = {}
    with open(obj_path, 'r') as objs:
        for line in objs:
            if line.startswith('#'):
                continue
            fields = re.split(' *\t*\n*', line)
            obj = int(fields[0])
            size = int(fields[2])
            addr = int(fields[3], 0)
            obj_size[obj] = size
            obj_addr[obj] = addr
    return [obj_size, obj_addr]

def dap_trans_daphic(obj_path, dap_path):
    daps = []
    dap = []
    [obj_size, obj_addr] = get_obj_info_daphic(obj_path)
    with open(dap_path, 'r') as org_dap:
        ctx = None
        obj = None
        addr = [None, -1]
        for line in org_dap:
            if line.startswith('#'):
                continue
            fields = re.split('_| |\n', line)
            if ctx != int(fields[0]):
                if ctx:
                    daps.append('# ctx %d\n' % ctx)
                    daps.append(dap)
                dap = []
            ctx = int(fields[0])
            obj = int(fields[1])
            nr_accs = fields[2]
            addr = [obj_addr[obj], obj_addr[obj] + obj_size[obj] - 1]
            dap.append(str(addr[0]) + '-' + str(addr[1]))
            dap.append("sequential")
            dap.append("4")
            dap.append(str(nr_accs))
            dap.append('\n')
    if dap:
        daps.append('# ctx %d\n' % ctx)
        daps.append(dap)
    return daps

def write_out_daps(output_path, daps):
    with open(output_path, 'w') as mmse_dap:
        for dap in daps:
            dap_string = ""
            if dap[0] == '#':
                dap_string = dap
            else:
                for entity in dap:
                    if entity == '\n':
                        dap_string = dap_string[0:-2] + '\n'
                        continue
                    dap_string += entity + ', '
                dap_string += '\n'
            mmse_dap.write(dap_string)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument('--style', choices=['daphic'], default='daphic',
            metavar='dap_style', help='in which style is this dap written?')
    parser.add_argument('--indap', type=str,
            default='daps/others/daphic/470.lbm.dap.dat', metavar='input_dap',
            help='path for input dap')
    parser.add_argument('--inobj', type=str,
            default='daps/others/daphic/470.lbm.alloctrace',
            metavar='input_obj', help='path for object info')
    parser.add_argument('--outdap', type=str, default='daps/daphic/470.lbm',
            metavar='output_dap', help='path to write out translated dap')

    args = parser.parse_args()

    dap_path = args.indap
    obj_path = args.inobj
    output_path = args.outdap
    dap_style = args.style

    daps = dap_trans_daphic(obj_path, dap_path)
    write_out_daps(output_path, daps)
