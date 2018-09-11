import pytest
from PyQt4.QtGui import QPixmap
import os


def pytest_configure(config):
    import EMAN2
    EMAN2._called_from_test = True

def pytest_unconfigure(config):
    import EMAN2
    del EMAN2._called_from_test

@pytest.fixture
def curdir(request):
    return request.fspath.dirname

def get_main_form(module_name, sys_argv=None):
    module = __import__(module_name)
    if not os.path.isdir(module_name):
        os.mkdir(module_name)
    main_form = module.main(sys_argv)
    return main_form

@pytest.fixture
def main_form():
    # main_form = common.get_main_form()
    return get_main_form
    # main_form.close()

class Win(object):
    def __init__(self, module_name, sys_argv=[]):
        self.counter = 0
        self.dir = module_name
        self.main_form = get_main_form(module_name, sys_argv)
    
    def cycle(self, qtbot, form, clickButton=None):
        form.raise_()
        form.activateWindow()
        if clickButton:
            qtbot.mouseClick(form, clickButton)
        qtbot.waitForWindowShown(form)
        qtbot.wait(100)
        fname = '%s.png'%os.path.join(self.dir,str(self.counter))
        qpxmap = QPixmap.grabWindow(form.winId())
        qtbot.wait(100)
        qpxmap.save(fname,'png')
        print("Click!: %s"%fname)
        qtbot.wait(100)
        self.counter += 1

@pytest.fixture
def win():
    return Win
