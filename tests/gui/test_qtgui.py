import os
import pytest

from eman2_gui import em3Dfonts
from eman2_gui import emboxerbase 
from eman2_gui import embrowse 
from eman2_gui import embrowser 
from eman2_gui import emfoldhunterstat 
from eman2_gui import emform 
from eman2_gui import emimage3dslice 
from eman2_gui import emlights 


@pytest.mark.qt_no_exception_capture
def test_em3Dfonts():
    em3Dfonts.main()

def test_emboxerbase(datadir):
    emboxerbase.main([os.path.join(datadir, 'e2boxer', 'test_box.hdf')])

def test_embrowse():
    embrowse.main()

@pytest.mark.skip(reason="Gets stuck")
@pytest.mark.qt_no_exception_capture
def test_embrowser():
    embrowser.main()

def test_emfoldhunterstat():
    emfoldhunterstat.main()

def test_emform():
    emform.main()

def test_emimage3dslice():
    emimage3dslice.main([''])

def test_emlights():
    emlights.main()
