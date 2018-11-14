#!/usr/bin/env python

import argparse
import re

SECTOR_SIZE = 512

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

def dap_trans_blktrace(dap_path):
    daps = []
    dap = []
    with open(dap_path, 'r') as org_dap:
        for line in org_dap:
            if line.startswith('CPU'):
                break
            if line.startswith('#'):
                continue
            fields = re.split(', ', line.lstrip().rstrip())
            if fields[3] != 'C':
                continue
            time = float(fields[0])
            pid = int(fields[1])
            cmd = fields[2]
            sector_id = int(fields[4])
            acc_size = int(fields[5])
            sector_addr = sector_id * SECTOR_SIZE
            addr = [sector_addr, sector_addr + acc_size - 1]
            dap.append(str(addr[0]) + '-' + str(addr[1]))
            dap.append("sequential")
            dap.append("4")
            dap.append(str(acc_size//4))
            dap.append('\n')

            daps.append('# time %.6fs,\tpid %d\n' % (time, pid))
            daps.append(dap)
            dap = []
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
    subparsers_style = parser.add_subparsers(help = 'choose source dap style')
    subparser_daphic = subparsers_style.add_parser('daphic')
    subparser_blktrace = subparsers_style.add_parser('blktrace')
    
#   daphic
    subparser_daphic.add_argument('src_dap', type = str, 
            help='path for source dap')
    subparser_daphic.add_argument('obj', type = str,
            help = 'path for object info')
    subparser_daphic.add_argument('dst_dap', type = str,
            help = 'path to write out translated dap')
    subparser_daphic.set_defaults(src_style = 'daphic')

#   blktrace
    subparser_blktrace.add_argument('src_dap', type = str,
            help = 'path for source dap')
    subparser_blktrace.add_argument('dst_dap', type = str,
            help = 'path to write out translated dap')
    subparser_blktrace.set_defaults(src_style = 'blktrace')    
    
    args = parser.parse_args()
    src_path = args.src_dap
    dst_path = args.dst_dap
    src_style = args.src_style
    
    if src_style == 'daphic':
        obj_path = args.obj
	daps = dap_trans_daphic(obj_path, src_path)
    elif src_style == 'blktrace':
	daps = dap_trans_blktrace(src_path)
    write_out_daps(dst_path, daps)
