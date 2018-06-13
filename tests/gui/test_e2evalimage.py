import os
from PyQt4.QtCore import Qt, QPoint
import pyautogui


def test_display_file(qtbot, win, datadir):
    win = win('e2evalimage',[os.path.join(datadir, 'e2evalimage', 'BGal_000232.hdf')])
    main_form = win.main_form
    qtbot.addWidget(main_form)
    
    win.cycle(qtbot, main_form)
    qtbot.keyPress(main_form.setlist, Qt.Key_Down)
    qtbot.keyPress(main_form.setlist, Qt.Key_Alt)
    # win.clickButton(qtbot, main_form, main_form.brefit)

    win.cycle(qtbot, main_form.wplot)
    win.clickButton(qtbot, main_form, main_form.wplot)
    qtbot.mouseMove(main_form.wplot, QPoint(0, 0))
    pyautogui.click()
    pyautogui.dragRel(10,10, .1)

    win.cycle(qtbot, main_form.wfft)
    win.clickButton(qtbot, main_form, main_form.wfft)
    qtbot.mouseMove(main_form.wfft, QPoint(0, 0))
    pyautogui.click()
    pyautogui.dragRel(10,10, .1)

    win.cycle(qtbot, main_form.wimage)
    win.clickButton(qtbot, main_form, main_form.wimage)
    qtbot.mouseMove(main_form.wimage, QPoint(0, 0))
    pyautogui.click()
    pyautogui.dragRel(10,10, .1)

    win.clickButton(qtbot, main_form, main_form.brefit)
