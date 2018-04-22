import os

def test_display_initial_gui(qtbot, win, datadir):
    datafile = os.path.join(datadir, "e2spt_boxer", "00bin32.hdf")
    options = type('', (), {})
    options.apix = 0.0
    options.invert = False
    options.inmemory = False

    win = win('e2spt_boxer', options, datafile)
    main_form = win.main_form

    win.cycle(qtbot, main_form)
    win.cycle(qtbot, main_form.boxesviewer)
    win.cycle(qtbot, main_form.optionviewer)
