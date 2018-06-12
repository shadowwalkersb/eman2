from PyQt4.QtCore import Qt
import os
import glob
import sys


def test_mouseClick_altModifier(qtbot, win, datadir):
    root_dir = os.path.join(datadir, "playground")
    args = glob.glob('%s'%os.path.join(root_dir, 'particles', '*.hdf'))
    args.extend(["--allparticles", "--sortdefocus", "--minptcl=0", "--minqual=0", "--constbfactor=-1.0", "--gui", "--sf=auto"])

    win = win('e2ctf', args)
    main_form = win.main_form
    qtbot.addWidget(main_form)

    win.cycle(qtbot, main_form)
    win.cycle(qtbot, main_form.guiim)
    win.cycle(qtbot, main_form.guiplot)
    win.cycle(qtbot, main_form.guirealim)

