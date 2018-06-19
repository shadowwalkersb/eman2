import os
import glob
from PyQt4.QtCore import Qt
import eman2_gui
import inspect
import pytest

modules = [
    'em3Dfonts',
    'emanimationutil',
    'emapplication', 
    'emboxerbase', 
    'embrowse', 
    'embrowser', 
    'emdataitem3d', 
    'emdatastorage', 
    'emfoldhunterstat', 
    'emform', 
    'emglobjects', 
    'emhist', 
    'emimage', 
    'emimage2d', 
    'emimage3d', 
    'emimage3diso', 
    'emimage3dmorph', 
    'emimage3dslice', 
    'emimage3dsym', 
    'emimage3dvol', 
    'emimagemx', 
    'emimageutil', 
    'emitem3d', 
    'emlights', 
    'empdbitem3d', 
    'empdbvaltool', 
    'empdbviewer', 
    'emplot2d', 
    'emplot3d', 
    'empmtabwidgets', 
    'empmwidgets', 
    'emrctboxergui', 
    'emrctstrategy', 
    'emsave', 
    'emscene3d', 
    'emselector', 
    'emshape', 
    'emshapeitem3d', 
    'emsprworkflow', 
    'emtprworkflow',
]


def test_modules():
    for module in modules:
        obj = __import__('eman2_gui.' + module)
        obj.main()
