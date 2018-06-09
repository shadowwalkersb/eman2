import os
from PyQt4.QtCore import Qt, QPoint
import pytest
import pyautogui


@pytest.mark.xfail
def test_cli(qtbot, win, datadir):
    win = win('e2tiltvalidate', ["--path=%s" % os.path.join(datadir, 'e2tiltvalidate', 'TiltValidate_04'), '--gui'])
    
    main_form = win.main_form
    qtbot.addWidget(main_form)
    
    win.cycle(qtbot, main_form)
    
    plot = main_form.polarplot
    # qtbot.mouseMove(plot, QPoint(20, 20))
    # qtbot.mouseClick(plot, Qt.LeftButton)
    # pyautogui.click()
    # qtbot.wait(1000)
    qtbot.mouseMove(plot, QPoint(0, 0))
    # qtbot.wait(1000)
    # qtbot.mouseRelease(plot, Qt.LeftButton, delay=100)
    pyautogui.dragRel(100,100, .1)
    qtbot.wait(1000)
