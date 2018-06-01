import os
from PyQt4.QtCore import Qt
import pytest


@pytest.mark.xfail
def test_cli(qtbot, win, datadir):
    win = win('e2tiltvalidate', ["--path=%s" % os.path.join(datadir, 'e2tiltvalidate', 'TiltValidate_04'), '--gui'])
    
    main_form = win.main_form
    qtbot.addWidget(main_form)
    
    win.cycle(qtbot, main_form)
