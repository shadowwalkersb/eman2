# from PyQt4.QtCore import Qt


def test_display_initial_gui(qtbot, win):
    win = win('e2projectmanager')
    main_form = win.main_form

    win.cycle(qtbot, main_form)
    ws = main_form.tree_widgets
    for w in ws:
        print(w)
        # qtbot.mouseClick(w)
        main_form._tree_widget_click(w, 0)
        qtbot.wait(400)
    # qtbot.mouseClick(main_form.main_image, Qt.LeftButton)
