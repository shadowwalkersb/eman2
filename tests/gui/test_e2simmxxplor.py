import os

def test_display_initial_gui(qtbot, win, datadir):
    
    root_dir = os.path.join(datadir, "playground")
    args=[
        os.path.join(root_dir, "refine_01", "simmx_01_even.hdf"),
        os.path.join(root_dir, "refine_01", "projections_01_even.hdf"),
        os.path.join(root_dir, "sets", "all__ctf_flip_lp14_even.lst"),
    ]
    
    win = win('e2simmxxplor', args)
    main_form = win.main_form
    qtbot.addWidget(main_form)

    win.cycle(qtbot, main_form)
