# import os
# import glob
from PyQt4.QtCore import Qt, QPoint
from PyQt4 import QtGui
# import eman2_gui
# # from eman2_gui import emlights
# import inspect
# import runpy

from OpenGL.GL import GL_LIGHT1
from eman2_gui import valslider
import pyautogui


def widget_show(qtbot, widget):
    widget.show()
    widget.raise_()
    widget.activateWindow()
    # if clickButton:
    #     qtbot.mouseClick(form, clickButton)
    qtbot.mouseClick(widget, Qt.LeftButton)
    qtbot.waitForWindowShown(widget)
    qtbot.wait(300)

def test_ValSlider(qtbot):
    # parent = QtGui.QWidget()
    # widget = valslider.ValSlider(parent,(1.0,5.0),"GLShd:")
    # valsl = valslider.ValSlider(rng=[1,10], label="some label", showenable=0)
    # widget_show(qtbot, valsl)
    # qtbot.mouseClick(valsl.enablebox, Qt.LeftButton)
    # qtbot.mouseClick(valsl.slider, Qt.LeftButton)
    # qtbot.wait(500)

    classes = [
        valslider.ValSlider(rng=[1,10], label="some label", showenable=0),
        valslider.ValBox(rng=[1,10], label="some label", showenable=0),
        valslider.StringBox(label="some label", showenable=0),
        valslider.CheckBox(label="some label", showenable=0),
        valslider.RangeSlider(),
        valslider.EMSpinWidget(5,.2),
        valslider.EMLightControls(GL_LIGHT1),
        valslider.EMQTColorWidget(),
        # valslider.CameraControls(),
        valslider.EMANToolButton(),
    ]
    
    for cl in classes:
        widget_show(qtbot, cl)
        try:
            if hasattr(cl, 'text'):
                cl.text.clear()
                
                qtbot.keyClicks(cl.text, '3.0')
                qtbot.mouseMove(cl.text, QPoint(0, 0))
                pyautogui.click()
                qtbot.mouseClick(cl.hboxlayout, Qt.LeftButton)
                qtbot.wait(200)
        except:
            pass
        if hasattr(cl, 'enablebox'):
            cl.enablebox.setFocus()
            qtbot.mouseClick(cl.enablebox, Qt.LeftButton)
        if hasattr(cl, 'lbutton'):
            qtbot.mouseClick(cl.lbutton, Qt.LeftButton)
        if hasattr(cl, 'rbutton'):
            qtbot.mouseClick(cl.rbutton, Qt.LeftButton)
        if hasattr(cl, 'numbox'):
            cl.numbox.clear()
            qtbot.keyClicks(cl.numbox, '3')
        # if hasattr(cl, 'color'):
        if hasattr(cl, 'slider'):
            qtbot.mouseClick(cl.slider, Qt.LeftButton)
        # qtbot.mouseClick(cl, Qt.LeftButton)
        # qtbot.wait(200)
        # pyautogui.click()
        # qtbot.wait(200)
        qtbot.mouseMove(cl, QPoint(0, 0))
        pyautogui.dragRel(10,10, .1)
        # qtbot.mousePress(cl, Qt.LeftButton)
        # qtbot.mouseMove(cl, QPoint(100,100))
        # qtbot.mouseRelease(cl, Qt.LeftButton)
        qtbot.wait(300)

    # qtbot.wait(2000)

    # widget_show(qtbot, widg1)
    # widget.raise_()
    # widget.activateWindow()
    # # if clickButton:
    # #     qtbot.mouseClick(form, clickButton)
    # qtbot.mouseClick(widget, Qt.LeftButton)
    # qtbot.waitForWindowShown(widget)
    # qtbot.wait(2000)
    # glcontrast = ValSlider(gltab,(1.0,5.0),"GLShd:")
    # widget.show()
