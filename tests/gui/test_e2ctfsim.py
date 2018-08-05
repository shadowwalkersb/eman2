from PyQt5.QtCore import Qt, QPoint
import pyautogui


def test_cli(qtbot, win):
    win = win('e2ctfsim')
    main_form = win.main_form
    qtbot.addWidget(main_form)
    
    win.cycle(qtbot, main_form)
    win.clickButton(qtbot, main_form, main_form.newbut)
    qtbot.keyPress(main_form.setlist, Qt.Key_Down)
    qtbot.keyPress(main_form.setlist, Qt.Key_Alt)
    
    win.cycle(qtbot, main_form.guiim)
    win.clickButton(qtbot, main_form, main_form.guiim)
    qtbot.mouseMove(main_form.guiim, QPoint(0, 0))
    pyautogui.dragRel(10,10, .1)

    win.cycle(qtbot, main_form.guiplot)
    win.clickButton(qtbot, main_form, main_form.guiplot)
    qtbot.mouseMove(main_form.guiplot, QPoint(0, 0))
    pyautogui.click()
    pyautogui.dragRel(10,10, .1)
