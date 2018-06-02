from PyQt4.QtCore import Qt


def test_cli(qtbot, win):
    win = win('e2ctfsim')
    main_form = win.main_form
    qtbot.addWidget(main_form)
    
    win.cycle(qtbot, main_form)
    win.clickButton(qtbot, main_form, main_form.newbut)
    qtbot.keyPress(main_form.setlist, Qt.Key_Down)
    qtbot.keyPress(main_form.setlist, Qt.Key_Alt)
    
    win.cycle(qtbot, main_form.guiim)
    win.cycle(qtbot, main_form.guiplot)
