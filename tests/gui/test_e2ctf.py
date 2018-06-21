from PyQt4.QtCore import Qt
import os
import glob
import sys
from PyQt4.QtCore import Qt, QPoint
# from PyQt4 import QtGui
import pyautogui


def test_mouseClick_altModifier(qtbot, win, datadir):
    root_dir = os.path.join(datadir, "playground")
    args = glob.glob('%s'%os.path.join(root_dir, 'particles', '*.hdf'))
    args.extend(["--allparticles", "--sortdefocus", "--minptcl=0", "--minqual=0", "--constbfactor=-1.0", "--gui", "--sf=auto"])

    win = win('e2ctf', args)
    main_form = win.main_form
    qtbot.addWidget(main_form)

    win.cycle(qtbot, main_form)
    win.clickButton(qtbot, main_form, main_form.setlist)
    qtbot.keyPress(main_form.setlist, Qt.Key_Down)
    qtbot.keyPress(main_form.setlist, Qt.Key_Alt)

    win.clickButton(qtbot, main_form, main_form.refit)
    win.clickButton(qtbot, main_form, main_form.saveparms)
    win.clickButton(qtbot, main_form, main_form.recallparms)
    
    win.cycle(qtbot, main_form.guiim)
    win.clickButton(qtbot, main_form, main_form.guiim)
    qtbot.mouseMove(main_form.guiim, QPoint(0, 0))
    pyautogui.dragRel(10,10, .1)

    win.cycle(qtbot, main_form.guiplot)
    win.clickButton(qtbot, main_form, main_form.guiplot)
    qtbot.mouseMove(main_form.guiplot, QPoint(0, 0))
    pyautogui.click()
    pyautogui.dragRel(10,10, .1)

    win.cycle(qtbot, main_form.guirealim)
    qtbot.keyPress(main_form.guirealim, Qt.Key_I)

    win.cycle(qtbot, main_form)
    win.clickButton(qtbot, main_form, main_form.show2dfit)
    qtbot.mouseClick(main_form.show2dfit, Qt.LeftButton)
    qtbot.mouseMove(main_form.show2dfit, QPoint(0, 0))
    pyautogui.click()

    win.clickButton(qtbot, main_form, main_form.showzerorings)
    win.clickButton(qtbot, main_form, main_form.usephaseplate)