#!/usr/bin/env python

# Author: Muthu Alagappan, 07/22/09
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

from em3dmodule import *
from EMAN2 import PDBReader
import sys
import os


class AlaRenderer:
	def __init__(self): pass
		
	def __call__(self,res,target):
		t1 = res[3].index('CB')

		target.makeStick(res, 0, 1)
		target.makeStick(res, 1, 2)
		target.makeStick(res, 2, 3)

		target.makeStick(res, 1, t1)

class ArgRenderer:
	def __init__(self): pass
		
	def __call__(self,res,target):
		t1 = res[3].index('CB')
		t2 = res[3].index('CG')
		t3 = res[3].index('CD')
		t4 = res[3].index('NE')
		t5 = res[3].index('CZ')
		t6 = res[3].index('NH1')
		t7 = res[3].index('NH2')


		target.makeStick(res, 0, 1)
		target.makeStick(res, 1, 2)
		target.makeStick(res, 2, 3)

		target.makeStick(res, 1, t1)
		target.makeStick(res, t1, t2)
		target.makeStick(res, t2, t3)
		target.makeStick(res, t3, t4)
		target.makeStick(res, t4, t5)
		target.makeStick(res, t5, t6)
		target.makeStick(res, t5, t7)

class AspRenderer:
	def __init__(self): pass
		
	def __call__(self,res,target):
		t1 = res[3].index('CB')
		t2 = res[3].index('CG')
		t3 = res[3].index('OD1')
		t4 = res[3].index('OD2')


		target.makeStick(res, 0, 1)
		target.makeStick(res, 1, 2)
		target.makeStick(res, 2, 3)

		target.makeStick(res, 1, t1)
		target.makeStick(res, t1, t2)
		target.makeStick(res, t2, t3)
		target.makeStick(res, t2, t4)

class AsnRenderer:
	def __init__(self): pass
		
	def __call__(self,res,target):
		t1 = res[3].index('CB')
		t2 = res[3].index('CG')
		t3 = res[3].index('OD1')
		t4 = res[3].index('ND2')


		target.makeStick(res, 0, 1)
		target.makeStick(res, 1, 2)
		target.makeStick(res, 2, 3)

		target.makeStick(res, 1, t1)
		target.makeStick(res, t1, t2)
		target.makeStick(res, t2, t3)
		target.makeStick(res, t2, t4)

class CysRenderer:
	def __init__(self): pass
		
	def __call__(self,res,target):
		t1 = res[3].index('CB')
		t2 = res[3].index('SG')

		target.makeStick(res, 0, 1)
		target.makeStick(res, 1, 2)
		target.makeStick(res, 2, 3)

		target.makeStick(res, 1, t1)
		target.makeStick(res, t1, t2)

class GlyRenderer:
	def __init__(self): pass
		
	def __call__(self,res,target):
		target.makeStick(res, 0, 1)
		target.makeStick(res, 1, 2)
		target.makeStick(res, 2, 3)

class GlnRenderer:
	def __init__(self): pass
		
	def __call__(self,res,target):
		t1 = res[3].index('CB')
		t2 = res[3].index('CG')
		t3 = res[3].index('CD')
		t4 = res[3].index('OE1')
		t5 = res[3].index('NE2')


		target.makeStick(res, 0, 1)
		target.makeStick(res, 1, 2)
		target.makeStick(res, 2, 3)

		target.makeStick(res, 1, t1)
		target.makeStick(res, t1, t2)
		target.makeStick(res, t2, t3)
		target.makeStick(res, t3, t4)
		target.makeStick(res, t3, t5)

class GluRenderer:
	def __init__(self): pass
		
	def __call__(self,res,target):
		t1 = res[3].index('CB')
		t2 = res[3].index('CG')
		t3 = res[3].index('CD')
		t4 = res[3].index('OE1')
		t5 = res[3].index('OE2')


		target.makeStick(res, 0, 1)
		target.makeStick(res, 1, 2)
		target.makeStick(res, 2, 3)

		target.makeStick(res, 1, t1)
		target.makeStick(res, t1, t2)
		target.makeStick(res, t2, t3)
		target.makeStick(res, t3, t4)
		target.makeStick(res, t3, t5)

class HisRenderer:
	def __init__(self): pass
		
	def __call__(self,res,target):
		t1 = res[3].index('CB')
		t2 = res[3].index('CG')
		t3 = res[3].index('CD2')
		t4 = res[3].index('ND1')
		t5 = res[3].index('NE2')
		t6 = res[3].index('CE1')


		target.makeStick(res, 0, 1)
		target.makeStick(res, 1, 2)
		target.makeStick(res, 2, 3)

		target.makeStick(res, 1, t1)
		target.makeStick(res, t1, t2)
		target.makeStick(res, t2, t3)
		target.makeStick(res, t2, t4)
		target.makeStick(res, t3, t5)
		target.makeStick(res, t5, t6)
		target.makeStick(res, t4, t6)

class IleRenderer:
	def __init__(self): pass
		
	def __call__(self,res,target):
		t1 = res[3].index('CB')
		t2 = res[3].index('CG1')
		t3 = res[3].index('CG2')
		t4 = res[3].index('CD1')


		target.makeStick(res, 0, 1)
		target.makeStick(res, 1, 2)
		target.makeStick(res, 2, 3)

		target.makeStick(res, 1, t1)
		target.makeStick(res, t1, t2)
		target.makeStick(res, t1, t3)
		target.makeStick(res, t2, t4)

class LeuRenderer:
	def __init__(self): pass
		
	def __call__(self,res,target):
		t1 = res[3].index('CB')
		t2 = res[3].index('CG')
		t3 = res[3].index('CD1')
		t4 = res[3].index('CD2')


		target.makeStick(res, 0, 1)
		target.makeStick(res, 1, 2)
		target.makeStick(res, 2, 3)

		target.makeStick(res, 1, t1)
		target.makeStick(res, t1, t2)
		target.makeStick(res, t2, t3)
		target.makeStick(res, t2, t4)

class LysRenderer:
	def __init__(self): pass
		
	def __call__(self,res,target):
		t1 = res[3].index('CB')
		t2 = res[3].index('CG')
		t3 = res[3].index('CD')
		t4 = res[3].index('CE')
		t5 = res[3].index('NZ')


		target.makeStick(res, 0, 1)
		target.makeStick(res, 1, 2)
		target.makeStick(res, 2, 3)

		target.makeStick(res, 1, t1)
		target.makeStick(res, t1, t2)
		target.makeStick(res, t2, t3)
		target.makeStick(res, t3, t4)
		target.makeStick(res, t4, t5)

class MetRenderer:
	def __init__(self): pass
		
	def __call__(self,res,target):
		t1 = res[3].index('CB')
		t2 = res[3].index('CG')
		t3 = res[3].index('SD')
		t4 = res[3].index('CE')


		target.makeStick(res, 0, 1)
		target.makeStick(res, 1, 2)
		target.makeStick(res, 2, 3)

		target.makeStick(res, 1, t1)
		target.makeStick(res, t1, t2)
		target.makeStick(res, t2, t3)
		target.makeStick(res, t3, t4)

class PheRenderer:
	def __init__(self): pass
		
	def __call__(self,res,target):
		t1 = res[3].index('CB')
		t2 = res[3].index('CG')
		t3 = res[3].index('CD1')
		t4 = res[3].index('CD2')
		t5 = res[3].index('CE1')
		t6 = res[3].index('CE2')
		t7 = res[3].index('CZ')


		target.makeStick(res, 0, 1)
		target.makeStick(res, 1, 2)
		target.makeStick(res, 2, 3)

		target.makeStick(res, 1, t1)
		target.makeStick(res, t1, t2)
		target.makeStick(res, t2, t3)
		target.makeStick(res, t2, t4)
		target.makeStick(res, t3, t5)
		target.makeStick(res, t4, t6)
		target.makeStick(res, t5, t7)
		target.makeStick(res, t6, t7)

class ProRenderer:
	def __init__(self): pass
		
	def __call__(self,res,target):
		t1 = res[3].index('CB')
		t2 = res[3].index('CG')
		t3 = res[3].index('CD')
		t4 = res[3].index('N')


		target.makeStick(res, 0, 1)
		target.makeStick(res, 1, 2)
		target.makeStick(res, 2, 3)

		target.makeStick(res, 1, t1)
		target.makeStick(res, t1, t2)
		target.makeStick(res, t2, t3)
		target.makeStick(res, t3, t4)

class SerRenderer:
	def __init__(self): pass
		
	def __call__(self,res,target):
		t1 = res[3].index('CB')
		t2 = res[3].index('OG')

		target.makeStick(res, 0, 1)
		target.makeStick(res, 1, 2)
		target.makeStick(res, 2, 3)

		target.makeStick(res, 1, t1)
		target.makeStick(res, t1, t2)

class ThrRenderer:
	def __init__(self): pass
		
	def __call__(self,res,target):
		t1 = res[3].index('CB')
		t2 = res[3].index('CG2')
		t3 = res[3].index('OG1')

		target.makeStick(res, 0, 1)
		target.makeStick(res, 1, 2)
		target.makeStick(res, 2, 3)

		target.makeStick(res, 1, t1)
		target.makeStick(res, t1, t2)
		target.makeStick(res, t1, t3)

class TrpRenderer:
	def __init__(self): pass
		
	def __call__(self,res,target):
		t1 = res[3].index('CB')
		t2 = res[3].index('CG')
		t3 = res[3].index('CD1')
		t4 = res[3].index('CD2')
		t5 = res[3].index('NE1')
		t6 = res[3].index('CE2')
		t7 = res[3].index('CE3')
		t8 = res[3].index('CZ3')
		t9 = res[3].index('CH2')
		t10 = res[3].index('CZ2')

		target.makeStick(res, 0, 1)
		target.makeStick(res, 1, 2)
		target.makeStick(res, 2, 3)

		target.makeStick(res, 1, t1)
		target.makeStick(res, t1, t2)
		target.makeStick(res, t2, t3)
		target.makeStick(res, t2, t4)
		target.makeStick(res, t3, t5)
		target.makeStick(res, t5, t6)
		target.makeStick(res, t4, t6)
		target.makeStick(res, t4, t7)
		target.makeStick(res, t7, t8)
		target.makeStick(res, t8, t9)
		target.makeStick(res, t10, t9)

class TyrRenderer:
	def __init__(self): pass
		
	def __call__(self,res,target):
		t1 = res[3].index('CB')
		t2 = res[3].index('CG')
		t3 = res[3].index('CD1')
		t4 = res[3].index('CD2')
		t5 = res[3].index('CE1')
		t6 = res[3].index('CE2')
		t7 = res[3].index('CZ')
		t8 = res[3].index('OH')


		target.makeStick(res, 0, 1)
		target.makeStick(res, 1, 2)
		target.makeStick(res, 2, 3)

		target.makeStick(res, 1, t1)
		target.makeStick(res, t1, t2)
		target.makeStick(res, t2, t3)
		target.makeStick(res, t2, t4)
		target.makeStick(res, t3, t5)
		target.makeStick(res, t4, t6)
		target.makeStick(res, t5, t7)
		target.makeStick(res, t6, t7)
		target.makeStick(res, t7, t8)

class ValRenderer:
	def __init__(self): pass
		
	def __call__(self,res,target):
		t1 = res[3].index('CB')
		t2 = res[3].index('CG2')
		t3 = res[3].index('CG1')

		target.makeStick(res, 0, 1)
		target.makeStick(res, 1, 2)
		target.makeStick(res, 2, 3)

		target.makeStick(res, 1, t1)
		target.makeStick(res, t1, t2)
		target.makeStick(res, t1, t3)



class EMPDBViewer(EM3DModule):
	def __init__(self, application=None,ensure_gl_context=True,application_control=True):
		EM3DModule.__init__(self,application,ensure_gl_context=ensure_gl_context,application_control=application_control)
		self.fName = ""
		self.text = self.fName
		self.dl = None
		
		self.side_chain_renderer = {}
		self.side_chain_renderer["ALA"] = AlaRenderer()
		self.side_chain_renderer["ARG"] = ArgRenderer()
		self.side_chain_renderer["ASP"] = AspRenderer()
		self.side_chain_renderer["ASN"] = AsnRenderer()
		self.side_chain_renderer["CYS"] = CysRenderer()
		self.side_chain_renderer["GLY"] = GlyRenderer()
		self.side_chain_renderer["GLN"] = GlnRenderer()
		self.side_chain_renderer["GLU"] = GluRenderer()
		self.side_chain_renderer["HIS"] = HisRenderer()
		self.side_chain_renderer["ILE"] = IleRenderer()
		self.side_chain_renderer["LEU"] = LeuRenderer()
		self.side_chain_renderer["LYS"] = LysRenderer()
		self.side_chain_renderer["MET"] = MetRenderer()
		self.side_chain_renderer["PHE"] = PheRenderer()
		self.side_chain_renderer["PRO"] = ProRenderer()
		self.side_chain_renderer["SER"] = SerRenderer()
		self.side_chain_renderer["THR"] = ThrRenderer()
		self.side_chain_renderer["TRP"] = TrpRenderer()
		self.side_chain_renderer["TYR"] = TyrRenderer()
		self.side_chain_renderer["VAL"] = ValRenderer()
		
		#self.pdb_delete = False
		#self.pdbFile_to_delete = None

	def current_text(self): return self.text
	
	def set_current_text(self,text):
		self.text = text
		self.get_inspector().text.setText(self.text)
		self.updateGL()

		
	def get_inspector(self):
		if self.inspector == None:
			self.inspector = EMPDBInspector(self)
		return self.inspector

	def createDefault(self):
		return          #display a default pdb here
		
	
	def draw_objects(self):
		self.init_basic_shapes() # only does something the first time you call it
		if (self.text == ""): 
			#default drawing
			self.createDefault()
			return
			
		
		#self.gl_context_parent.makeCurrent()
		if (self.text != self.fName): 
			if (self.dl != None): glDeleteLists(self.dl, 1)
			self.dl=None
			self.fName = self.text

		if (self.dl == None):
			self.dl=glGenLists(1)
			glNewList(self.dl,GL_COMPILE)
			self.buildResList()

			for res in self.allResidues:
				for i in range (0, len(res[0])):
					glPushMatrix()
					glTranslate(res[0][i], res[1][i], res[2][i])
					glScale(1,1,1)
					if (str(res[3][i])[0] == 'C'): self.load_gl_color("white")
					elif (str(res[3][i])[0] == 'N'): self.load_gl_color("green")
					elif (str(res[3][i])[0] == 'O'): self.load_gl_color("blue")
					elif (str(res[3][i])[0] == 'S'): self.load_gl_color("red")
					else: self.load_gl_color("silver")
					glCallList(self.highresspheredl)
					glPopMatrix()
			
#			self.load_gl_color("silver")
			for k in range (0, len(self.allResidues)):
				
				res = self.allResidues[k]
				key =  res[4][0]
				if self.side_chain_renderer.has_key(key):
					self.side_chain_renderer[key](res,self)
					continue


				if (k!=0):
				
					nt = [0,0,0]
					pt = [0,0,0]
					nt[0] = res[0][0]
					nt[1] = res[1][0]
					nt[2] = res[2][0]

					pt[0] = self.allResidues[(k-1)][0][2]
					pt[1] = self.allResidues[(k-1)][1][2]
					pt[2] = self.allResidues[(k-1)][2][2]
					self.cylinder_to_from(nt, pt, 0.2)
			glEndList()

		try: glCallList(self.dl)
		except: 
			print "call list failed",self.dl
			glDeleteLists(self.dl,1)
			self.dl = None

	def makeStick (self, res, index1, index2):
		n = [0,0,0]
		p = [0,0,0]
		p[0] = res[0][index1]
		p[1] = res[1][index1]
		p[2] = res[2][index1]

		n[0] = res[0][index2]
		n[1] = res[1][index2]
		n[2] = res[2][index2]
		self.cylinder_to_from(n, p, 0.2)	

	def buildResList (self):

		self.allResidues = []
		
		try:
			f = open(self.fName)
			f.close()
		except IOError:	
			print "Sorry, the file name \"" + str(self.fName) + "\" does not exist"
			sys.exit()
		
   		self.a = PDBReader()
    		self.a.read_from_pdb(self.fName)
    		point_x = self.a.get_x()
   		point_y = self.a.get_y()
	        point_z = self.a.get_z()
		point_atomName = self.a.get_atomName()
		point_resName = self.a.get_resName()
		point_resNum = self.a.get_resNum()
		x =[]
		y =[]
		z =[]
		atomName =[]
		resName = []
		amino = []
		currentRes = 1


    		for i in range(0, len(point_x)):
        		if (point_resNum[i]==currentRes):
           			x.append(point_x[i])
            			y.append(point_y[i])
            			z.append(point_z[i])
				temp = point_atomName[i]
				temp2 = temp.strip()
				atomName.append(temp2)
            			resName.append(point_resName[i])
       			else:
            			currentRes = point_resNum[i]
				amino.append(x[:])
				amino.append(y[:])
				amino.append(z[:])
				amino.append(atomName[:])
				amino.append(resName[:])
				self.allResidues.append(amino[:])
				del amino[:]
            			del x[:]
            			del y[:]
            			del z[:]
            			del atomName[:]
            			del resName[:]
           			x.append(point_x[i])
            			y.append(point_y[i])
            			z.append(point_z[i])
				temp = point_atomName[i]
				temp2 = temp.strip()
				atomName.append(temp2)
            			resName.append(point_resName[i])
			if (i == (len(point_x)-1)): 
				amino.append(x[:])
				amino.append(y[:])
				amino.append(z[:])
				amino.append(atomName[:])
				amino.append(resName[:])
				self.allResidues.append(amino[:])
				break


	def cylinder_to_from(self,next,prev,scale=0.5):
		dx = next[0] - prev[0]
		dy = next[1] - prev[1]
		dz = next[2] - prev[2]
		from math import sqrt,acos,atan2,pi
		try:
			length = sqrt(dx**2 + dy**2 + dz**2)
		except: return
		if length == 0: return

		alt = acos(dz/length)*180.0/pi
		phi = atan2(dy,dx)*180.0/pi
		
		glPushMatrix()
		glTranslatef(prev[0],prev[1],prev[2] )
		glRotatef(90+phi,0,0,1)
		glRotatef(alt,1,0,0)
		glScalef(scale,scale,length)
		self.load_gl_color("silver")
		glCallList(self.cylinderdl)

		glPopMatrix()		
	
	def get_pdb_file(self):
		return self.fName
		
class EMPDBInspector(EM3DInspector):
	def __init__(self,target,enable_advanced=False):
		EM3DInspector.__init__(self,target,enable_advanced)
		self.tabwidget.insertTab(0,self.get_pdb_tab(),"PDB Main")
		self.tabwidget.setCurrentIndex(0)
		
		'''
		self.vbl.setMargin(0)
		self.vbl.setSpacing(6)
		self.vbl.setObjectName("vbl")

		hbl1 = QtGui.QHBoxLayout()
		self.text = QtGui.QLineEdit()
		self.text.setText(self.target().current_text())
		hbl1.addWidget(self.text)
		self.browse = QtGui.QPushButton("Browse")
		hbl1.addWidget(self.browse)
		self.vbl.addLayout(hbl1)

		QtCore.QObject.connect(self.text, QtCore.SIGNAL("textChanged(const QString&)"), self.on_text_change)
		QtCore.QObject.connect(self.browse, QtCore.SIGNAL("clicked(bool)"), self.on_browse)
		'''
		
			
	def get_pdb_tab(self):
		'''
		@return an QtGui.QWidget, i.e. for insertion into a tab widget, or layour, etc
		'''
		widget = QtGui.QTabWidget()
		vbl = QtGui.QVBoxLayout(widget)
		vbl.setMargin(0)
		vbl.setSpacing(6)

		hbl1 = QtGui.QHBoxLayout()
		self.text = QtGui.QLineEdit()
		self.text.setText(self.target().current_text())
		hbl1.addWidget(self.text)
		self.browse = QtGui.QPushButton("Browse")
		hbl1.addWidget(self.browse)
		vbl.addLayout(hbl1)
		
		QtCore.QObject.connect(self.text, QtCore.SIGNAL("textEdited(const QString&)"), self.on_text_change)
		QtCore.QObject.connect(self.browse, QtCore.SIGNAL("clicked(bool)"), self.on_browse)
		
		return widget
	
	def on_text_change(self,text):
		#self.target().set_current_text(str(text))
		#self.target().updateGL()
		print "Use the Browse button to update the pdb file"

	def on_browse(self):
		import os
		self.fileName = QtGui.QFileDialog.getOpenFileName(self, "open file", os.getcwd(), "Text files (*.pdb)")
		if (self.fileName == ""): return
		self.target().set_current_text(str(self.fileName)) #self.target().text and self.text are what the user sees. 
		self.text.setText(self.fileName) #if self.text changes, then self.fName becomes self.text and the image regenerates	
		self.target().updateGL()
	
if __name__ == '__main__':
	from emapplication import EMStandAloneApplication
	em_app = EMStandAloneApplication()
	window = EMPDBViewer()
	#window.set_current_text("fh-solution-0-1UF2-T.pdb")
	em_app.show()
	em_app.execute()

