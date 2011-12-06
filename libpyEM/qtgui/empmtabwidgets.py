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

from EMAN2 import *
import os
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import Qt
from embrowser import EMBrowserWidget, EMFileItemModel, EMDirEntry, nonone


class EMModelsTable(EMBrowserWidget):
	""" Widget to display junk from e2boxercache """
	def __init__(self, withmodal=False, multiselect=False):
		EMBrowserWidget.__init__(self, withmodal=withmodal, multiselect=multiselect, startpath="./initial_models")
	
	def setPath(self,path,silent=False):
		super(EMModelsTable, self).setPath(path,silent=False,inimodel=EMModelsModel)
		

class EMModelsModel(EMFileItemModel):
	""" Item model for the raw data """
	
	headers=("3D Models","Quality", "Dims")
	
	def __init__(self,startpath=None):
		EMFileItemModel.__init__(self, startpath=startpath, direntryclass=EMModelsEntry)
		
	def columnCount(self,parent):
		"Always 3 columns"
		#print "EMFileItemModel.columnCount()=6"
		return 3
		
	def data(self,index,role):
		"Returns the data for a specific location as a string"
		
		if not index.isValid() : return None
		if role!=Qt.DisplayRole : return None
		
		data=index.internalPointer()
		if data==None : 
			print "Error with index ",index.row(),index.column()
			return "XXX"
		#if index.column()==0 : print "EMFileItemModel.data(%d %d %s)=%s"%(index.row(),index.column(),index.parent(),str(data.__dict__))

		col=index.column()
		if col==0 : 
			if data.isbdb : return "bdb:"+data.name
			return nonone(data.name)
		elif col==1 :
			if data.quality==0 : return "-"
			return nonone(data.quality)
		elif col==2 :
			if data.dims==0 : return "-"
			return nonone(data.dims)

class EMModelsEntry(EMDirEntry):
	""" Subclassing of EMDirEntry to provide functionality"""
	
	col=(lambda x:x.name,lambda x:x.quality, lambda x:x.dims)
	
	def __init__(self,root,name,parent=None,hidedot=True):
		EMDirEntry.__init__(self,root,name,parent=parent,hidedot=hidedot)
		self.quality=None
		self.dims=None
		
	def fillDetails(self):
		"""Fills in the expensive metadata about this entry. Returns False if no update was necessary."""
		if self.filetype!=None : return False		# must all ready be filled in

		# Should only be this:
		self.filetype="Image"
			
		# Get particle stack headers
		a = None
		try:
			a = EMData(self.path(),0,True)
		except:
			pass	
		if a:
			self.dims = "%dx%dx%d"%(a.get_xsize(),a.get_ysize(),a.get_zsize())
			try:
				self.quality = a['quality']
			except:
				pass
			
		return True
		
################################################################################################################

class EMSetsTable(EMBrowserWidget):
	""" Widget to display junk from e2boxercache """
	def __init__(self, withmodal=False, multiselect=False):
		EMBrowserWidget.__init__(self, withmodal=withmodal, multiselect=multiselect, startpath="./sets")
	
	def setPath(self,path,silent=False):
		super(EMSetsTable, self).setPath(path,silent=False,inimodel=EMSetsModel)


class EMSetsModel(EMFileItemModel):
	""" Item model for the raw data """
	
	headers=("Particles","NUm Particles", "Dims")
	
	def __init__(self,startpath=None):
		EMFileItemModel.__init__(self, startpath=startpath, direntryclass=EMSetsEntry)
		
	def columnCount(self,parent):
		"Always 3 columns"
		#print "EMFileItemModel.columnCount()=6"
		return 3
		
	def data(self,index,role):
		"Returns the data for a specific location as a string"
		
		if not index.isValid() : return None
		if role!=Qt.DisplayRole : return None
		
		data=index.internalPointer()
		if data==None : 
			print "Error with index ",index.row(),index.column()
			return "XXX"
		#if index.column()==0 : print "EMFileItemModel.data(%d %d %s)=%s"%(index.row(),index.column(),index.parent(),str(data.__dict__))

		col=index.column()
		if col==0 : 
			if data.isbdb : return "bdb:"+data.name
			return nonone(data.name)
		elif col==1 :
			if data.partcount==0 : return "-"
			return nonone(data.partcount)
		elif col==2 :
			if data.dims==0 : return "-"
			return nonone(data.dims)

class EMSetsEntry(EMDirEntry):
	""" Subclassing of EMDirEntry to provide functionality"""
	
	col=(lambda x:x.name,lambda x:x.partcount, lambda x:x.dims)
	
	def __init__(self,root,name,parent=None,hidedot=True):
		EMDirEntry.__init__(self,root,name,parent=parent,hidedot=hidedot)
		self.partcount=None
		self.dims=None
		
	def fillDetails(self):
		"""Fills in the expensive metadata about this entry. Returns False if no update was necessary."""
		if self.filetype!=None : return False		# must all ready be filled in
		
		# get image counts
		try:
			self.partcount = EMUtil.get_image_count(self.path())
			if self.partcount == 1 : self.filetype="Image"
			if int(self.partcount) > 1 : self.filetype="Image Stack"
		except:
			self.filetype="-"
		

		# Get particle stack headers
		a = None
		try:
			a = EMData(self.path(),0,True)
		except:
			pass	
		if a:
			self.dims = "%dx%dx%d"%(a.get_xsize(),a.get_ysize(),a.get_zsize())
			
		return True


###########################################################################################################################

class EMParticlesTable(EMBrowserWidget):
	""" Widget to display junk from e2boxercache """
	def __init__(self, withmodal=False, multiselect=False):
		EMBrowserWidget.__init__(self, withmodal=withmodal, multiselect=multiselect, startpath="./particles")
	
	def setPath(self,path,silent=False):
		super(EMParticlesTable, self).setPath(path,silent=False,inimodel=EMParticlesModel)

class EMParticlesModel(EMFileItemModel):
	""" Item model for the raw data """
	
	headers=("Raw Data Files","Type", "Num Particles", "Particle Dims", "Defocus", "B Factor", "SNR", "Quality", "Sampling")
	
	def __init__(self,startpath=None):
		EMFileItemModel.__init__(self, startpath=startpath, direntryclass=EMParticlesEntry)
		
	def columnCount(self,parent):
		"Always 9 columns"
		#print "EMFileItemModel.columnCount()=6"
		return 9
		
	def data(self,index,role):
		"Returns the data for a specific location as a string"
		
		if not index.isValid() : return None
		if role!=Qt.DisplayRole : return None
		
		data=index.internalPointer()
		if data==None : 
			print "Error with index ",index.row(),index.column()
			return "XXX"
		#if index.column()==0 : print "EMFileItemModel.data(%d %d %s)=%s"%(index.row(),index.column(),index.parent(),str(data.__dict__))

		col=index.column()
		if col==0 : 
			if data.isbdb : return "bdb:"+data.name
			return nonone(data.name)
		elif col==1 : 
			if data.type==0 : return "-"
			return nonone(data.type)
		elif col==2 :
			if data.particlecount==0 : return "-"
			return nonone(data.particlecount)
		elif col==3 :
			if data.particledim==0 : return "-"
			return nonone(data.particledim)
		elif col==4 :
			if data.defocus==0 : return "-"
			return nonone(data.defocus)
		elif col==5 :
			if data.bfactor==0 : return "-"
			return nonone(data.bfactor)
		elif col==6 :
			if data.snr==0 : return "-"
			return nonone(data.snr)
		elif col==7 :
			if data.quality==0 : return "-"
			return nonone(data.quality)
		elif col==8 :
			if data.sampling==0 : return "-"
			return nonone(data.sampling)

class EMParticlesEntry(EMDirEntry):
	""" Subclassing of EMDirEntry to provide functionality"""
	
	col=(lambda x:x.name,lambda x:x.type,lambda x:x.particlecount, lambda x:x.particledim, lambda x:x.defocus, lambda x:x.bfactor, lambda x:x.snr, lambda x:x.quality, lambda x:x.sampling)
	
	def __init__(self,root,name,parent=None,hidedot=True):
		EMDirEntry.__init__(self,root,name,parent=parent,hidedot=hidedot)
		self.type = None
		self.particlecount=None
		self.particledim=None
		self.defocus=None
		self.bfactor=None
		self.snr=None
		self.quality=None
		self.sampling=None
		
	def fillDetails(self):
		"""Fills in the expensive metadata about this entry. Returns False if no update was necessary."""
		if self.filetype!=None : return False		# must all ready be filled in
		
		# get image counts
		try:
			self.particlecount = str(EMUtil.get_image_count(self.path()))
			if int(self.particlecount)==1 : self.filetype="Image"
			if int(self.particlecount) > 1 : self.filetype="Image Stack"
		
		except:
			pass
		
		# get partivle set type
		try:
			self.type = str(self.path().split('_ctf_')[1])
		except:
			pass
		
		# Get particle stack headers
		d = None
		try:
			a = EMData(self.path(),0,True)
			d = a.get_attr_dict()
		except:
			pass
		
		# get CTF dims
		if d:
			if d.has_key('nx') and d.has_key('ny') and d.has_key('nz'):
				self.particledim = "%dx%dx%d"%(d['nx'],d['ny'],d['nz'])
			if d.has_key('ctf'):
				ctf = d['ctf']
				self.defocus = "%.3f" %ctf.defocus
				self.bfactor = "%.3f" %ctf.bfactor
				self.snr = "%.3f" %(sum(ctf.snr)/len(ctf.snr))
				self.sampling = str(len(ctf.background))
		# get quality
		if db_check_dict("bdb:e2ctf.parms"):
			ctf_db = db_open_dict("bdb:e2ctf.parms",ro=True)
			try:
				quality = ctf_db[get_file_tag(self.path()).split("_ctf")[0]][3]
				self.quality = "%d" %quality
			except:
				pass
								
		return True
		
######################################################################################################################

class EMParticlesEditTable(EMBrowserWidget):
	""" Widget to display junk from e2boxercache """
	def __init__(self, withmodal=False, multiselect=False):
		EMBrowserWidget.__init__(self, withmodal=withmodal, multiselect=multiselect, startpath="./particles",setsmode=True)
	
	def setPath(self,path,silent=False):
		super(EMParticlesEditTable, self).setPath(path,silent=False,inimodel=EMParticlesEditModel)
		
class EMParticlesEditModel(EMFileItemModel):
	""" Item model for the raw data """
	
	headers=("Raw Data Files","Type", "Num Particles", "Bad Particles", "Defocus", "B Factor", "SNR", "Quality", "Sampling", "Particle Dims")
	
	def __init__(self,startpath=None):
		EMFileItemModel.__init__(self, startpath=startpath, direntryclass=EMParticlesEditEntry)
		
	def columnCount(self,parent):
		"Always 10 columns"
		#print "EMFileItemModel.columnCount()=6"
		return 10
		
	def data(self,index,role):
		"Returns the data for a specific location as a string"
		
		if not index.isValid() : return None
		if role!=Qt.DisplayRole : return None
		
		data=index.internalPointer()
		if data==None : 
			print "Error with index ",index.row(),index.column()
			return "XXX"
		#if index.column()==0 : print "EMFileItemModel.data(%d %d %s)=%s"%(index.row(),index.column(),index.parent(),str(data.__dict__))

		col=index.column()
		if col==0 : 
			if data.isbdb : return "bdb:"+data.name
			return nonone(data.name)
		elif col==1 : 
			if data.type==0 : return "-"
			return nonone(data.type)
		elif col==2 :
			if data.particlecount==0 : return "-"
			return nonone(data.particlecount)
		elif col==3 :
			if data.badparticlecount==0 : return "-"
			return nonone(data.badparticlecount)
		elif col==4 :
			if data.defocus==0 : return "-"
			return nonone(data.defocus)
		elif col==5 :
			if data.bfactor==0 : return "-"
			return nonone(data.bfactor)
		elif col==6 :
			if data.snr==0 : return "-"
			return nonone(data.snr)
		elif col==7 :
			if data.quality==0 : return "-"
			return nonone(data.quality)
		elif col==8 :
			if data.sampling==0 : return "-"
			return nonone(data.sampling)
		elif col==9 :
			if data.particledim==0 : return "-"
			return nonone(data.particledim)

class EMParticlesEditEntry(EMParticlesEntry):
	""" Subclassing of EMDirEntry to provide functionality"""
	
	col=(lambda x:x.name,lambda x:x.type,lambda x:x.particlecount, lambda x:x.badparticlecount, lambda x:x.defocus, lambda x:x.bfactor, lambda x:x.snr, lambda x:x.quality, lambda x:x.sampling, lambda x:x.particledim)
	
	def __init__(self,root,name,parent=None,hidedot=True):
		EMParticlesEntry.__init__(self,root=root,name=name,parent=parent,hidedot=hidedot)
		self.badparticlecount = None
		
	def fillDetails(self):
		super(EMParticlesEditEntry, self).fillDetails()
		
		# bad particles
		if db_check_dict("bdb:select"):
			select_db = db_open_dict("bdb:select",ro=True)
			try:
			#print self.getBaseName(self.path())
				self.badparticlecount = len(select_db[self.getBaseName(self.path())])
			except:
				pass
			
#######################################################################################################################

class EMBoxesTable(EMBrowserWidget):
	""" Widget to display junk from e2boxercache """
	def __init__(self, withmodal=False, multiselect=False):
		EMBrowserWidget.__init__(self, withmodal=withmodal, multiselect=multiselect, startpath="./micrographs")
	
	def setPath(self,path,silent=False):
		super(EMBoxesTable, self).setPath(path,silent=False,inimodel=EMBoxesModel)


class EMBoxesModel(EMFileItemModel):
	""" Item model for the raw data """
	
	headers=("Raw Data Files","Stored Boxes", "Quality")
	
	def __init__(self,startpath=None):
		EMFileItemModel.__init__(self, startpath=startpath, direntryclass=EMBoxesEntry)
		
	def columnCount(self,parent):
		"Always 3 columns"
		#print "EMFileItemModel.columnCount()=6"
		return 3
		
	def data(self,index,role):
		"Returns the data for a specific location as a string"
		
		if not index.isValid() : return None
		if role!=Qt.DisplayRole : return None
		
		data=index.internalPointer()
		if data==None : 
			print "Error with index ",index.row(),index.column()
			return "XXX"
		#if index.column()==0 : print "EMFileItemModel.data(%d %d %s)=%s"%(index.row(),index.column(),index.parent(),str(data.__dict__))

		col=index.column()
		if col==0 : 
			if data.isbdb : return "bdb:"+data.name
			return nonone(data.name)
		elif col==1 :
			if data.boxcount==0 : return "-"
			return nonone(data.boxcount)
		elif col==2 :
			if data.quality==0 : return "-"
			return nonone(data.quality)

class EMBoxesEntry(EMDirEntry):
	""" Subclassing of EMDirEntry to provide functionality"""
	
	col=(lambda x:x.name,lambda x:x.boxcount, lambda x:x.quality)
	
	def __init__(self,root,name,parent=None,hidedot=True):
		EMDirEntry.__init__(self,root,name,parent=parent,hidedot=hidedot)
		self.boxcount=None
		self.quality=None
		
	def fillDetails(self):
		"""Fills in the expensive metadata about this entry. Returns False if no update was necessary."""
		if self.filetype!=None : return False		# must all ready be filled in
		
		# get image counts
		try:
			if EMUtil.get_image_count(self.path())==1 : self.filetype="Image"
		except:
			self.filetype="-"
		
		# get quality and box numbers
		if db_check_dict('bdb:e2boxercache#quality'):
			qdb = db_open_dict('bdb:e2boxercache#quality')
			self.quality = qdb[self.getBaseName(self.path())]
			
		if db_check_dict('bdb:e2boxercache#boxes'):
			db = db_open_dict('bdb:e2boxercache#boxes')
			bc = db[self.getBaseName(self.path())]
			if bc:
				self.boxcount = len(bc)
				return True
			
		return True

#############################################################################################################################

class EMRCTBoxesTable(EMBrowserWidget):
	""" Widget to display junk from e2boxercache """
	def __init__(self, withmodal=False, multiselect=False):
		EMBrowserWidget.__init__(self, withmodal=withmodal, multiselect=multiselect, startpath="./micrographs")
	
	def setPath(self,path,silent=False):
		super(EMRCTBoxesTable, self).setPath(path,silent=False,inimodel=EMRCTBoxesModel)


class EMRCTBoxesModel(EMFileItemModel):
	""" Item model for the raw data """
	
	headers=("Raw Data Files","Stored Boxes", "Quality")
	
	def __init__(self,startpath=None):
		EMFileItemModel.__init__(self, startpath=startpath, direntryclass=EMRCTBoxesEntry)
		
	def columnCount(self,parent):
		"Always 3 columns"
		#print "EMFileItemModel.columnCount()=6"
		return 3
		
	def data(self,index,role):
		"Returns the data for a specific location as a string"
		
		if not index.isValid() : return None
		if role!=Qt.DisplayRole : return None
		
		data=index.internalPointer()
		if data==None : 
			print "Error with index ",index.row(),index.column()
			return "XXX"
		#if index.column()==0 : print "EMFileItemModel.data(%d %d %s)=%s"%(index.row(),index.column(),index.parent(),str(data.__dict__))

		col=index.column()
		if col==0 : 
			if data.isbdb : return "bdb:"+data.name
			return nonone(data.name)
		elif col==1 :
			if data.boxcount==0 : return "-"
			return nonone(data.boxcount)
		elif col==2 :
			if data.quality==0 : return "-"
			return nonone(data.quality)

class EMRCTBoxesEntry(EMDirEntry):
	""" Subclassing of EMDirEntry to provide functionality"""
	
	col=(lambda x:x.name,lambda x:x.boxcount, lambda x:x.quality)
	
	def __init__(self,root,name,parent=None,hidedot=True):
		EMDirEntry.__init__(self,root,name,parent=parent,hidedot=hidedot)
		self.boxcount=None
		self.quality=None
		
	def fillDetails(self):
		"""Fills in the expensive metadata about this entry. Returns False if no update was necessary."""
		if self.filetype!=None : return False		# must all ready be filled in
		
		# get image counts
		try:
			if EMUtil.get_image_count(self.path())==1 : self.filetype="Image"
		except:
			pass
		
		# get quality and box numbers
		if db_check_dict('bdb:e2boxercache#quality'):
			qdb = db_open_dict('bdb:e2boxercache#quality')
			self.quality = qdb[self.getBaseName(self.path())]
			
		if db_check_dict('bdb:e2boxercache#boxestilted'):
			db = db_open_dict('bdb:e2boxercache#boxestilted')
			bc = db[self.getBaseName(self.path())]
			if bc:
				self.boxcount = len(bc)
				return True
			
		if db_check_dict('bdb:e2boxercache#boxesuntilted'):
			db = db_open_dict('bdb:e2boxercache#boxesuntilted')
			bc = db[self.getBaseName(self.path())]
			if bc:
				self.boxcount = len(bc)
				return True
			
		return True
#################################################################################################################################

class EMSubTomosTable(EMBrowserWidget):
	""" Widget to display Raw Data """
	def __init__(self, withmodal=False, multiselect=False):
		EMBrowserWidget.__init__(self, withmodal=withmodal, multiselect=multiselect, startpath="./subtomograms")
	
	def setPath(self,path,silent=False):
		super(EMSubTomosTable, self).setPath(path,silent=False,inimodel=EMSubTomosModel)
	
class EMSubTomosModel(EMFileItemModel):
	""" Item model for the raw data """
	
	headers=("Subtomograms","num subtomos", "dims")
	
	def __init__(self,startpath=None):
		EMFileItemModel.__init__(self, startpath=startpath, direntryclass=EMRCTBoxesEntry)
		
	def columnCount(self,parent):
		"Always 3 columns"
		#print "EMFileItemModel.columnCount()=6"
		return 3
		
	def data(self,index,role):
		"Returns the data for a specific location as a string"
		
		if not index.isValid() : return None
		if role!=Qt.DisplayRole : return None
		
		data=index.internalPointer()
		if data==None : 
			print "Error with index ",index.row(),index.column()
			return "XXX"
		#if index.column()==0 : print "EMFileItemModel.data(%d %d %s)=%s"%(index.row(),index.column(),index.parent(),str(data.__dict__))

		col=index.column()
		if col==0 : 
			if data.isbdb : return "bdb:"+data.name
			return nonone(data.name)
		elif col==1 :
			if data.nimg==0 : return "-"
			return nonone(data.nimg)
		elif col==2 :
			if data.quality==0 : return "-"
			return nonone(data.dims)

class EMSubTomosEntry(EMDirEntry):
	""" Subclassing of EMDirEntry to provide functionality"""
	
	col=(lambda x:x.name,lambda x:x.nimg, lambda x:x.dims)
	
	def __init__(self,root,name,parent=None,hidedot=True):
		EMDirEntry.__init__(self,root,name,parent=parent,hidedot=hidedot)
		
	def fillDetails(self):
		# Maybe add code to cache results.....
		super(EMSubTomosEntry, self).fillDetails()

#################################################################################################################################

class EMRawDataTable(EMBrowserWidget):
	""" Widget to display Raw Data """
	def __init__(self, withmodal=False, multiselect=False, startpath="./micrographs"):
		EMBrowserWidget.__init__(self, withmodal=withmodal, multiselect=multiselect, startpath=startpath)
	
	def setPath(self,path,silent=False):
		super(EMRawDataTable, self).setPath(path,silent=False,inimodel=EMRawDataModel)

			
class EMRawDataModel(EMFileItemModel):
	""" Item model for the raw data """
	
	headers=("Raw Data Files","Dimensions")
	
	def __init__(self,startpath=None):
		EMFileItemModel.__init__(self, startpath=startpath, direntryclass=EMRawDataEntry)
		
	def columnCount(self,parent):
		"Always 2 columns"
		#print "EMFileItemModel.columnCount()=6"
		return 2
		
	def data(self,index,role):
		"Returns the data for a specific location as a string"
		
		if not index.isValid() : return None
		if role!=Qt.DisplayRole : return None
		
		data=index.internalPointer()
		if data==None : 
			print "Error with index ",index.row(),index.column()
			return "XXX"
		#if index.column()==0 : print "EMFileItemModel.data(%d %d %s)=%s"%(index.row(),index.column(),index.parent(),str(data.__dict__))

		col=index.column()
		if col==0 : 
			if data.isbdb : return "bdb:"+data.name
			return nonone(data.name)
		elif col==1 :
			if data.dim==0 : return "-"
			return nonone(data.dim)
		
class EMRawDataEntry(EMDirEntry):
	""" Subclassing of EMDirEntry to provide functionality"""
	
	col=(lambda x:x.name,lambda x:x.dim)
	
	def __init__(self,root,name,parent=None,hidedot=True):
		EMDirEntry.__init__(self,root,name,parent=parent,hidedot=hidedot)
		
	def fillDetails(self):
		# Maybe add code to cache results.....
		super(EMRawDataEntry, self).fillDetails()
		
#################################################################################################################################

class EMTomoDataTable(EMRawDataTable):
	""" Widget to display Raw Data """
	def __init__(self, withmodal=False, multiselect=False):
		EMRawDataTable.__init__(self, withmodal=withmodal, multiselect=multiselect, startpath="./rawtomograms")
	
	def setPath(self,path,silent=False):
		super(EMTomoDataTable, self).setPath(path,silent=False)	