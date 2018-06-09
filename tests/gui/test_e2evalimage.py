import os
from PyQt4.QtCore import Qt


def test_display_file(qtbot, win, datadir):
    win = win('e2evalimage',[os.path.join(datadir, 'e2evalimage', 'BGal_000232.hdf')])
    main_form = win.main_form
    qtbot.addWidget(main_form)
    
    win.cycle(qtbot, main_form)
    qtbot.keyPress(main_form.setlist, Qt.Key_Down)
    qtbot.keyPress(main_form.setlist, Qt.Key_Alt)

    win.cycle(qtbot, main_form.wplot)
    win.cycle(qtbot, main_form.wfft)
    win.cycle(qtbot, main_form.wimage)
