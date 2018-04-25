from PyQt4.QtCore import Qt
import os


def test_display_initial_gui(qtbot, win, datadir):
    win = win('e2helixboxer', [os.path.join(datadir, 'e2boxer', 'test_box.hdf'), "--gui"])
    main_form = win.main_form
    
    win.cycle(qtbot, main_form.main_image)
    qtbot.mouseClick(main_form.main_image, Qt.LeftButton)

    # main_window = main_window('e2helixboxer', [os.path.join(datadir, 'e2boxer', 'test_box.hdf'), "--gui"])
    # snap = snap('e2helixboxer')
    # snap(main_window)
    # snap(main_window.main_image)
