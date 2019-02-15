#!/usr/bin/env python

from glob import glob

# for f in glob('pyemtbx/*.py'):
# 	print(f)

# import fnmatch
# import os
# 
# # matches = []
# for root, dirnames, filenames in os.walk('.'):
# 	for filename in fnmatch.filter(filenames, '*.py'):
# 		full_path = os.path.join(root, filename)
# 		# matches.append(full_path)
# 		import_name = full_path.replace(u'/', '.').replace(u'..','.')[:-3]
# 		
# 		# print(import_name)
# 		try:
# 			__import__(import_name)
# 		except:
# 			print("Failed: ", import_name)
# 		
# print(dir())
# # print(matches)
# # print(len(matches))

# import pkgutil
# import importlib
# import sys
# 
# for (module_loader, name, ispkg) in pkgutil.iter_modules(['pyemtbx', 'programs']):
# 	if name == sys.argv[0] or name == '__init__':
# 		continue
# 	print('.' + name, __package__)
# 	# print(module_loader, name, ispkg)
# 	imp = importlib.import_module('.'+name, __package__)
# 	# imp = __import__('.'+name)
# 	print imp
# 
# print(dir())

import ast


# # print node
# # print node.body
# 

def show_info(functionNode):
	print("Function name:", functionNode.name)
# 	print("Args:")
# 	print(dir(functionNode))
# 	# print(functionNode.args.args)
# 	for arg in functionNode.args.args:
# 		#import pdb; pdb.set_trace()
# 		print("\tParameter name:", dir(arg))
# 

# files=[]
# for f in glob('pyemtbx/*.py'):
# 	# files.append(f)
# 	
# 	with open(f) as file:
# 		node = ast.parse(file.read())
# 
# 	functions = [n for n in node.body if isinstance(n, ast.FunctionDef)]
# 	# fields = [n for n in node.body if isinstance(n, ast.FunctionDef)]
# 	classes = [n for n in node.body if isinstance(n, ast.ClassDef)]
# 	
# 	# for field in fields:
# 	# 	show_info(field)
# 	
# 	for function in functions:
# 		show_info(function)
# 	
# 	for class_ in classes:
# 		print("Class name:", class_.name)
# 		methods = [n for n in class_.body if isinstance(n, ast.FunctionDef)]
# 		fields = [n for n in class_.body if isinstance(n, ast)]
# 		for method in methods:
# 			show_info(method)
# 		for field in fields:
# 			print("  Field: ", field)

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

# print classes
# import inspect
# 
# mymodule = __import__('pyemtbx')
# 
# print mymodule
# 
# for element_name in dir(mymodule):
# 	print element_name
# 	element = getattr(mymodule, element_name)
# 	if inspect.isclass(element):
# 		print("class %s" % element_name)
