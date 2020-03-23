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
	process_all_files(qapp21, "QtGui.QApplication -> QtWidgets.QApplication")

def fix_qweb():
	process_all_files(qweb, "QtWebKit -> QtWebEngineWidgets")

def fix_imports_pyqt4_to_pyqt5():
	process_all_files(rename_imports_pyqt4_to_pyqt5, "PyQt4 -> PyQt5")

def fix_module_names():
	# fix_imports_pyqt4_to_pyqt5()
	
	for m in sorted(list(QTWIDGETS[5]&QTGUI[4])):
		print(m)
		process_all_files(rename_module_usage, m, 'QtWidgets', [m])
		# update_imports()

	for m in sorted(list(QTCORE[5]&QTGUI[4])):
		print(m)
		process_all_files(rename_module_usage, m, 'QtCore', [m])
		# update_imports()


def update_imports():
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
							  for k,v in sorted(imports.items())])
			file_contents = re.sub(r'from PyQt[4,5]\..*(\nfrom PyQt[4,5]\..*)+', 'from PyQt.', file_contents)
			file_contents = re.sub(r'from PyQt\..*', repl, file_contents)
			file_write(f, file_contents)
			
	git_commit("imports: PyQt5.Qt*")

def fix_qfile_dialog():
	# for f in iter_py_files_debug():
	for f in iter_py_files():
		file = File(f)
		file.fix_qfile_dialog()
		file.writelines(f)
		# file_write(f, file_contents)
				
	git_commit("getOpenFileName, getSaveFileName")

def fix_old_div(func, op_sym, commit_message):
	# for f in iter_py_files_debug():
	for f in iter_py_files():
		file = File(f)
		file.fix_old_div(func, op_sym)
		file.writelines(f)
		# file_write(f, file_contents)
				
	git_commit(commit_message)

def count_old_div():
	search_str = "old_div"
	# for f in iter_py_files_debug():
	for f in iter_py_files():
		file = File(f)
		count = file.file_context.count(search_str)
		if count == 1:
			print("{}: {}".format(f, count))
			matches = [(i,k) for i,k in enumerate(file.lines) if search_str in k]
			for i,k in matches:
				if "from" in k:
					print("   {}: {}".format(i, k))
					del file.lines[i]
		file.writelines(f)

	git_commit("cleanup unused imports old_div")

# fix_module_names()
# update_imports()
# fix_imports_pyqt4_to_pyqt5()
# fix_imports()
# fix_qapp()
# fix_margins_all()
# fix_delta_all()
# fix_qfile_dialog()
# fix_qweb()

def op_bool_any(args):
	return any(is_bin_op_float(arg) for arg in args)

def op_bool_all(args):
	return all(is_bin_op_int(arg) for arg in args)

from functools import partial


func_list_and_commit_messages = [[
	# [is_num_float,   	"float literal"],
	# [is_func_float,  	"float func"],
	# [is_math_const,  	"math const"],
	# [is_np_const,    	"np const"],
	# [is_math_func,   	"math func"],
	# [is_np_func,     	"np func"],
	# [is_bin_op_float,  	"recursive float"],
	],
	[
	[is_num_int,     	"int literal"],
	[is_func_int,    	"int func"],
	[is_func_len,    	"len func"],
	[is_func_size,    	"size func"],
	[is_const_size,    	"size const"],
	# [is_bin_op_int,  	"recursive int"],
	]
]

for f_m in func_list_and_commit_messages[0]:
	funcs_float.append(f_m[0])
	fix_old_div(op_bool_any, '/', f_m[1])
	
	count_old_div()

for f_m in func_list_and_commit_messages[1]:
	funcs_int.append(f_m[0])
	fix_old_div(op_bool_all, '//', f_m[1])

	count_old_div()
