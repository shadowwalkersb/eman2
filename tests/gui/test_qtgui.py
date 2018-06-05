import os
import pytest

from eman2_gui import em3Dfonts
from eman2_gui import emboxerbase 
from eman2_gui import emlights 


@pytest.mark.qt_no_exception_capture
def test_em3Dfonts():
    em3Dfonts.main()

def test_emboxerbase(datadir):
    emboxerbase.main([os.path.join(datadir, 'e2boxer', 'test_box.hdf')])

def test_emlights():
    emlights.main()
