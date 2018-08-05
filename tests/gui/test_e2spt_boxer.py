import os
from PyQt5.QtCore import Qt, QPoint
import pyautogui


def test_display_initial_gui(qtbot, win, datadir):
    win = win('e2spt_boxer', [os.path.join(datadir, "e2spt_boxer", "00bin32.hdf")])
    main_form = win.main_form

    win.cycle(qtbot, main_form)
    # qtbot.wait(1000)
    # qtbot.keyPress(main_form, Qt.Key_Alt)
    # qtbot.wait(1000)
    # qtbot.keyPress(main_form, Qt.Key_Shift, delay=1)
    # qtbot.wait(1000)
    # qtbot.keyPress(main_form, Qt.Key_Control, delay=1)
    # qtbot.wait(100)
    pyautogui.press('alt')
    qtbot.wait(100)
    # pyautogui.press('shift')
    qtbot.mouseClick(main_form, Qt.LeftButton)
    qtbot.mouseMove(main_form, QPoint(0, 0))
    # qtbot.mousePress(main_form.main_image, Qt.LeftButton, pos=QPoint(0, 0))
    pyautogui.click()
    pyautogui.dragRel(100,100, .1)
    qtbot.wait(300)

    win.cycle(qtbot, main_form.boxesviewer)

    qtbot.mouseMove(main_form.xyview, QPoint(10, 10))
    pyautogui.click()
    pyautogui.dragRel(10,10, .1)
    qtbot.wait(300)

    qtbot.mouseMove(main_form.xzview, QPoint(10, 10))
    pyautogui.click()
    pyautogui.dragRel(10,10, .1)
    qtbot.wait(300)

    qtbot.mouseMove(main_form.zyview, QPoint(10, 10))
    pyautogui.click()
    pyautogui.dragRel(10,10, .1)
    qtbot.wait(300)

    win.clickButton(qtbot, main_form, main_form.wlocalbox)
    # # qtbot.keyPress(main_form.boxesviewer, Qt.Key_Alt)
    # 
    win.cycle(qtbot, main_form.optionviewer)
    # # qtbot.keyPress(main_form.optionviewer, Qt.Key_Alt)
