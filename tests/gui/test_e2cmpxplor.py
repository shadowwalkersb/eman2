import os

module_name = 'e2cmpxplor'


def test_display_initial_gui(qtbot, win, datadir):
    args=[
        os.path.join(datadir, "e2cmpxplor", "projections_02_odd.hdf"),
        os.path.join(datadir, "e2cmpxplor", "BGal_000232.hdf"),
    ]
    win = win(module_name, args[0], args[1])
    main_form = win.main_form
    qtbot.addWidget(main_form)

    win.cycle(qtbot, main_form)

def test_display_data(qtbot, win, datadir):
    root_dir = os.path.join(datadir, "playground")
    args=[
        os.path.join(root_dir, "refine_01", "projections_01_even.hdf"),
        os.path.join(root_dir, "particles", "BGal_000232__ctf_flip_lp14.hdf"),
    ]
    
    win = win(module_name, args[0], args[1])
    main_form = win.main_form
    qtbot.addWidget(main_form)

    win.cycle(qtbot, main_form)
