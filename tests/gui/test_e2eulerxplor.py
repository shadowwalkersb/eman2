from PyQt4.QtCore import Qt
import pytest


@pytest.mark.qt_no_exception_capture
def test_cli(qtbot, win):
    win = win('e2eulerxplor')
    main_form = win.main_form
    qtbot.addWidget(main_form)
    
    win.cycle(qtbot, main_form)
