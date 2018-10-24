import subprocess
import re

import pathlib2

from collections import defaultdict

from .constants import *

cur = pathlib2.Path('.')

files = [
		 # 'libpyEM/qtgui/empmwidgets.py',
		 # 'libpyEM/qtgui/embrowser.py',
		 # 'libpyEM/qtgui/emform.py',
		 # 'libpyEM/qtgui/emsave.py',
		 # 'broken/e2preferences.py',
		 # 'broken/em3Dhelloworld.py',
		 # 'libpyEM/qtgui/emplot2d.py',
		 # 'examples/alignbystars.py',
		 # 'programs/e2tomo_showali.py',
		 # 'programs/e2maskbyclass.py',
		 # 'libpyEM/qtgui/emshapeitem3d.py',
		 # 'libpyEM/qtgui/embrowser.py',
		 'pyemtbx/boxertools.py',
		 # 'examples/e2tomoseg.py'
		 ]

def iter_py_files_debug():
	for p in (pathlib2.Path(f) for f in files):
		yield p

def iter_py_files():
	for p in (p for p in cur.glob('**/*.py') if \
			  not str(p).startswith('sparx') \
			  and not str(p).startswith('scripts') \
			  and p.parent != pathlib2.Path(__file__).parent):
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
