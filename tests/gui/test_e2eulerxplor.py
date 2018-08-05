from PyQt5.QtCore import Qt
import pytest
from PyQt5.QtCore import Qt, QPoint
import pyautogui


@pytest.mark.qt_no_exception_capture
def test_cli(qtbot, win):
    win = win('e2eulerxplor')
    main_form = win.main_form
    qtbot.addWidget(main_form)
    
    win.cycle(qtbot, main_form)
    # main_form = main_form.model
    # pyautogui.click()

    # qtbot.keyPress(main_form, Qt.Key_Down)
    # qtbot.keyPress(main_form, Qt.Key_Alt)

    # qtbot.mouseMove(main_form, QPoint(0, 0))
    # pyautogui.click()
    # pyautogui.dragRel(10,10, .1)

    # win.cycle(qtbot, main_form.guiplot)
    # win.clickButton(qtbot, main_form, main_form.guiplot)
    # qtbot.mouseMove(main_form.guiplot, QPoint(0, 0))
    # pyautogui.click()
    # pyautogui.dragRel(10,10, .1)
