import re

from scripts import is_comment_line, re_compile_imports_usage, find_matching_parentheses, replace_old_div


class File:
	
	def __init__(self, pathlib_file):
		self._read_lines(pathlib_file)
		self._docstring_quote = ''
	
	def _read_lines(self, pathlib_file):
		with pathlib_file.open() as fin:
			self.lines = fin.readlines()
			
		with pathlib_file.open() as fin:
			self.file_context = fin.read()
			
	def write(self, pathlib_file):
		with pathlib_file.open('w') as fout:
			fout.write(self.file_context)

	def writelines(self, pathlib_file):
		with pathlib_file.open('w') as fout:
			fout.writelines(self.lines)

	def _iter_lines(self):
		for i in range(len(self.lines)):
			line = self.lines[i].partition('#')[0]

			# # Skip lines containing only strings wrapped in " " or ' '
			# sre_string=re.search(r'^[ \t]*("|\')(?!"|\').+(\1)[ \t]*$', line)
			# if sre_string:
			# 	continue

			# # Skip lines containing only strings wrapped in """ """ or ''' '''
			# # or docstrings spanning multiple lines
			# sre = re.findall(r'("""|\'\'\')', line)
			# if len(sre) == 2:
			# 	continue
			# elif sre and not self._docstring_quote:
			# 	self._docstring_quote = sre[0]
			# 	line = line.partition(self._docstring_quote)[0]
			# elif sre and self._docstring_quote:
			# 	line = line.partition(self._docstring_quote)[2]
			# 	self._docstring_quote = ''
			# elif not sre and self._docstring_quote:
			# 	continue

			if not line.strip() or is_comment_line(line):
				continue

			yield i, line

	def fix_margins(self):
		self.file_context = re.sub(r'\.setMargin\((.*)\)', 
				  '.setContentsMargins(\g<1>, \g<1>, \g<1>, \g<1>)', 
				  self.file_context)
		# for i, line in self._iter_lines():
		# 	self.lines[i] = fix_margins(self.lines[i])
	
	def rename_used_modules(self, modules):
		# sre = re_compile_imports_usage(modules).search(self.file_context)
		self.file_context = re_compile_imports_usage(modules).sub('QtWidgets.\g<2>', self.file_context)
		# if sre:
		# 	print(sre.groups())
		# import_lines = {}
		# imports = defaultdict(list)
		# for i, line in self._iter_lines():
		# 	_, self.lines[i] = rename_modules(line, modules)
		
	def update_imports(self):
		self.file_context = re.sub(r'PyQt4', 'PyQt5', self.file_context)
		if re.search(r'QtWidgets\.\w+', self.file_context):
			self.file_context = re.sub(r'(from PyQt5 import .*)QtGui(.*)', '\g<1>QtGui, QtWidgets\g<2>', self.file_context)
			self.file_context = re.sub(r'(from PyQt5 import .*)QtWidgets, QtWidgets', '\g<1>QtWidgets', self.file_context)
		# sree = re.search(r'QtWidgets|QtCore\.\w+', self.file_context)
		# if sree:
		# 	print(sree.group())
		# 	print(sree.groups())			
		# sre = re.search(r'from PyQt4 import (\w+[, ]*)+', self.file_context)
		# if sre:
		# 	print(sre.group())
		# 	print(sre.groups())
		# if 'from PyQt5' in self.file_context:
		# 	print("YAY")
		# print(self.file_context)
		# for i, line in self._iter_lines():
		# 	upd = parse_imports_all(line)
		# 	if upd:
		# 		print("    {} : {}".format(i, line.strip()))
		# 		print(upd)
		# 		imports.update(upd)
		# 		for k,v in upd.items():
		# 			print("k,v",k,v)
		# 			for vv in v:
		# 				# imp_key = PYQT4_ALL_FROM[vv]
		# 				# print("   imp_key: ", imp_key)
		# 				import_lines[vv] = i
		# 		# # import_lines[vv] = 0
		# 		# # pprint(upd)
		# 		continue
		# 	
		# 	line_back = line
		# 	new_imports, line = rename_modules(line)
		# 	# if len(new_imports)>1:
		# 	if line != line_back:
		# 		# print("    {} : {}".format(i, line.strip()))
		# 		for im in new_imports:
		# 			if not PYQT[5][im] in imports:
		# 				imports[PYQT[5][im]].append(im)
		# 				print(" {} not in imports".format(im))
		# 				print("new_imports: ", new_imports, PYQT[5][im])
		# 		
		# 	# modules = parse_import_usage(line)
		# 	# 
		# 	# if modules:
		# 	# 	pprint(modules)
		# 	# 	for m in modules:
		# 	# 		if not m in import_lines:
		# 	# 			print("    {} : {}".format(i, line))
		# 	# 			print("Missing import: {}".format(m))
		# 	# 			try:
		# 	# 				ll = import_lines[sree[0][0]]
		# 	# 				if not m in self.lines[ll]:
		# 	# 					ln = self.lines[ll].strip('\n')
		# 	# 					ln +=  ", " + m
		# 	# 					self.lines[ll] = ln + '\n'
		# 	# 					import_lines[m] = ll
		# 	# 			except KeyError:
		# 	# 				print("KeyError: {}".format(sree[0][0]))
		# pprint(import_lines)
		# pprint(imports)
	
	def qapp(self):
		self.file_context = re.sub(r'qApp', 'QApplication.instance()', self.file_context)
		
	def fix_qfile_dialog(self):
		# QtWidgets.QFileDialog.getOpenFileName
		# QtWidgets.QFileDialog.getSaveFileName
		for i, line in self._iter_lines():
			sre = re.search(r'QFileDialog\.get(Open|Save)FileName', line)
			if sre:
				pos = sre.end()
				end = find_matching_parentheses(line, pos)
				self.lines[i] = line[:end+1] + '[0]' + line[end+1:]
				print("    {} : {}".format(i, line.strip()))
				# print("    {} : {}".format(i, line_new.strip()))
				print(sre.group())
				print(line[pos:pos+4], line[end-4:end+1])
				print(pos, end)

	def fix_old_div(self, func, op_sym):
		for i, line in self._iter_lines():
			# print("    {} : {}".format(i, line.strip()))
			if 'old_div(' in line:
				self.lines[i] = replace_old_div(line, func, op_sym)
