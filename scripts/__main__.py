from scripts.file import File
from . import *

def process_all_files(func, commit_message, *args, **kwargs):
	# for f in iter_py_files_debug():
	for f in iter_py_files():
		file_contents = file_read(f)
		file_contents = func(file_contents, *args, **kwargs)
		file_write(f, file_contents)
		
	git_commit(commit_message)

def fix_margins_all():
	process_all_files(fix_margins, ".setMargin -> .setContentsMargins")

def fix_delta_all():
	process_all_files(fix_delta, ".delta() -> .angleDelta().y()")

def fix_qapp():
	process_all_files(qapp1, "qApp. -> QApplication.")
	process_all_files(qapp2, "qApp -> QApplication")

def fix_imports_pyqt4_to_pyqt5():
	process_all_files(rename_imports_pyqt4_to_pyqt5, "PyQt4 -> PyQt5")

def fix_module_names():
	fix_imports_pyqt4_to_pyqt5()
	
	for m in sorted(list(QTWIDGETS[5]&QTGUI[4])):
		print(m)
		process_all_files(rename_module_usage, m, 'QtWidgets', [m])
		for f in iter_py_files():
			file = File(f)
			file.update_imports()
			file.write(f)
		git_commit("imports")

	for m in sorted(list(QTCORE[5]&QTGUI[4])):
		print(m)
		process_all_files(rename_module_usage, m, 'QtCore', [m])
		for f in iter_py_files():
			file = File(f)
			file.update_imports()
			file.write(f)
		git_commit("update pyqt5 imports")

from collections import defaultdict

def fix_imports():
	sre = re.compile(r'from +(PyQt[4,5]\.\w+) +import +(.*)')

	# for f in iter_py_files_debug():
	for f in iter_py_files():
		file_contents = file_read(f)
		sreee = sre.findall(file_contents)

		imports = defaultdict(list)
		imports_orig = defaultdict(list)
		for sree in sreee:
			src = sree #.group()
			modules = [s.strip() for s in sree[1].split(',')]
			for m in modules:
				parent = sree[0]
				imports_orig[parent].append(m)
				
				if m in PYQT[5]:
					imports[PYQT[5][m]].append(m)
				else:
					imports[parent].append(m)

		if imports_orig != imports:
			repl = '\n'.join(["from {} import {}".format(k, ', '.join(v)) 
							  for k,v in sorted(imports.iteritems())])
			file_contents = re.sub(r'from PyQt[4,5]\..*(\nfrom PyQt[4,5]\..*)+', 'from PyQt.', file_contents)
			file_contents = re.sub(r'from PyQt\..*', repl, file_contents)
			file_write(f, file_contents)
			
	git_commit("imports: PyQt5.Qt*")


fix_margins_all()
fix_qapp()
fix_module_names()
fix_imports()
fix_delta_all()
