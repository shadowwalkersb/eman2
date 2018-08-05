from PyQt5.QtCore import Qt, QPoint
import os
import pyautogui


def test_display_initial_gui(qtbot, win, datadir):
    win = win('e2helixboxer', [os.path.join(datadir, 'e2boxer', 'test_box.hdf'), "--gui"])
    main_form = win.main_form
    
    win.cycle(qtbot, main_form.main_image)
    qtbot.mouseClick(main_form.main_image, Qt.LeftButton)

    qtbot.mouseMove(main_form.main_image, QPoint(10, 10))
    # qtbot.mousePress(main_form.main_image, Qt.LeftButton, pos=QPoint(0, 0))
    pyautogui.click()
    pyautogui.dragRel(100,100, .1)
    qtbot.wait(300)

    # main_window = main_window('e2helixboxer', [os.path.join(datadir, 'e2boxer', 'test_box.hdf'), "--gui"])
    # snap = snap('e2helixboxer')
    # snap(main_window)
    # snap(main_window.main_image)
