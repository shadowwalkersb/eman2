#! /usr/bin/env python
#
# Do not run this script directly. You could run this as 
# ipython --gui=qt -i e2_real.py
# otherwise it is normally run via the e2.py script
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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  2111-1307 USA
#
#

import global_def
from global_def import *

if global_def.GUIUSE: from PyQt4 import QtCore, QtGui, QtOpenGL
from emapplication import EMApp
import IPython.lib.inputhook


if global_def.GUIUSE:
	app=EMApp()
	IPython.lib.inputhook.enable_qt4(app)

from EMAN2 import *
from sparx import *
if global_def.GUIUSE:
	from emimage import image_update

	def ipy_on_timer():
		image_update()

	ipytimer = QtCore.QTimer()
	ipytimer.timeout.connect(ipy_on_timer)
	ipytimer.start(200)

print "Welcome to the interactive SPARX Python interface, provided by ipython"
