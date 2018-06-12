import os
from PyQt4.QtCore import Qt
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
    
    win.cycle(qtbot, main_form.boxesviewer)
    # # qtbot.keyPress(main_form.boxesviewer, Qt.Key_Alt)
    # 
    win.cycle(qtbot, main_form.optionviewer)
    # # qtbot.keyPress(main_form.optionviewer, Qt.Key_Alt)

