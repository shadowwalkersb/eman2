#!/usr/bin/env python

#
# Author: Steven Ludtke, 02/15/2011 - using code and concepts drawn from Jesus Galaz's scripts
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

from EMAN2 import *
import math
from copy import deepcopy
import os
import sys
import random
from random import choice
from pprint import pprint
from EMAN2db import EMTask

def main():
	progname = os.path.basename(sys.argv[0])
	usage = """prog <output> [options]

	This program produces iterative class-averages akin to those generated by e2classaverage, but for stacks of 3-D Volumes.
	Normal usage is to provide a stack of particle volumes and a classification matrix file defining
	class membership. Members of each class are then iteratively aligned to each other and averaged
	together.  It is also possible to use this program on all of the volumes in a single stack.

	Three preprocessing operations are provided for, mask, normproc and preprocess. They are executed in that order. Each takes
	a generic <processor>:<parm>=<value>:...  string. While you could provide any valid processor for any of these options, if
	the mask processor does not produce a valid mask, then the default normalization will fail. It is recommended that you
	specify the following, unless you really know what you're doing:
	
	--mask=mask.sharp:outer_radius=<safe radius>
	--preprocess=filter.lowpass.gauss:cutoff_freq=<1/resolution in A>
	
	"""
			
	parser = EMArgumentParser(usage=usage,version=EMANVERSION)
	
	parser.add_header(name="caheader", help='Options below this label are specific to e2classaverage3d', title="### e2classaverage3d options ###", default=None, guitype='filebox', row=3, col=0, rowspan=1, colspan=3)
	parser.add_argument("--path",type=str,default=None,help="Path for the refinement, default=auto")
	parser.add_argument("--input", type=str, help="The name of the input volume stack. MUST be HDF or BDB, since volume stack support is required.", default=None, guitype='filebox', row=0, col=0, rowspan=1, colspan=3)
	parser.add_argument("--output", type=str, help="The name of the output class-average stack. MUST be HDF or BDB, since volume stack support is required.", default=None, guitype='strbox', row=2, col=0, rowspan=1, colspan=3)
	parser.add_argument("--oneclass", type=int, help="Create only a single class-average. Specify the class number.",default=None)
	parser.add_argument("--classmx", type=str, help="The name of the classification matrix specifying how particles in 'input' should be grouped. If omitted, all particles will be averaged.", default=None)
	parser.add_argument("--ref", type=str, help="Reference image(s). Used as an initial alignment reference and for final orientation adjustment if present. This is typically the projections that were used for classification.", default=None, guitype='filebox', filecheck=False, row=1, col=0, rowspan=1, colspan=3)
	parser.add_argument("--resultmx",type=str,help="Specify an output image to store the result matrix. This is in the same format as the classification matrix. http://blake.bcm.edu/emanwiki/EMAN2/ClassmxFiles", default=None)
	parser.add_argument("--iter", type=int, help="The number of iterations to perform. Default is 1.", default=1, guitype='intbox', row=5, col=0, rowspan=1, colspan=1)
	parser.add_argument("--savesteps",action="store_true", help="If set, will save the average after each iteration to class_#.hdf. Each class in a separate file. Appends to existing files.",default=False, guitype='boolbox', row=4, col=0, rowspan=1, colspan=1)
	parser.add_argument("--saveali",action="store_true", help="If set, will save the aligned particle volumes in class_ptcl.hdf. Overwrites existing file.",default=False, guitype='boolbox', row=4, col=1, rowspan=1, colspan=1)
	parser.add_argument("--saveallalign",action="store_true", help="If set, will save the alignment parameters after each iteration",default=False, guitype='boolbox', row=4, col=2, rowspan=1, colspan=1)
	parser.add_argument("--sym", dest = "sym", default=None, help = "Symmetry to impose - choices are: c<n>, d<n>, h<n>, tet, oct, icos", guitype='symbox', row=6, col=1, rowspan=1, colspan=2)
	parser.add_argument("--mask",type=str,help="Mask processor applied to particles before alignment. Default is mask.sharp:outer_radius=-2", default="mask.sharp:outer_radius=-2", guitype='comboparambox', choicelist='re_filter_list(dump_processors_list(),\'mask\')', row=9, col=0, rowspan=1, colspan=3)
	parser.add_argument("--normproc",type=str,help="Normalization processor applied to particles before alignment. Default is to use normalize.mask. If normalize.mask is used, results of the mask option will be passed in automatically. If you want to turn this option off specify \'None\'", default="normalize.mask")
	parser.add_argument("--preprocess",type=str,help="A processor (as in e2proc3d.py) to be applied to each volume prior to alignment. Not applied to aligned particles before averaging.",default=None, guitype='comboparambox', choicelist='re_filter_list(dump_processors_list(),\'filter\')', row=8, col=0, rowspan=1, colspan=3)
	parser.add_argument("--ncoarse", type=int, help="Deprecated", default=None)
	parser.add_argument("--npeakstorefine", type=int, help="The number of best coarse alignments to refine in search of the best final alignment. Default=4.", default=4, guitype='intbox', row=6, col=0, rowspan=1, colspan=1)
	parser.add_argument("--align",type=str,help="This is the aligner used to align particles to the previous class average. Default is rotate_translate_3d:search=10:delta=15:dphi=15", default="rotate_translate_3d:search=10:delta=15:dphi=15", guitype='comboparambox', choicelist='re_filter_list(dump_aligners_list(),\'3d\')', row=10, col=0, rowspan=1, colspan=3)
	parser.add_argument("--aligncmp",type=str,help="The comparator used for the --align aligner. Default is the internal tomographic ccc. Do not specify unless you need to use another specific aligner.",default="ccc.tomo")
	parser.add_argument("--ralign",type=str,help="This is the second stage aligner used to refine the first alignment. Default is refine.3d, specify 'None' to disable", default="refine_3d", guitype='comboparambox', choicelist='re_filter_list(dump_aligners_list(),\'refine.*3d\')', row=11, col=0, rowspan=1, colspan=3)
	parser.add_argument("--raligncmp",type=str,help="The comparator used by the second stage aligner. Default is the internal tomographic ccc",default="ccc.tomo")
	parser.add_argument("--averager",type=str,help="The type of averager used to produce the class average. Default=mean",default="mean")
	#parser.add_argument("--cmp",type=str,dest="cmpr",help="The comparitor used to generate quality scores for the purpose of particle exclusion in classes, strongly linked to the keep argument.", default="ccc")
	parser.add_argument("--keep",type=float,help="The fraction of particles to keep in each class.",default=1.0)
	
	parser.add_argument("--groups",type=int,help="This parameter is EXPERIMENTAL. It's the number of final averages you want from the set after ONE iteration of alignment. Particles will be separated in groups based on their correlation to the reference",default=0)

	parser.add_argument("--keepsig", action="store_true", help="Causes the keep argument to be interpreted in standard deviations.",default=False)
	parser.add_argument("--postprocess",type=str,help="A processor to be applied to the volume after averaging the raw volumes, before subsequent iterations begin.",default=None, guitype='comboparambox', choicelist='re_filter_list(dump_processors_list(),\'filter\')', row=12, col=0, rowspan=1, colspan=3)
	
	#parser.add_argument('--reverse_contrast', action="store_true", default=False, help=""" This multiplies the input particles by -1. Remember that EMAN2 **MUST** work with 'white protein' """)
	
	parser.add_argument("--shrink", type=int,default=1,help="Optionally shrink the input volumes by an integer amount for coarse alignment.", guitype='intbox', row=5, col=1, rowspan=1, colspan=1)
	parser.add_argument("--shrinkrefine", type=int,default=1,help="Optionally shrink the input volumes by an integer amount for refine alignment.", guitype='intbox', row=5, col=2, rowspan=1, colspan=1)
	#parser.add_argument("--automask",action="store_true",help="Applies a 3-D automask before centering. Can help with negative stain data, and other cases where centering is poor.")
	#parser.add_argument("--resample",action="store_true",help="If set, will perform bootstrap resampling on the particle data for use in making variance maps.",default=False)
	#parser.add_argument("--odd", default=False, help="Used by EMAN2 when running eotests. Includes only odd numbered particles in class averages.", action="store_true")
	#parser.add_argument("--even", default=False, help="Used by EMAN2 when running eotests. Includes only even numbered particles in class averages.", action="store_true")
	parser.add_argument("--parallel",  help="Parallelism. See http://blake.bcm.edu/emanwiki/EMAN2/Parallel", default="thread:1", guitype='strbox', row=13, col=0, rowspan=1, colspan=3)
	parser.add_argument("--ppid", type=int, help="Set the PID of the parent process, used for cross platform PPID",default=-1)
	parser.add_argument("--verbose", "-v", dest="verbose", action="store", metavar="n",type=int, default=0, help="verbose level [0-9], higner number means higher level of verboseness")

	(options, args) = parser.parse_args()

	if options.ncoarse!=None :
		print "The ncoarse option has been renamed npeakstorefine"
		sys.exit(1)
	
	if options.align: 
		options.align=parsemodopt(options.align)
	if options.ralign: 
		options.ralign=parsemodopt(options.ralign)
	
	if options.aligncmp: 
		options.aligncmp=parsemodopt(options.aligncmp)
	if options.raligncmp: 
		options.raligncmp=parsemodopt(options.raligncmp)
	
	if options.averager: 
		options.averager=parsemodopt(options.averager)

	if options.normproc: 
		options.normproc=parsemodopt(options.normproc)
	if options.mask: 
		options.mask=parsemodopt(options.mask)
	if options.preprocess: 
		options.preprocess=parsemodopt(options.preprocess)
	if options.postprocess: 
		options.postprocess=parsemodopt(options.postprocess)

#	if options.cmpr: 
#		options.cmpr=parsemodopt(options.cmpr)

	if options.resultmx : 
		print "Sorry, resultmx not implemented yet"
	if options.resultmx!=None: 
		options.storebad=True
		
	if options.path and ("/" in options.path or "#" in options.path) :
		print "Path specifier should be the name of a subdirectory to use in the current directory. Neither '/' or '#' can be included. "
		sys.exit(1)
		
	if options.path and options.path[:4].lower()!="bdb:": 
		options.path="bdb:"+options.path
	if not options.path: 
		options.path="bdb:"+numbered_path("job3d",True)
	
	hdr = EMData(options.input,0,True)
	nx = hdr["nx"]
	ny = hdr["ny"]
	nz = hdr["nz"]
	if nx!=ny or ny!=nz :
		print "ERROR, input volumes are not cubes"
		sys.exit(1)
	
	if options.ref!=None :
		hdr = EMData(options.ref,0,True)
		if hdr["nx"]!=nx or hdr["ny"]!=ny or hdr["nz"]!=nz : 
			print "Error, ref volume not same size as input volumes"
			sys.exit(1)
			
	if '.' not in options.output:					#jesus
		print "Error in output name. It must end in a valid format, like '.hdf'; make sure you didn't mistake a comma for a dot"
		sys.exit(1)
		
	logger = E2init(sys.argv, options.ppid)
	
	try: 
		classmx = EMData.read_images(options.classmx)		# we keep the entire classification matrix in memory, since we need to update it in most cases
		ncls = int(classmx[0]["maximum"])
	except:
		ncls=1
		#if options.resultmx!=None :
			#print "resultmx can only be specified in conjunction with a valid classmx input."
			#sys.exit(1)

	nptcl=EMUtil.get_image_count(options.input)
	if nptcl<1 : 
		print "ERROR : at least 1 particle required in input stack"
		sys.exit(1)
		
	if nptcl==1:
		if options.iter>1 :
			print "Error: makes no sense to have iter>1 with one particle"
			sys.exit(1)
		
		if options.keepsig or options.keep!=1.0 :
			print "Error: do not use --keepsig with one particle, also keep should be 1.0 if specified"
			sys.exit(1)

	# Initialize parallelism if being used
	if options.parallel :
		from EMAN2PAR import EMTaskCustomer
		etc=EMTaskCustomer(options.parallel)
		pclist=[options.input]
		
		if options.ref: 
			pclist.append(options.ref)
		etc.precache(pclist)

	#########################################
	# This is where the actual class-averaging process begins
	#########################################

	# outer loop over classes, ic=class number
	for ic in range(ncls):
		if ncls==1: 
			ptcls=range(nptcl)				# start with a list of particle numbers in this class
		else: 
			ptcls=classmx_ptcls(classmx,ic)			# This gets the list from the classmx
		
		if options.verbose and ncls>1 : print "###### Beggining class %d(%d)/%d"%(ic+1,ic,ncls)
		
		# prepare a reference either by reading from disk or bootstrapping
		if options.ref: 
			ref=EMData(options.ref,ic)
		else :
			if nptcl==1 : 
				print "Error: More than 1 particle required if no reference specified"
				sys.exit(1)
			
			# we need to make an initial reference. Due to the parallelism scheme we're using in 3-D and the slow speed of the
			# individual alignments we use a slightly different strategy than in 2-D. We make a binary tree from the first 2^n particles and
			# compute pairwise alignments until we get an average out. 
		
			nseed=2**int(floor(log(len(ptcls),2)))	# we stick with powers of 2 for this to make the tree easier to collapse
			if nseed>64 : 
				nseed=64
				print "Limiting seeding to the first 64 images"

			nseediter=int(log(nseed,2))			# number of iterations we'll need
			if options.verbose: 
				print "Seedtree to produce initial reference. Using %d particles in a %d level tree"%(nseed,nseediter)
			
			# We copy the particles for this class into bdb:seedtree_0
			for i,j in enumerate(ptcls[:nseed]):
				EMData(options.input,j).write_image("%s#seedtree_0"%options.path,i)
				
			# Outer loop covering levels in the converging binary tree
			for i in range(nseediter):
				infile="%s#seedtree_%d"%(options.path,i)
				outfile="%s#seedtree_%d"%(options.path,i+1)
			
				tasks=[]
				# loop over volumes in the current level
				for j in range(0,nseed/(2**i),2):
					# Unfortunately this tree structure limits the parallelism to the number of pairs at the current level :^(
					task=Align3DTask(["cache",infile,j],["cache",infile,j+1],j/2,"Seed Tree pair %d at level %d"%(j/2,i),options.mask,options.normproc,options.preprocess,
						options.npeakstorefine,options.align,options.aligncmp,options.ralign,options.raligncmp,options.shrink,options.shrinkrefine,options.verbose-1)
					tasks.append(task)

				# Start the alignments for this level
				tids=etc.send_tasks(tasks)
				if options.verbose: 
					print "%d tasks queued in seedtree level %d"%(len(tids),i) 

				# Wait for alignments to finish and get results
				results=get_results(etc,tids,options.verbose)

				if options.verbose>2 : 
					print "Results:"
					pprint(results)
				
				
				make_average_pairs(infile,outfile,results,options.averager,options.mask,options.normproc,options.postprocess)
				
			ref=EMData(outfile,0)		# result of the last iteration
			
			if options.savesteps :
				ref.write_image("%s#class_%02d"%(options.path,ic),-1)
		
		# Now we iteratively refine a single class
		for it in range(options.iter):
			# In 2-D class-averaging, each alignment is fast, so we send each node a class-average to make
			# in 3-D each alignment is very slow, so we use a single ptcl->ref alignment as a task
			tasks=[]
			for p in ptcls:
				task=Align3DTask(ref,["cache",options.input,p],p,"Ptcl %d in iter %d"%(p,it),options.mask,options.normproc,options.preprocess,
					options.npeakstorefine,options.align,options.aligncmp,options.ralign,options.raligncmp,options.shrink,options.shrinkrefine,options.verbose-1)
				tasks.append(task)
			
			# start the alignments running
			tids=etc.send_tasks(tasks)
			if options.verbose: 
				print "%d tasks queued in class %d iteration %d"%(len(tids),ic,it) 

			# Wait for alignments to finish and get results
			results=get_results(etc,tids,options.verbose)

			if options.verbose>2 : 
				print "Results:"
				pprint(results)
			
			ref=make_average(options.input,options.path,results,options.averager,options.saveali,options.saveallalign,options.keep,options.keepsig,options.groups,options.verbose)		# the reference for the next iteration
			
			#postprocess(ref,options.mask,options.normproc,options.postprocess) #jesus
			
			if options.groups > 1:
				for i in range(len(ref)):
					refc=ref[i]
					postprocess(refc,None,options.normproc,options.postprocess) #jesus
					
					if options.savesteps:
						refc.write_image("%s/class_%02d"%(options.path,i),it)			
			else:
				if type(ref) is list:
					if len(ref) > 1:
						print "Looks like you have multiple references!!"
						ref=ref[0]
				postprocess(ref,None,options.normproc,options.postprocess) #jesus
				if options.savesteps:
						ref.write_image("%s/class_%02d"%(options.path,ic),it)

			#sys.exit()

			if options.sym!=None : 
				if options.verbose: 
					print "Apply ",options.sym," symmetry"
				symmetrize(ref,options.sym)
			

		if options.verbose: 
			print "Preparing final average"
		# new average

		ref=make_average(options.input,options.path,results,options.averager,options.saveali,options.saveallalign,options.keep,options.keepsig,options.groups,options.verbose)		# the reference for the next iteration
		
		#if options.postprocess!=None : 
			#ref.process_inplace(options.postprocess[0],options.postprocess[1])     #jesus - The post process should be applied to the refinment averages. The last one is identical
												#to the output final average, so no need to apply it to ref. Plus, you ALWAYS want to have a copy
		if type(ref) is list:
			print "You hvae a LIST of references"
			if len(ref) > 1:
				print "The first one will be picked"
				ref=ref[0]
												#of the average of the raw particles, completley raw
		ref['origin_x']=0
		ref['origin_y']=0		#jesus - The origin needs to be reset to ZERO to avoid display issues in Chimera
		ref['origin_z']=0
		#output_pathname=
		ref.write_image(options.output,ic)
	E2end(logger)


def postprocess(img,optmask,optnormproc,optpostprocess):
	"""Postprocesses a volume in-place"""
	
	img.process_inplace("xform.centerofmass")
	
	# Make a mask, use it to normalize (optionally), then apply it 
	mask=EMData(img["nx"],img["ny"],img["nz"])
	mask.to_one()
	if optmask != None:
		mask.process_inplace(optmask[0],optmask[1])
		
	# normalize
	if optnormproc != None:
		if optnormproc[0]=="normalize.mask" : optnormproc[1]["mask"]=mask
		img.process_inplace(optnormproc[0],optnormproc[1])

	img.mult(mask)
	
	# Postprocess filter
	if optpostprocess!=None : 
		img.process_inplace(optpostprocess[0],optpostprocess[1])


def make_average(ptcl_file,path,align_parms,averager,saveali,saveallalign,keep,keepsig,groups,verbose=1):			#jesus - added the groups parameter
	"""Will take a set of alignments and an input particle stack filename and produce a new class-average.
	Particles may be excluded based on the keep and keepsig parameters. If keepsig is not set, then keep represents
	an absolute fraction of particles to keep (0-1). Otherwise it represents a sigma multiplier akin to e2classaverage.py"""
	
	
	
	if groups > 1:
		#print "QUIT! Becuase the groups are", groups
		#print "And their types are", type(groups)
		#sys.exit()
		print "This is an example of where I'm getting the score from", align_parms[0][0]						#jesus
		val=[p[0]["score"] for p in align_parms]
		
		val.sort()
		threshs = []
		guinea_particles=[]
		print "The number of groups you have requested is", groups
		for i in range(groups - 1):
			threshs.append(val[int((i+1)*(1.0/groups)*len(align_parms)) -1])
			guinea_particles.append(int((i+1)*(1.0/groups)*len(align_parms)) -1)
		print "Therefore, based on the size of the set, the coefficients that will work as thresholds are", threshs	
		print "While the guinea particles where these came from were", guinea_particles
		print "Out of a total of these many particles", len(align_parms)
		print "Therefor each group will contain approximately these many particles", len(align_parms)/groups
	
		threshs.sort()
		
		#avgr=Averagers.get(averager[0], averager[1])
		
		groupslist=[]
		includedlist=[]
		for i in range(groups):
			groupslist.append([])
			includedlist.append([])
		
		for i,ptcl_parms in enumerate(align_parms):
			ptcl=EMData(ptcl_file,i)
			ptcl.process_inplace("xform",{"transform":ptcl_parms[0]["xform.align3d"]})

			if ptcl_parms[0]["score"] > threshs[-1]: 
				#avgr.add_image(ptcl)
				groupslist[-1].append(ptcl)
				includedlist[-1].append(i)			
				print "Particle %d assigned to last group!" %(i)
				print "The threshold criteria was %f, and the particles cc score was %f" %(threshs[-1], ptcl_parms[0]["score"])
				
			elif ptcl_parms[0]["score"] < threshs[0]: 
				groupslist[0].append(ptcl)
				includedlist[0].append(i)
				print "Particle %d assigned to first group!" %(i)
				print "The threshold criteria was %f, and the particles cc score was %f" %(threshs[0], ptcl_parms[0]["score"])
			
			else:
				for kk in range(len(threshs)-1):
					if ptcl_parms[0]["score"] > threshs[kk] and ptcl_parms[0]["score"] < threshs[kk+1]:
						groupslist[kk+1].append(ptcl)
						includedlist[kk+1].append(i)
						print "Particle %d assigned to group number %d!" %(i,kk+1)
						print "The threshold criteria was %f, and the particles cc score was %f" %(threshs[kk+1], ptcl_parms[0]["score"])

			#if saveali:
			#	ptcl['origin_x'] = 0
			#	ptcl['origin_y'] = 0		
			#	ptcl['origin_z'] = 0
			#	
			#	print "I will write the particle with the origin set to 0. Its type is", type(ptcl)
			#	ptcl.write_image("bdb:class_ptcl",i)
		
		ret=[]
		
		for i in range(len(groupslist)):
			avgr=Averagers.get(averager[0], averager[1])
			
			for j in range(len(groupslist[i])):
				avgr.add_image(groupslist[i][j])
				
				if saveali:
					groupslist[i][j]['origin_x'] = 0
					groupslist[i][j]['origin_y'] = 0		# jesus - the origin needs to be reset to ZERO to avoid display issues in Chimera
					groupslist[i][j]['origin_z'] = 0
					classname=path+"/class_" + str(i).zfill(len(str(len(groupslist)))) + "_ptcl"
					groupslist[i][j].write_image(classname,j)
					
			avg=avgr.finish()
			avg["class_ptcl_idxs"]=includedlist[i]
			avg["class_ptcl_src"]=ptcl_file
			
			ret.append(avg)
		
		#sys.exit()
		return ret

	else:
		if keepsig:
			# inefficient memory-wise
			val=sum([p[0]["score"] for p in align_parms])
			val2=sum([p[0]["score"]**2 for p in align_parms])

			mean=val/len(align_parms)
			sig=sqrt(val2/len(align_parms)-mean*mean)
			thresh=mean+sig*keep
			if verbose: 
				print "Keep threshold : %f (mean=%f  sigma=%f)"%(thresh,mean,sig)

		if keep:
			val=[p[0]["score"] for p in align_parms]
			val.sort()
			thresh=val[int(keep*len(align_parms))-1]
			if verbose: 
				print "Keep threshold : %f (min=%f  max=%f)"%(thresh,val[0],val[-1])

		avgr=Averagers.get(averager[0], averager[1])
		included=[]
		
		
		print "The path is", path
		#sys.exit()

		for i,ptcl_parms in enumerate(align_parms):
			ptcl=EMData(ptcl_file,i)
			ptcl.process_inplace("xform",{"transform":ptcl_parms[0]["xform.align3d"]})

			if ptcl_parms[0]["score"]<=thresh: 
				avgr.add_image(ptcl)
				included.append(i)

			if saveali:
				ptcl['origin_x'] = 0
				ptcl['origin_y'] = 0		# jesus - the origin needs to be reset to ZERO to avoid display issues in Chimera
				ptcl['origin_z'] = 0
				classname=path+"/class_ptcl"
				#print "The class name is", classname
				#sys.exit()
				ptcl.write_image(classname,i)

		if verbose: 
			print "Kept %d / %d particles in average"%(len(included),len(align_parms))

		ret=avgr.finish()
		ret["class_ptcl_idxs"]=included
		ret["class_ptcl_src"]=ptcl_file

		return ret
		

def make_average_pairs(ptcl_file,outfile,align_parms,averager,optmask,optnormproc,optpostprocess):
	"""Will take a set of alignments and an input particle stack filename and produce a new set of class-averages over pairs"""
	
	for i,ptcl_parms in enumerate(align_parms):
		ptcl0=EMData(ptcl_file,i*2)
		ptcl1=EMData(ptcl_file,i*2+1)
		ptcl1.process_inplace("xform",{"transform":ptcl_parms[0]["xform.align3d"]})

		# While this is only 2 images, we still use the averager in case something clever is going on
		avgr=Averagers.get(averager[0], averager[1])
		avgr.add_image(ptcl0)
		avgr.add_image(ptcl1)
		
		avg=avgr.finish()
		postprocess(avg,optmask,optnormproc,optpostprocess)		# we treat these intermediate averages just like the final average
		avg.write_image(outfile,i)


def symmetrize(ptcl,sym):
	"Impose symmetry in the standard orientation in-place. Does not reorient particle before symmetrization"
	xf = Transform()
	xf.to_identity()
	nsym=xf.get_nsym(sym)
	orig=ptcl.copy()
	for i in range(1,nsym):
		dc=orig.copy()
		dc.transform(xf.get_sym(sym,i))
		ptcl.add(dc)
	ptcl.mult(1.0/nsym)	
	
	return

def get_results(etc,tids,verbose):
	"""This will get results for a list of submitted tasks. Won't return until it has all requested results.
	aside from the use of options["ptcl"] this is fairly generalizable code. """
	
	# wait for them to finish and get the results
	# results for each will just be a list of (qual,Transform) pairs
	results=[0]*len(tids)		# storage for results
	ncomplete=0
	tidsleft=tids[:]
	while 1:
		time.sleep(5)
		proglist=etc.check_task(tidsleft)
		nwait=0
		for i,prog in enumerate(proglist):
			if prog==-1 : nwait+=1
			if prog==100 :
				r=etc.get_results(tidsleft[i])		# results for a completed task
				ptcl=r[0].options["ptcl"]			# get the particle number from the task rather than trying to work back to it
				results[ptcl]=r[1]["final"]			# this will be a list of (qual,Transform)
				ncomplete+=1
		
		tidsleft=[j for i,j in enumerate(tidsleft) if proglist[i]!=100]		# remove any completed tasks from the list we ask about
		if verbose:
			print "  %d tasks, %d complete, %d waiting to start        \r"%(len(tids),ncomplete,nwait)
			sys.stdout.flush()
	
		if len(tidsleft)==0: break
		
	return results

class Align3DTask(EMTask):
	"""This is a task object for the parallelism system. It is responsible for aligning one 3-D volume to another, with a variety of options"""

	def __init__(self,fixedimage,image,ptcl,label,mask,normproc,preprocess,npeakstorefine,align,aligncmp,ralign,raligncmp,shrink,shrinkrefine,verbose):
		"""fixedimage and image may be actual EMData objects, or ["cache",path,number]
	label is a descriptive string, not actually used in processing
	ptcl is not used in executing the task, but is for reference
	other parameters match command-line options from e2classaverage3d.py
	Rather than being a string specifying an aligner, 'align' may be passed in as a Transform object, representing a starting orientation for refinement"""
		data={}
		data={"fixedimage":fixedimage,"image":image}
		EMTask.__init__(self,"ClassAv3d",data,{},"")
		self.ppid = os.getpid()

		self.options={"ptcl":ptcl,"label":label,"mask":mask,"normproc":normproc,"preprocess":preprocess,"npeakstorefine":npeakstorefine,"align":align,"aligncmp":aligncmp,"ralign":ralign,"raligncmp":raligncmp,"shrink":shrink,"shrinkrefine":shrinkrefine,"verbose":verbose}
	
	def execute(self,callback=None):
		"""This aligns one volume to a reference and returns the alignment parameters"""
		options=self.options
		if options["verbose"]: 
			print "Aligning ",options["label"]

		if isinstance(self.data["fixedimage"],EMData) :
			fixedimage=self.data["fixedimage"]
		else: 
			fixedimage=EMData(self.data["fixedimage"][1],self.data["fixedimage"][2])
		
		if isinstance(self.data["image"],EMData) :
			image=self.data["image"]
		else: 
			image=EMData(self.data["image"][1],self.data["image"][2])
		
		# Preprocessing currently applied to both volumes. Often 'fixedimage' will be a reference, though, 
		# so may need to rethink whether it should be treated identically. Similar issues in 2-D single particle
		# refinement ... handled differently at the moment
		
		# Make the mask first, use it to normalize (optionally), then apply it 
		mask=EMData(image["nx"],image["ny"],image["nz"])
		mask.to_one()
		if options["mask"] != None:
			print "This is the mask I will apply: mask.process_inplace(%s,%s)" %(options["mask"][0],options["mask"][1]) 
			mask.process_inplace(options["mask"][0],options["mask"][1])
		
		# normalize
		if options["normproc"] != None:
			if options["normproc"][0]=="normalize.mask" : options["normproc"][1]["mask"]=mask
			fixedimage.process_inplace(options["normproc"][0],options["normproc"][1])
			image.process_inplace(options["normproc"][0],options["normproc"][1])
		
		fixedimage.mult(mask)
		image.mult(mask)
		
		# preprocess
		if options["preprocess"] != None:
			fixedimage.process_inplace(options["preprocess"][0],options["preprocess"][1])
			image.process_inplace(options["preprocess"][0],options["preprocess"][1])
		
		# Shrinking both for initial alignment and reference
		if options["shrink"]!=None and options["shrink"]>1 :
			sfixedimage=fixedimage.process("math.meanshrink",{"n":options["shrink"]})
			simage=image.process("math.meanshrink",{"n":options["shrink"]})
		else :
			sfixedimage=fixedimage
			simage=image
			
		if options["shrinkrefine"]!=None and options["shrinkrefine"]>1 :
			if options["shrinkrefine"]==options["shrink"] :
				s2fixedimage=sfixedimage
				s2image=simage
			else :
				s2fixedimage=fixedimage.process("math.meanshrink",{"n":options["shrinkrefine"]})
				s2image=image.process("math.meanshrink",{"n":options["shrinkrefine"]})
		else :
			s2fixedimage=fixedimage
			s2image=image
			

		if options["verbose"]: 
			print "Align size %d,  Refine Align size %d"%(sfixedimage["nx"],s2fixedimage["nx"])

		# If a Transform was passed in, we skip coarse alignment
		if isinstance(options["align"],Transform):
			bestcoarse=[{"score":1.0,"xform.align3d":options["align"]}]
			if options["shrinkrefine"]>1: 
				bestcoarse[0]["xform.align3d"].set_trans(bestcoarse[0]["xform.align3d"].get_trans()/float(options["shrinkrefine"]))
		
		# this is the default behavior, seed orientations come from coarse alignment
		else:
			# returns an ordered vector of Dicts of length options.npeakstorefine. The Dicts in the vector have keys "score" and "xform.align3d"
			bestcoarse=simage.xform_align_nbest(options["align"][0],sfixedimage,options["align"][1],options["npeakstorefine"],options["aligncmp"][0],options["aligncmp"][1])
			scaletrans=options["shrink"]/float(options["shrinkrefine"])
			if scaletrans!=1.0:
				for c in bestcoarse:
					c["xform.align3d"].set_trans(c["xform.align3d"].get_trans()*scaletrans)

		# verbose printout
		if options["verbose"]>1 :
			for i,j in enumerate(bestcoarse): 
				print "coarse %d. %1.5g\t%s"%(i,j["score"],str(j["xform.align3d"]))

		if options["ralign"]!=None :
			# Now loop over the individual peaks and refine each
			bestfinal=[]
			for bc in bestcoarse:
				options["ralign"][1]["xform.align3d"]=bc["xform.align3d"]
				ali=s2image.align(options["ralign"][0],s2fixedimage,options["ralign"][1],options["raligncmp"][0],options["raligncmp"][1])
				
				try: 
					bestfinal.append({"score":ali["score"],"xform.align3d":ali["xform.align3d"],"coarse":bc})
				except:
					bestfinal.append({"xform.align3d":bc["xform.align3d"],"score":1.0e10,"coarse":bc})

			if options["shrinkrefine"]>1 :
				for c in bestfinal:
					c["xform.align3d"].set_trans(c["xform.align3d"].get_trans()*float(options["shrinkrefine"]))

			# verbose printout of fine refinement
			if options["verbose"]>1 :
				for i,j in enumerate(bestfinal): 
					print "fine %d. %1.5g\t%s"%(i,j["score"],str(j["xform.align3d"]))

		else: 
			bestfinal=bestcoarse
		
		#bestfinal.sort()	
		from operator import itemgetter						#jesus - if you just sort 'bestfinal' it will be sorted based on the 'coarse' key in the dictionaries of the list
											#because they come before the 'score' key of the dictionary (alphabetically)
		bestfinal = sorted(bestfinal, key=itemgetter('score'))

		print "\n$$$$\n$$$$\n$$$$\n$$$$\n$$$$\n$$$$The best peaks sorted are"	#confirm the peaks are adequately sorted
		for i in bestfinal:
			print i
		
		if bestfinal[0]["score"] == 1.0e10 :
			print "Error: all refine alignments failed for %s. May need to consider altering filter/shrink parameters. Using coarse alignment, but results are likely invalid."%self.options["label"]
		
		if options["verbose"]: 
			print "Best %1.5g\t %s"%(bestfinal[0]["score"],str(bestfinal[0]["xform.align3d"]))

		if options["verbose"]: 
			print "Done aligning ",options["label"]
		
		return {"final":bestfinal,"coarse":bestcoarse}


def classmx_ptcls(classmx,n):
	"""Scans a classmx file to determine which images are in a specific class. classmx may be a filename or an EMData object.
	returns a list of integers"""
	
	if isinstance(classmx,str) : classmx=EMData(classmx,0)
	
	plist=[i.y for i in classmx.find_pixels_with_value(float(n))]
	
	return plist


	
if __name__ == "__main__":
    main()
