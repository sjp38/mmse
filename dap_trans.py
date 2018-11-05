#!/usr/bin/env python

import re

def get_obj_info_daphic(obj_path):
	obj_size = {}
	obj_addr = {}
	with open(obj_path, 'r') as objs:
		for line in objs:
			if line.startswith('#'):
				continue
			fields = re.split(' *\t*\n*', line)
			print(fields)
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
	daphic_dap = "/home/yjlee/470.lbm.dap.dat"
	daphic_obj = "/home/yjlee/470.lbm.alloctrace"
	mmse_dap = "daps/daphic/470.lbm"

	daps = dap_trans_daphic(daphic_obj, daphic_dap)
	write_out_daps(mmse_dap, daps)
