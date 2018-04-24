from PyQt4.QtCore import Qt
import os


def test_mouseClick_altModifier(qtbot, win, datadir):
    win = win('e2ctf','%s'%os.path.join(datadir, 'particles', '*.hdf') + " --allparticles --sortdefocus --minptcl=0 --minqual=0 --gui --constbfactor=-1.0 --sf=auto")
    main_form = win.main_form
    qtbot.addWidget(main_form)

    # win.cycle(qtbot, main_form)

