import os
import glob
from PyQt4.QtCore import Qt
import eman2_gui
import inspect
import runpy
import pytest

from eman2_gui import em3Dfonts
from eman2_gui import emanimationutil
from eman2_gui import emapplication 
from eman2_gui import emboxerbase 
from eman2_gui import embrowse 
from eman2_gui import embrowser 
from eman2_gui import emdataitem3d 
from eman2_gui import emdatastorage 
from eman2_gui import emfoldhunterstat 
from eman2_gui import emform 
from eman2_gui import emglobjects 
from eman2_gui import emhist 
from eman2_gui import emimage 
from eman2_gui import emimage2d 
from eman2_gui import emimage3d 
from eman2_gui import emimage3diso 
from eman2_gui import emimage3dslice 
from eman2_gui import emimage3dsym 
from eman2_gui import emimage3dvol 
from eman2_gui import emimagemx 
from eman2_gui import emimageutil 
from eman2_gui import emitem3d 
from eman2_gui import emlights 
from eman2_gui import empdbitem3d 
from eman2_gui import empdbvaltool 
from eman2_gui import empdbviewer 
from eman2_gui import emplot2d 
from eman2_gui import emplot3d 
from eman2_gui import empmtabwidgets 
from eman2_gui import empmwidgets 
from eman2_gui import emrctboxergui 
from eman2_gui import emrctstrategy 
from eman2_gui import emsave 
from eman2_gui import emscene3d 
from eman2_gui import emselector 
from eman2_gui import emshape 
from eman2_gui import emshapeitem3d 
from eman2_gui import emsprworkflow 
from eman2_gui import emtprworkflow


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

@pytest.mark.qt_no_exception_capture
def test_emplot2d():
    emplot2d.main([''])

def test_emplot3d():
    emplot3d.main([''])

def test_emscene3d():
    emscene3d.main()

@pytest.mark.skip(reason="Needs user response")
def test_emselector():
    emselector.main()

def test_emsprworkflow():
    emsprworkflow.main()

def test_emimage2d():
    emimage2d.main([''])

@pytest.mark.qt_no_exception_capture
def test_emimage3d():
    emimage3d.main([''])

@pytest.mark.skip(reason="Broken, segfault")
def test_emimage3diso():
    emimage3diso.main()

@pytest.mark.skip(reason="Needs user response")
@pytest.mark.qt_no_exception_capture
def test_emimage3dsym():
    emimage3dsym.main()

def test_emimage3dvol():
    emimage3dvol.main([''])

def test_emimagemx():
    emimagemx.main([''])

@pytest.mark.skip(reason="Broken, ???")
def test_empdbitem3d():
    empdbitem3d.main()

@pytest.mark.skip(reason="Needs input files")
def test_empdbvaltool():
    empdbvaltool.main()

@pytest.mark.qt_no_exception_capture
def test_empdbviewer():
    empdbviewer.main()

# no main()
# def test_emanimationutil():
#     emanimationutil.main()

# no main()
# def test_emapplication():
#     emapplication.main()

# no main()
# def test_emdataitem3d():
#     emdataitem3d.main()

# no main()
# def test_emdatastorage():
#     emdatastorage.main()

# no main()
# def test_emglobjects():
#     emglobjects.main()

# no main()
# def test_emhist():
#     emhist.main()

# no main()
# def test_emimage():
#     emimage.main()

# no main()
# def test_emimageutil():
#     emimageutil.main()

# no main()
# def test_empmtabwidgets():
#     empmtabwidgets.main()

# no main()
# def test_empmwidgets():
#     empmwidgets.main()

# no main()
# def test_emrctboxergui():
#     emrctboxergui.main()

# no main()
# def test_emrctstrategy():
#     emrctstrategy.main()

# no main()
# def test_emsave():
#     emsave.main()

# no main()
# def test_emshape():
#     emshape.main()

# no main()
# def test_emshapeitem3d():
#     emshapeitem3d.main()

# no main()
# def test_emtprworkflow():
#     emtprworkflow.main()

# no gui
# def test_emitem3d():
#     emitem3d.main()
