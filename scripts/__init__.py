import ast
import subprocess
import re

import pathlib

from collections import defaultdict

from .constants import *

cur = pathlib.Path('.')

files = [
		 'libpyEM/qtgui/empmwidgets.py',
		 'libpyEM/qtgui/embrowser.py',
		 'libpyEM/qtgui/emform.py',
		 'libpyEM/qtgui/emsave.py',
		 'broken/e2preferences.py',
		 'broken/em3Dhelloworld.py',
		 'libpyEM/qtgui/emplot2d.py',
		 'examples/alignbystars.py',
		 'programs/e2tomo_showali.py',
		 'programs/e2maskbyclass.py',
		 'libpyEM/qtgui/emshapeitem3d.py',
		 'libpyEM/qtgui/embrowser.py',
		 'examples/crystal_index.py',
		 'libpyEM/EMAN2.py',
		 'examples/e2pw_pathrefine.py',
		 'examples/e2spt_refprep.py',
		 'broken/e2modeleval.py'
		 ]

def iter_py_files_debug():
	for p in (pathlib.Path(f) for f in files):
		yield p

def iter_py_files():
	for p in (p for p in cur.glob('**/*.py') if \
			  not str(p).startswith('sparx') \
			  and not str(p).startswith('scripts') \
			  and p.parent != pathlib.Path(__file__).parent):
		yield p

def iter_py_file_lines():
	for p in iter_py_files():
		with p.open() as fin:
			lines = fin.readlines()
		yield lines

def file_readlines(pathlib_file):
	with pathlib_file.open() as fin:
		return fin.readlines()
		
def file_read(pathlib_file):
	with pathlib_file.open() as fin:
		return fin.read()
		
def file_writelines(pathlib_file, lines):
	with pathlib_file.open('w') as fout:
		fout.writelines(lines)

def file_write(pathlib_file, file_content):
	with pathlib_file.open('w') as fout:
		fout.write(file_content)


def git_commit(message):
	subprocess.call(["git", "status"])
	subprocess.call(["git", "add", "."])
	subprocess.call(["git", "commit", "-m", message])


def is_comment_line(line):
	return line.strip()[0] == '#'


def fix_margins(line):
	return re.sub(r'\.setMargin\((.*)\)', 
				  '.setContentsMargins(\g<1>, \g<1>, \g<1>, \g<1>)', 
				  line) 

def fix_delta(line):
	return re.sub(r'event.delta\(\)', 
				  'event.angleDelta().y()', 
				  line) 

def qapp1(file_context):
	return re.sub(r'qApp\.', 'QApplication.', file_context)

def qapp2(file_context):
	return re.sub(r'qApp', 'QApplication.instance()', file_context)

def qapp21(file_context):
	return re.sub(r'QtGui\.QApplication', 'QtWidgets.QApplication', file_context)

def qweb(file_context):
	file_context = re.sub(r'QtWebKit\.QWebView', 'QtWebEngineWidgets.QWebEngineView', file_context)
	file_context = re.sub(r'QtWebKit', 'QtWebEngineWidgets', file_context)
	
	return file_context

def re_compile_imports_usage(modules):
	return re.compile(r'(?:(\bQt\w+)\.)' 
							+ r'(' 
							+ "|".join([r'\b' + k + r'\b' for k in modules]) 
							+ r')')

def rename_module_usage(file_context, parent_module, modules):
	return re_compile_imports_usage(modules).sub('{}.\g<2>'.format(parent_module), file_context)

def rename_imports_pyqt4_to_pyqt5(file_context):
	return re.sub(r'PyQt4', 'PyQt5', file_context)

RE_IMPORTS = re.compile(r'from +(PyQt[4,5](\.(?:' 
						+ "|".join(PYQT_MAIN_MODULES[5].keys()) 
						+ r'))?) +import')

	
def parse_imports_selective(line):
	sre = RE_IMPORTS.search(line)
	imports = defaultdict(list)
	if sre:
		imports_parsed = [s.strip() \
						  for s in line.partition('import')[2].split(',') \
						  if s.strip() in PYQT[4]]
		imports[sre.group(1)].extend(imports_parsed)
		
	return imports

def parse_imports_all(line):
	imports = defaultdict(list)
	sre = re.search(r'from +(PyQt[4,5](?:\.(?:\w+))?) +import', line)
	if sre:
		imports_parsed = [s.strip() \
						  for s in line.partition('import')[2].split(',')]
		imports[sre.group(1)].extend(imports_parsed)
		
	return imports

def parse_import_usage(line):
	sre = re_compile_imports_usage().findall(line)
	res = []
	if sre:
		for s in sre:
			if s[0]:
				res.append(s[0])
			else:
				res.append(s[1])
	return res

def rename_modules(line, modules):
	sre = re_compile_imports_usage(modules).findall(line)
	new_imports = set()
	if sre:
		for s in sre:
			module = s[1]
			parent_module = PYQT[5][module].split('.')[1]
			if s[0]:
				line_partioned = list(line.partition('#'))
				line_partioned[0] = line_partioned[0].replace('.'.join(s),
															  '.'.join([parent_module, module]))
				line = ''.join(line_partioned)
				new_imports.add(parent_module)
	return new_imports, line


def find_matching_parentheses(line, pos):
	count = 0
	for i in range(pos, len(line)):
		if line[i] == '(':
			count += 1
		if line[i] == ')':
			count -= 1
			if count == 0:
				return i
	else:
		return None


SEARCH_FUNC = 'old_div'
lenSEARCH_FUNC = len(SEARCH_FUNC)


def partition_old_div(s):
	p = s.partition(SEARCH_FUNC)
	# print(p)
	if p[1] != '':
		end = find_matching_parentheses(p[2], 0)
		
		return p[0], p[1]+p[2][:end+1], p[2][end+1:]
	else:
		return s, '', ''


def replace_old_div(line, func, op_sym):
	p = partition_old_div(line)
	# print(p)
	if p[1] == '':
		return line
	if not SEARCH_FUNC in p[1][lenSEARCH_FUNC:]:
		res = p[1]
	else:
		res = SEARCH_FUNC +'(' + replace_old_div(p[1][lenSEARCH_FUNC+1:-1], func, op_sym) + ')'
	
	res = old_div_replace_func(res, func, op_sym)
	return p[0] + res + replace_old_div(p[2], func, op_sym)


def old_div_replace_func(s, func, op_sym='/'):
	print(s)

	root = ast.parse(s)
	args = root.body[0].value.args
	
	if func(args):
		print(s)
	
		# for i, arg in enumerate(args):
		# 	print("^"*arg.col_offset)
		loffset = max(args[0].col_offset, max(n.col_offset for n in ast.walk(args[0]) if hasattr(n, 'col_offset')))
		roffset = min(args[1].col_offset, min(n.col_offset for n in ast.walk(args[1]) if hasattr(n, 'col_offset')))
		print("^"*loffset)
		print("^"*roffset)
		ind = s.rfind(',', loffset, roffset)
		# print("^"*(ind+1))
		arg2 = s[ind+1:-1]
		if arg2[0] == ' ':
			space = ' '
		else:
			space = ''
		arg1 = s[len('old_div('):ind] + space
		s = "{}{}{}".format(arg1, op_sym, arg2)
		print(s)
		# for i, arg in enumerate(args):
		# 	print("arg{}:".format(i))
		# 	print("is_float(arg): {}".format(is_float(arg)))

	return s


def is_num_float(node):
	if isinstance(node, ast.Num) and isinstance(node.n, float): return True
	else: return False

def is_func_float(node):
	if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "float": return True
	else: return False

def is_math_func(node):
	if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name) and node.func.value.id == "math": return True
	else: return False

def is_np_func(node):
	if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name) and node.func.value.id == "np": return True
	else: return False

def is_math_const(node):
	if isinstance(node, ast.Attribute) and hasattr(node.value, 'id') and node.value.id == "math": return True
	else: return False

def is_np_const(node):
	if isinstance(node, ast.Attribute) and hasattr(node.value, 'id') and node.value.id == "np": return True
	else: return False

def is_num_int(node):
	if isinstance(node, ast.Num) and isinstance(node.n, int): return True
	else: return False

def is_func_int(node):
	if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "int": return True
	else: return False

def is_func_len(node):
	if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "len": return True
	else: return False

def is_func_size(node):
	if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and "size" in node.func.attr: return True
	else: return False

def is_const_size(node):
	if isinstance(node, ast.Attribute) and "size" in node.attr: return True
	else: return False


funcs_float = [
]

def is_bin_op_float(node):
	if isinstance(node, ast.BinOp):
		return is_bin_op_float(node.left) or is_bin_op_float(node.right)
	else:
		return any(f(node) for f in funcs_float)

funcs_int = [
]

def is_bin_op_int(node):
	if isinstance(node, ast.BinOp):
		return is_bin_op_int(node.left) and is_bin_op_int(node.right)
	else:
		return any(f(node) for f in funcs_int)

def is_float(node):
	# print(node)
	# print(node.func)
	# print(dir(node.func))

	if isinstance(node, ast.Attribute) and hasattr(node.value, 'id') and node.value.id == "math": return True
	if isinstance(node, ast.Attribute) and hasattr(node.value, 'id') and node.value.id == "np": return True
	if isinstance(node, ast.BinOp):
		return is_float(node.left) or is_float(node.right)
