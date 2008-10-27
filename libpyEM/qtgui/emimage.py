#!/usr/bin/env python

#
# Author: Steven Ludtke, 04/10/2003 (sludtke@bcm.edu)
# Copyright (c) 2000-2006 Baylor College of Medicine
#
# This software is issued under a joint BSD/GNU license. You may use the
# source code in this file under either license. However, note that the
# complete EMAN2 and SPARX software packages have some GPL dependencies,
# so you are responsible for compliance with the licenses of these packages
# if you opt to use BSD licensing. The warranty disclaimer below holds
# in either instance.
#
# This complete copyright notice must be included in any revised version of the
# source code. Additional authorship citations may be added, but existing
# author citations must be preserved.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston MA 02111-1307 USA
#
#

from PyQt4 import QtCore, QtGui, QtOpenGL
from PyQt4.QtCore import Qt
from emimage2d import *
from emimagemx import *
from emplot2d import *
#from emimagemxrotor import *
from emimage3d import *
from emimageutil import EMParentWin
from OpenGL import GL,GLU,GLUT
from sys import argv
from copy import deepcopy
#from valslider import ValSlider
#from math import *
#from EMAN2 import *
#import sys
#import numpy



GLUT.glutInit(sys.argv )


def image_update():
	for i in EMImage2DModule.allim.keys():
		try:
			if i.data.get_changecount() !=i.get_last_render_image_display_count() :
				i.force_display_update()
				i.force_fft_redo()
				i.updateGL()
		except: pass
	
	for i in EMImageMXModule.allim.keys():
		try:
			if i.data[0].get_changecount()!=i.get_last_render_image_display_count() :
				i.force_display_update()
				i.updateGL()
		except: pass
		
	for i in EMImage3DModule.allim.keys():
		try:
			if i.data.get_changecount()!=i.get_last_render_image_display_count() :
				i.updateGL()
		except: pass
	
	
def get_app():
	app=QtGui.QApplication.instance()
	if not app : app = QtGui.QApplication([])
	
	try: 
		if app.updtimer : pass
	except:
		tmr=QtCore.QTimer()
		tmr.setInterval(250)
		tmr.connect(tmr,QtCore.SIGNAL("timeout()"), image_update)
		tmr.start()
	
		app.updtimer=tmr

	return app
		
#def imageupdate():
	#for i in EMImage2DModule.allim.keys():
		#try:
			#if i.data.get_attr("changecount")!=i.get_last_render_image_display_count() :
				#i.force_display_update()
				#i.updateGL()
		#except: pass

	#for i in EMImage3DWidget.allim.keys():
		#try:
			#if i.data.get_attr("changecount")!=i.changec :
				#i.set_data(i.data)
		#except: pass
		
	#for i in EMImageMXWidget.allim.keys():
		#try:
			#if len(i.data)!=i.nimg : i.set_data(i.data)
		#except:
			#pass
		#upd=0
		#try:
			#for j in i.changec.keys():
				#try:
					#if j.get_attr("changecount")!=i.changec[j] :
						#upd=1
						#break
				#except: pass
		#except: pass
		#if upd : i.set_data(i.data)

class EMImageModule(object):
	"""This is basically a factory class that will return an instance of the appropriate EMImage* class """
	def __new__(cls,data=None,old=None,app=None):
		"""This will create a new EMImage* object depending on the type of 'data'. If
		old= is provided, and of the appropriate type, it will be used rather than creating
		a new instance.
		FIXME "old" aspect un tested
		"""
		if isinstance(data,EMData) and data.get_zsize()==1:
			if old:
				if isinstance(old,EMImage2DModule) :
					old.set_data(data)
					return old
			module = EMImage2DModule(application=app)
			module.set_data(data)
			return module
		elif isinstance(data,EMData):
			if old:
				if isinstance(old,EMImage3DModule) :
					old.set_data(data)
					return old
			module = EMImage3DModule(application=app)
			module.set_data(data)
			return module
		elif isinstance(data,list) and isinstance(data[0],EMData):
			if old:
				if isinstance(old,EMImageMXModule) :
					old.set_data(data)
					return old
			module = EMImageMXModule(application=app)
			module.set_data(data)
			return module
		elif isinstance(data,list):
			if old:
				if isinstance(old,EMPlot2DModule) :
					old.set_data(data)
					return old
			module = EMPlot2DModule(application=app)
			module.set_data("data",data)
			return module	
		else:
			raise Exception,"data must be a single EMData object or a list of EMData objects"


class EMModuleFromFile(object):
	"""This is basically a factory class that will return an instance of the appropriate EMDisplay class,
	using only a file name as input. Can force plot and force 2d display, also.
	"""
	def __new__(cls,filename,application,force_plot=False,force_2d=False):
		
		file_type = Util.get_filename_ext(filename)
		em_file_type = EMUtil.get_image_ext_type(file_type)
		
		if force_plot and force_2d:
			# ok this sucks but it suffices for the time being
			print "Error, the force_plot and force_2d options are mutually exclusive"
			return None
		
		if force_plot:
			module = EMPlot2DModule(application=application)
			module.set_data_from_file(filename)
			return module
		
		if em_file_type != IMAGE_UNKNOWN:
			data=EMData.read_images(filename)
			if len(data) == 1: data = data[0]
			
			if force_2d or isinstance(data,EMData) and data.get_zsize()==1:
				module= EMImage2DModule(application=application)
			elif isinstance(data,EMData):
				module = EMImage3DModule(application=application)
			elif isinstance(data,list) and isinstance(data[0],EMData):
				module = EMImageMXModule(application=application)
			else: raise # weirdness, this should never happen
			module.set_data(data,filename)
			return module
		else:
			module = EMPlot2DModule(application=application)
			module.set_data_from_file(filename)
			return module

