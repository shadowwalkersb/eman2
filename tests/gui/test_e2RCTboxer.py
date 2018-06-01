from PyQt4.QtCore import Qt
import os


def test_display_initial_gui(qtbot, win, datadir):
    args=[
        os.path.join(datadir, "e2RCTboxer", "00.hdf"),
        os.path.join(datadir, "e2RCTboxer", "10.hdf"),
        "--boxsize=256",
    ]
    
    win = win('e2RCTboxer', args)
    main_form = win.main_form

    win.cycle(qtbot, main_form.control_window)
    win.cycle(qtbot, main_form.untilt_win.window, Qt.LeftButton)
    win.cycle(qtbot, main_form.tilt_win.window, Qt.LeftButton)
    win.cycle(qtbot, main_form.particles_window.window)
    
    # main_window = main_window('e2RCTboxer', args)
    # snap = snap('e2RCTboxer')
    # snap(main_window.control_window)
    # snap(main_window.untilt_win.window, Qt.LeftButton)
    # snap(main_window.tilt_win.window, Qt.LeftButton)
    # snap(main_window.particles_window.window)
