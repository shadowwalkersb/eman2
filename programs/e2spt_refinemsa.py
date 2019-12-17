#!/usr/bin/env python
#
# Author: Jesus Galaz  1/1/2012 (rewritten)
# Copyright (c) 2011- Baylor College of Medicine
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

from __future__ import print_function
from __future__ import division
from builtins import str
from sys import argv
import os
from EMAN2 import *
from EMAN2_utils import *

current = os.getcwd()
filesindir = os.listdir(current)

def main():
	progname = os.path.basename(sys.argv[0])
	usage = """prog [options] <Volume file>

	WARNING: This program still under development.
	
	Tomography 3-D particle picker and annotation tool. Still under development."""

	parser = EMArgumentParser(usage=usage,version=EMANVERSION)
	
	parser.add_argument("--ncls", type=int, default=3, help ="""Default=3. Number of classes to sort the particle stack into. In theory, a minimum of 2 conformational classes and 1 'garbage' class should be used.""")
	
	parser.add_argument("--nbasis", type=int, help="Basis vectors to use", default=3)

	parser.add_argument("--input", type=str, help="The name of the volumes stack that HAVE BEEN ALIGNED to a common reference", default=None)
	
	parser.add_argument("--verbose", "-v", dest="verbose", action="store", metavar="n", type=int, default=0, help="verbose level [0-9], higher number means higher level of verboseness")			
	parser.add_argument("--filter",type=int,help="Resolution (integer, in Angstroms) at which you want to apply a gaussian lowpass filter to the tomogram prior to loading it for boxing",default=0, guitype='intbox', row=3, col=2, rowspan=1, colspan=1)
	parser.add_argument("--preprocess",type=str,help="""A processor (as in e2proc3d.py) to be applied to the tomogram before opening it. \nFor example, a specific filter with specific parameters you might like. \nType 'e2proc3d.py --processors' at the commandline to see a list of the available processors and their usage""",default=None)
		
	(options, args) = parser.parse_args()
	
	logger = E2init(sys.argv, options.ppid)

	stack = options.input
	print("The stack name is", stack)
		
	stack_basis = stack.replace(".hdf","_basis.hdf")
	stack_projection = stack.replace(".hdf","_projection.hdf")
	
	ncls = 3

	if options.ncls:
		ncls = options.ncls
	cmd1=''
	cmd2=''
	cmd3=''
	
	cmd1 = 'e2msa.py --nbasis=' +  str(options.nbasis) + ' ' + stack  + ' ' + stack_basis
	
	cmd2 = 'e2basis.py --mean=1 project ' + stack_basis + ' ' +  stack + ' ' + stack_projection
	
	cmd3 = 'e2classifykmeans.py --ncls=' + str(options.ncls) + ' --average --original=' + stack + ' ' + stack_projection
	
	if cmd1 and cmd2 and cmd3:
		print("Running msa on stack %s through commands cmd1=%s, cmd2=%s, cmd3=%s" %( stack, cmd1, cmd2, cmd3 ))
		cmd = cmd1 + " && " + cmd2 + " && " + cmd3
		#print "The command to execute is", cmd
		runcmd( cmd )
	else:
		print("\nError building command for stack=%s, cmd1=%s, cmd2=%s, cmd3=%s" %( stack, cmd1, cmd2, cmd3 ))
		sys.exit(1)
	
	E2end(logger)
	
	return

"""
def runcmd(options,cmd):
	if options.verbose > 9:
		print("(e2spt_classaverage)(runcmd) running command", cmd)
	
	p=subprocess.Popen( cmd, shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	text=p.communicate()	
	p.stdout.close()
	
	
	print("(e2spt_refinemsa)(runcmd) done")

	return 1
"""
	
	
if __name__ == "__main__":

    main()
