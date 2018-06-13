from PyQt4.QtCore import Qt, QPoint
import os
import pyautogui


def test_display_initial_gui(qtbot, win, datadir):
    args=[
        os.path.join(datadir, "e2RCTboxer", "00.hdf"),
        os.path.join(datadir, "e2RCTboxer", "10.hdf"),
        "--boxsize=64",
    ]
    
    win = win('e2RCTboxer', args)
    main_form = win.main_form

    win.cycle(qtbot, main_form.control_window)
    qtbot.keyPress(main_form.control_window, Qt.Key_Alt)

    win.cycle(qtbot, main_form.untilt_win.window, Qt.LeftButton)
    qtbot.keyPress(main_form.untilt_win.window, Qt.Key_Alt)
    win.clickButton(qtbot, main_form, main_form.untilt_win.window)
    qtbot.mouseMove(main_form.untilt_win.window, QPoint(0, 0))
    pyautogui.click()
    pyautogui.dragRel(10,10, .1)
    qtbot.wait(300)
    
    win.cycle(qtbot, main_form.tilt_win.window, Qt.LeftButton)
    win.clickButton(qtbot, main_form, main_form.tilt_win.window)
    qtbot.mouseMove(main_form.tilt_win.window, QPoint(0, 0))
    pyautogui.click()
    pyautogui.dragRel(10,10, .1)
    qtbot.wait(300)

    win.cycle(qtbot, main_form.particles_window.window)
    
    # main_window = main_window('e2RCTboxer', args)
    # snap = snap('e2RCTboxer')
    # snap(main_window.control_window)
    # snap(main_window.untilt_win.window, Qt.LeftButton)
    # snap(main_window.tilt_win.window, Qt.LeftButton)
    # snap(main_window.particles_window.window)
