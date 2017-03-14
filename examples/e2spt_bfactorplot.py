#!/usr/bin/python2.7
#
# Author: Jesus Galaz, 22/Jan/2017; last update Jan/22/2017
# Copyright (c) 2011 Baylor College of Medicine
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

import os
from EMAN2 import *

import sys
import numpy
import math
import collections

from e2spt_intrafsc import genOddAndEvenVols, fscOddVsEven	
	
def main():
	
	progname = os.path.basename(sys.argv[0])
	usage = """WARNING:  **PRELIMINARY** program, still heavily under development. 
				Autoboxes globular particles from tomograms.
				Note that self-generated spherical templates generated by this program
				are 'white'; which means you have to provide the tomogram with inverted (or 'white') contrast, and the same goes for any stacks
				provided (specimen particles, gold, carbon and/or background)."""
			
	parser = EMArgumentParser(usage=usage,version=EMANVERSION)
	
	parser.add_argument("--apix",type=float,default=0.0,help="""Default=0.0 (not used). Use this apix value where relevant instead of whatever is in the header of the reference and the particles.""")

	parser.add_argument("--automask",action='store_true',default=False,help="""Applies loose automask at threshold=2.0""")
	
	parser.add_argument("--averager",type=str,default="mean.tomo",help="""Default=mean.tomo. The type of averager used to produce the class average.""")

	parser.add_argument("--clip",type=float,default=0,help="""Default=0 (not used). Size to clip the box to before calculating FSCs. If particle of 64 pixels in diameter are in a 128x128x128 box, it's safe to provide --clip 70 or so""")

	parser.add_argument("--inputeven", type=str, default='',help="""Default=None. The name of the EVEN aligned volume stack after gold-standard SPT refinement. MUST be HDF since volume stack support is required.""")

	parser.add_argument("--inputodd", type=str, default='',help="""Default=None. The name of the ODD aligned volume stack after gold-standard SPT refinement. MUST be HDF since volume stack support is required.""")
	
	parser.add_argument("--mask",action='store_true',default=False,help="""Applies soft mask beyond the radius of the particle assumed to be 1/4 + 0.2*1/4 of the box size.""")

	parser.add_argument("--path",type=str,default='sptbfactor',help="""Default=spt. Directory to store results in. The default is a numbered series of directories containing the prefix 'spt'; for example, spt_02 will be the directory by default if 'spt_01' already exists.""")

	parser.add_argument("--ppid", type=int, help="Set the PID of the parent process, used for cross platform PPID",default=-1)

	parser.add_argument("--runningavg",action='store_true',default=False,help="""Computes running average of particles weighing properly, instead of computing each average (as N grows) from scratch.""")

	parser.add_argument("--step",type=int,default=1,help="""Number of particles to increase from one data point to the next. For example, --step=10 will compute the B-factor averaging 10 particles from the even set and 10 from the odd set; then 20; then 40; etc.""")

	parser.add_argument("--sym", type=str, default='', help="""Default=None (equivalent to c1). Symmetry to impose -choices are: c<n>, d<n>, h<n>, tet, oct, icos""")
	
	parser.add_argument("--verbose", "-v", dest="verbose", action="store", metavar="n",type=int, default=0, help="verbose level [0-9], higner number means higher level of verboseness")
	
	(options, args) = parser.parse_args()	#c:this parses the options or "arguments" listed 
											#c:above so that they're accesible in the form of option.argument; 
											#c:for example, the input for --template would be accesible as options.template
		
	logger = E2init(sys.argv, options.ppid)	#c:this initiates the EMAN2 logger such that the execution
											#of the program with the specified parameters will be logged
											#(written) in the invisible file .eman2log.txt
	
	
	options.averager=parsemodopt(options.averager)
	
	from e2spt_classaverage import sptmakepath
	options = sptmakepath(options,'sptbfactor')

	ne = EMUtil.get_image_count( options.inputeven )
	no = EMUtil.get_image_count( options.inputodd )

	hdr = EMData( options.inputeven, 0, True )
	box = hdr['nx']
	radius = box/4
	
	print "\nradius is", radius
	radius_expanded = radius + math.ceil(0.2*radius)
	
	print "\nradius expanded is", radius_expanded
	
	nfinal = (ne+no)/2
	if ne < nfinal:
		nfinal = ne
	elif no < nfinal:
		nfinal = no
	
	fscareas = []
	fscareasdict={}
	
	
	preve = EMData( options.inputeven, 0 )
	prevo = EMData( options.inputodd, 0 )
	
	avge = preve.copy()
	avgo = prevo.copy()
	
	avge.process_inplace('normalize.edgemean')
	avgo.process_inplace('normalize.edgemean')
	
	for thisn in xrange( 1, nfinal+1, options.step ):
		
		indx = thisn-1
		
		if options.runningavg:
			if indx > 0:
				avge = runningavg( options.inputeven, preve, options, indx )
				avgo = runningavg( options.inputodd, prevo, options, indx )
				
				preve = avge.copy()
				prevo = avge.copy()
		else:
			avge = averagerfunc( options.inputeven, options, thisn )
			avgo = averagerfunc( options.inputodd, options, thisn )
		
		if options.mask:
			avge.process_inplace('mask.soft',{'outer_radius':radius_expanded})
			avgo.process_inplace('mask.soft',{'outer_radius':radius_expanded})
		if options.automask:
			avge.process_inplace('mask.auto3d',{'radius':1,'nmaxseed':10,'nshells':1,'nshellsgauss':10,'threshold':2.0})
			avgo.process_inplace('mask.auto3d',{'radius':1,'nmaxseed':10,'nshells':1,'nshellsgauss':10,'threshold':2.0})

		avge_w = avge.copy()
		avgo_w = avgo.copy()
		if options.sym:
			avge_w.process_inplace('xform.applysym',{'sym':options.sym})
			avgo_w.process_inplace('xform.applysym',{'sym':options.sym})
		
		fscarea = calcfsc( options, avge_w, avgo_w )

		fscareas.append( fscarea )
		fscareasdict.update({indx:fscarea})
		
		f = open( options.path +'/n_vs_fsc.txt','w' )
		fsclines = []
		
		x=0
		sortedfscareasdict = collections.OrderedDict(sorted(fscareasdict.items()))
		
		#for fscarea in fscareas:
		for k in sortedfscareasdict:
			fscareak = sortedfscareasdict[k]
			fscline = str(x) + '\t'+ str(fscareak) + '\n'
			fsclines.append( fscline )
			x+=1
	
		f.writelines( fsclines )
		f.close()
		print "\ndone with fsc %d/%d" %(thisn,nfinal)

	
	
	
	'''	
	ccc
	ccc.tomo.thresh
	ccc.tomo
	fsc.tomo.auto
	'''
	
	return


def averagerfunc(stack,options,n):
	print "\ncomputing average %d, from file %s" %(n,stack)
	
	avgr = Averagers.get( options.averager[0], options.averager[1])
		
	for i in range(n):
		print "\nadded ptcl %d/%d" %(i,n)
		ptcl = EMData( stack, i )
		
		#print "\napix is",ptcl['apix_x']
		avgr.add_image( ptcl )
	
	avg = avgr.finish()
	if avg:
		avg.process_inplace('normalize.edgemean')
		
		return avg
	else:
		print "average failed"
		return


def runningavg(stack,previousavg,options,indx):
	print "\ncomputing running avg %d, from file %s" %(indx,stack)
	
	avgr = Averagers.get( options.averager[0], options.averager[1])
		
	#for i in range(n):
	ptcl = EMData( stack, indx )
	ptcl.process_inplace('normalize.edgemean')	
	
	avgr.add_image( ptcl )
	
	previousavg.process_inplace('normalize.edgemean')
	previousavg.mult(indx)
	avgr.add_image( previousavg )
	
	avg = avgr.finish()
	#if avg:
	avg.process_inplace('normalize.edgemean')
		
	return avg
	#else:
	#	print "average failed"
	#	return

	#return avg

	
def calcfsc( options, img1, img2 ):
	
	img1fsc = img1.copy()
	img2fsc = img2.copy()
	
	apix = img1['apix_x']
	if options.apix:
		apix=options.apix
	
	#if options.clip:
		#img1fsc = clip3D( img1fsc, options.clip )
		#img1fsc.process_inpl
		
	#	img1fsc.write_image(options.path +'/vol4fsc1.hdf',0)
		
	#	img2fsc = clip3D( img2fsc, options.clip )
	#	img2fsc.write_image(options.path +'/vol4fsc2.hdf',0)
		
	fsc = img1fsc.calc_fourier_shell_correlation( img2fsc )
	third = len( fsc )/3
	xaxis = fsc[0:third]
	fsc = fsc[third:2*third]
	saxis = [x/apix for x in xaxis]

	fscfile = options.path + '/tmpfsc.txt'
	Util.save_data( saxis[1], saxis[1]-saxis[0], fsc[1:-1], fscfile )

	f=open(fscfile,'r')
	lines=f.readlines()
	fscarea = sum( [ float(line.split()[-1].replace('\n','')) for line in lines ])
	
	return fscarea
	

	
if '__main__' == __name__:
	main()
	



	