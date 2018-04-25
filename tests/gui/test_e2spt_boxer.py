import os

def test_display_initial_gui(qtbot, win, datadir):
    win = win('e2spt_boxer', [os.path.join(datadir, "e2spt_boxer", "00bin32.hdf")])
    main_form = win.main_form

    win.cycle(qtbot, main_form)
    win.cycle(qtbot, main_form.boxesviewer)
    win.cycle(qtbot, main_form.optionviewer)
