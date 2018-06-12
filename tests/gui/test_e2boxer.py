import os
from PyQt4.QtCore import Qt


def test_cli(qtbot, win, datadir):
    win = win('e2boxer', [os.path.join(datadir, 'e2boxer', 'test_box.hdf'), "--gui", "--apix=1", "--box=32"])
    main_form = win.main_form
    qtbot.addWidget(main_form)
    
    win.cycle(qtbot, main_form)
    win.clickButton(qtbot, main_form, main_form.bautobox)
    win.clickButton(qtbot, main_form, main_form.bautoboxa)
    win.cycle(qtbot, main_form.wimage, Qt.LeftButton)
    win.cycle(qtbot, main_form.wparticles)
