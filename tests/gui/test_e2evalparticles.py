from PyQt5.QtCore import Qt
# from PyQt4.QtCore import Qt, QPoint
# import pyautogui


def test_display_initial_gui(qtbot, win):
    win = win('e2evalparticles', ['--gui'])
    main_form = win.main_form
    qtbot.addWidget(main_form)

    win.cycle(qtbot, main_form)
    main_form = main_form.wclasstab
    qtbot.keyPress(main_form.wfilesel, Qt.Key_Down)
    qtbot.keyPress(main_form.wfilesel, Qt.Key_Alt)
    qtbot.wait(500)
    win.clickButton(qtbot, main_form, main_form.wfilesel)
    win.clickButton(qtbot, main_form, main_form.wselallb)
    win.clickButton(qtbot, main_form, main_form.wselnoneb)
