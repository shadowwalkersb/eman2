from PyQt4.QtCore import Qt


def test_cli(qtbot, win):
    win = win('e2eulerxplor')
    main_form = win.main_form
    qtbot.addWidget(main_form)
    
    win.cycle(qtbot, main_form)
