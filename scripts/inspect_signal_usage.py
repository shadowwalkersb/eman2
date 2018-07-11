#!/usr/bin/env python

from glob import glob
import ast


def show_info(functionNode):
	print("Function name:", functionNode.name)

files=[]
for f in glob('pyemtbx/*.py'):
	with open(f) as file:
		node = ast.parse(file.read())

	functions = [n for n in node.body if isinstance(n, ast.FunctionDef)]
	classes = [n for n in node.body if isinstance(n, ast.ClassDef)]
	
	for function in functions:
		show_info(function)
	
	for class_ in classes:
		print("Class name:", class_.name)
		methods = [n for n in class_.body if isinstance(n, ast.FunctionDef)]
		fields = [n for n in class_.body if isinstance(n, ast)]
		for method in methods:
			show_info(method)
		for field in fields:
			print("  Field: ", field)
