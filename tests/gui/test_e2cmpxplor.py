import os


def test_display_initial_gui(qtbot, win, datadir):
    args=[
        os.path.join(datadir, "e2cmpxplor", "projections_02_odd.hdf"),
        os.path.join(datadir, "e2cmpxplor", "BGal_000232.hdf"),
    ]
    win = win('e2cmpxplor', args[0], args[1])
    main_form = win.main_form
    qtbot.addWidget(main_form)

    win.cycle(qtbot, main_form)
