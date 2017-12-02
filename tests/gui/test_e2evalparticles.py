def test_display_initial_gui(qtbot, win):
    win = win('e2evalparticles', ['--gui'])
    main_form = win.main_form
    qtbot.addWidget(main_form)

    win.cycle(qtbot, main_form)
