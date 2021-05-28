#!/usr/bin/env python

from pathlib import Path
import sys
from subprocess import run
from EMAN2 import e2getinstalldir


def get_program_files():
	source_path = Path(__file__).resolve().parent / 'programs'
	# print(source_path)

	progs_exclude = {
		"e2.py",
		"e2projectmanager.py",
		"e2unwrap3d.py",
		"e2version.py",
		"e2fhstat.py",
		"e2_real.py",
		"e2proc3d.py",  # uses OptionParser
		"e2seq2pdb.py",  # no help provided
		"e2refine.py",
		"e2eotest.py",
		"e2foldfitter.py",
	}

	progs = set(Path(p).name for p in source_path.glob('e2*.py')) - progs_exclude

	return sorted(progs)


def add_bin_path_to_sys_path():
	sys.path.insert(0, str(Path(e2getinstalldir()) / 'bin'))


def get_parser_options(prog):
	return run([prog], capture_output=True).stdout.decode('utf-8')
	# return run([prog, '--generate_doc'], capture_output=True).stdout.decode('utf-8')


def main():
	progs = get_program_files()
	# print(progs)

	add_bin_path_to_sys_path()

	with open('opts.txt', 'w') as fout:
		fout.write("prog @ option @ default @ type @ help @ \n")
		# options = {}
		options = []
		c=0
		for prog in progs:
			# options[prog] = get_parser_options(prog)
			# options.append(f'{prog}: {o}')
			# options.append(get_parser_options(prog))
			fout.write(get_parser_options(prog))
			print(c, prog)
			c += 1
			# if c>1:
			# 	break
	
		# oo = []
		# for i,k in options.items():
		# 	print(dd = eval(k))
			# for v in dd.keys():
			# 	print(v)
			# 	fout.write(f'{i}: {v}')
		# for i in options:
		# 	fout.write(i)

if __name__ == "__main__":
	main()
