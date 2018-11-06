#!/usr/bin/env python

import argparse
import re

def get_obj_info_daphic(obj_path):
	size = {12884967425:214400000, 17179934721:214400000} 
	addr = {12884967425:0x7f7c2d483010, 17179934721:0x7f7c2080b010}
	return [size, addr]

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
			if ctx != fields[0]:
				if ctx:
					daps.append('# ctx %d' % ctx)
					daps.append(dap)
					daps.append('\n')
				dap = []
			ctx = int(fields[0])
			obj = int(fields[1])
			nr_accs = fields[2]
			addr = [obj_addr[obj], obj_addr[obj] + obj_size[obj] - 1]
			dap.append(str(addr[0]) + '-' + str(addr[1]))
			dap.append("sequential")
			dap.append("4")
			dap.append(str(nr_accs))
	if dap:
		daps.append('# ctx %d' % ctx)
		daps.append(dap)
	return daps

def write_out_daps(output_path, daps):
	with open(output_path, 'w') as mmse_dap:
		for dap in daps:
			dap_string = ""
			if dap[0] == '#':
				dap_string = dap + '\n'
			elif dap == '\n':
				dap_string = '\n'
			else:
				for entity in dap:
					dap_string += entity + ', '
				dap_string = dap_string[0:-2] + '\n'
			mmse_dap.write(dap_string)

if __name__ == "__main__":
	parser = argparse.ArgumentParser()

	parser.add_argument('--dap', type=str, metavar='data_access_pattern',
		help='path to the data access pattern file of ctxobjtracer')
	parser.add_argument('--atrace', type=str, metavar='alloc_trace',
		help='path to the allocation trace file')

	args = parser.parse_args()
	daphic_dap = args.dap
	daphic_obj = args.atrace
	mmse_dap = "daps/daphic/470.lbm"

	if not daphic_dap or not daphic_obj:
		parser.print_help()
		exit(1)

	daps = dap_trans_daphic(daphic_obj, daphic_dap)
	print(daps)
	write_out_daps(mmse_dap, daps)
