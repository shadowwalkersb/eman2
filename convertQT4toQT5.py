import os, re, stat
from os.path import normpath

from PyQt5 import QtWidgets, QtCore
main_path = '.'

qtWidgets_modules = dir(QtWidgets)
qtCore_modules = dir(QtCore)

dictWidgets={}
dictCore={}

def fixFile(line_list):
	line_generator = list(line_list)
	changed = False
	num = -1

	for each in line_generator:
		num += 1
		if 'from PyQt4 import' in each.strip():
			line_list[num] = 'from PyQt5 import QtWidgets, QtGui, QtCore\n'
			changed = True
			continue

		result = re.search('QtGui\.(\w+)', each)

		if result and result.group(1) in qtWidgets_modules:
			line_list[num] = each.replace('QtGui', 'QtWidgets')
			changed = True
			dictWidgets[result.group(1)] = 1
			# if result.group(1) not in qtWidgets_modules:
			# 	dictWidgets[result.group(1)] = 0
			# else:
			# 	dictWidgets[result.group(1)] += 1

		if result and result.group(1) in qtCore_modules:
			line_list[num] = each.replace('QtGui', 'QtCore')
			changed = True
			dictCore[result.group(1)] = 1
			# if result.group(1) not in qtCore_modules:
			# 	dictCore[result.group(1)] = 0
			# else:
			# 	dictCore[result.group(1)] += 1

	if changed:
		return ''.join(line_list)

def convert(main_path):
	for dirs, folders, files in os.walk(main_path):
		for each in [x for x in files if x.endswith('.py') and normpath(x) != normpath(__file__)]:
			file_path = os.path.join(dirs, each).replace(os.sep, '/')
			print(file_path)
			# os.chmod(file_path, stat.S_IWRITE)

			with open(file_path, 'r+') as out_file:
				line_list = out_file.readlines()

			fixed_lines = fixFile(line_list)
			# 
			# if fixed_lines:
			# 	print file_path
			# 
			# 	with open(file_path, 'w+') as out_file:
			# 		out_file.write(fixed_lines)

convert(main_path=main_path)
# slf='./convertQT4toQT5.py'
# print(slf)
# print(__file__)
# print(normpath(slf))
# print(normpath(__file__))

for k in dictWidgets.keys():
	print(k)
print(dictCore.keys())
