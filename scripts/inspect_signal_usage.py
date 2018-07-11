#!/usr/bin/env python

from glob import glob
import ast


def show_info(functionNode):
	print("Function name:", functionNode.name)


classes=[]

for f in glob('pyemtbx/*.py'):
	with open(f) as file:
		data = file.readlines()
	
	for line in data:
		# print line.strip()
		lstriped = line.strip()
		if len(lstriped)>0 and lstriped[0] != '#':
			if lstriped[0:5] == 'class':
				print lstriped
			# classes.append(line.strip())

