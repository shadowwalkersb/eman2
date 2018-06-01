import os


def test_display_initial_gui(qtbot, win, datadir):
    win = win('e2spt_wedge', [os.path.join(datadir, "e2spt_wedge", "00bin16.hdf")])
    main_form = win.main_form

    win.cycle(qtbot, main_form)
