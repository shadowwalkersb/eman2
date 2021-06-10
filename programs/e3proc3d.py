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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  2111-1307 USA
#
from past.utils import old_div
from EMAN2 import *
from eman.proc import parse_list_arg
import sys
from math import *
import os.path
from time import time
from numpy import arange
import traceback
from collections import defaultdict


def FragmentizeType(s):
	par = s.partition(":")
	# par = ast.literal_eval(s)
	print("par:", par)
	# par[0] = int(par[0])
	# print(type(par[0]))
	# print(type(par[2]))

	result = int(float(par[0])), float(par[2])
	# traceback.print_exc()
	# try:
	# 	result = int(par[0]), float(par[2])
	# except ValueError:
	# 	raise ValueError('ERROR: fragmentize requires <N>:<threshold>')
	# except TypeError:
	# 	raise TypeError('ERROR: fragmentize requires <N>:<threshold>')
	# except:
	# 	traceback.print_exc()
		# raise Exception("fffff").with_traceback()
	# if not (isinstance(par[0], int) and isinstance(par[2], float)):
	# 	raise argparse.ArgumentTypeError("specify N:thr!")

	# return int(par[0]), float(par[1])
	return int(float(par[0])), float(par[2])


def OriginType(s):
	result = ast.literal_eval(s)

	if len(result) != 3:
		raise argparse.ArgumentTypeError("specify origin_x,origin_y,origin_z!")

	return float(result[0]), float(result[1]), int(result[2])


def AlignctodType(s):
	result = ast.literal_eval(s)

	if s[0][0].lower() != "d":
		raise argparse.ArgumentTypeError("specify D symmetry as alignctod!")

	return s


def ClipType(s):
	result = ast.literal_eval(s)

	if len(result) != 1 and len(result) != 3 and len(result) != 6:
		raise argparse.ArgumentTypeError("clip option takes 1, 3 or 6 arguments. --clip=x[,y,z[,xc,yc,zc]]!")

	return result


def FftclipType(s):
	result = ast.literal_eval(s)

	if len(result) != 3:
		raise argparse.ArgumentTypeError("fftclip option takes either 3 arguments. --fftclip=x,y,z!")

	return result


def test_tomoprep(): pass  # depends on outfile, need to add dependency check ???
def test_process(): pass
def test_align(): pass  # depends on alignref, need to add dependency check


#parse_file() will read the input image file and return a list of EMData() object
def parse_infile(infile, first, last, step, apix=None):
	if infile[0] == ":":
		parm=infile.split(":")
		if len(parm) == 4: parm.append(0)
		if len(parm) != 5:
			print("Error: please specify ':X:Y:Z:fillval' to create a new volume")
			sys.exit(1)

		ret=EMData(int(parm[1]),int(parm[2]),int(parm[3]))
		ret.to_value(float(parm[4]))
		return [ret]

	nimg = EMUtil.get_image_count(infile)

	if nimg > 1:
		d = EMData(infile,nimg-1)    # we read the last image, since it should always exist

		x = d.get_xsize()
		y = d.get_ysize()
		z = d.get_zsize()

		apixdata = d['apix_x']
		if not apix:
			apix = apixdata

		if z == 1:
			print("the images are 2D - I will now make a 3D image out of the 2D images")
			data = []
			return_data = EMData()
			return_data.set_size(x, y, nimg)
			for i in range(0, nimg):
				d.read_image(infile, i)
				return_data.insert_clip(d, (0, 0, i))
			if apix:
				return_data['apix_x']=apix
				return_data['apix_y']=apix
				return_data['apix_z']=apix
			data.append(return_data)
			return data
		else:
			print("the image is a 3D stack - I will process images from %d to %d" % (first, last))
			data = []

			for i in range(first, last+1, step):
				d = EMData(infile,i,True)    # header only

				if not first - last:
					d = EMData(infile,i)    # header only

				data.append(d)
			return data
	else: return [EMData(infile,0)]


def main():
	description = """
	Generic 3-D image processing and file format conversion program.
	All EMAN2 recognized file formats accepted (see Wiki for list).

	To create a new image, rather than reading from a file, specify ':<nx>:<ny>:<nz>:<value>'
	as an input filename.

	Examples:

	Convert MRC format to HDF format:
	e2proc3d.py test.mrc test.hdf

	Apply a 10 A low-pass filter to a volume and write output to a new file:
	e2proc3d.py threed.hdf threed.filt.hdf --process=filter.lowpass.gauss:cutoff_freq=0.1

	Extract a reconstruction from a refinement directory as an HDF file usable with Chimera:
	e2proc3d.py bdb:refine_02#threed_filt_04 map_02_04.hdf

	Create a new 64x64x64 volume, initialize it as 1, then apply a hard spherical mask to 0:
	e2proc3d.py :64:64:64:1 myvol.hdf --process mask.sharp:outer_radius=25

	'e2help.py processors -v 2' for a detailed list of available procesors

"""
	parser = EMArgumentParser(description=description, allow_abbrev=False)

	parser.add_argument("--add", metavar="f", type=float, help="Adds a constant 'f' to the densities")
	parser.add_argument("--addfile", type=str, action="append", help="Adds the volume to another volume of identical size")
	parser.add_argument("--align", metavar="aligner_name:param1=value1:param2=value2", type=str, action="append", help="Align input map to reference specified with --alignref. As with processors, a sequence of aligners is permitted")
	parser.add_argument("--alignctod", type=parse_list_arg, action="append", help="Rotates a map already aligned for C symmetry so the best 2-fold is positioned for specified D symmetry. Does not impose specified symmetry.")
	parser.add_argument("--alignref", metavar="filename", type=str, default=None, help="Alignment reference volume. May only be specified once.")
	parser.add_argument("--apix", type=float, default=None, help="Default=None (not used). A/pixel for S scaling. Also sets/resets the apix of an image to this value.")
	parser.add_argument("--append", action="store_true", help="Append output image, i.e., do not write inplace.")
	parser.add_argument("--average", action="store_true", help="Computes the average of a stack of 3D volumes")
	parser.add_argument("--avg_byxf", action="store_true", help="Transform each volume by xform.align3d in its header before computing the average. Only used in --average mode.")
	parser.add_argument("--averager", type=str, default="mean", help="Averager used for --average and --sym options")

	parser.add_argument("--calcfsc", type=str, metavar="with input", help="Calculate a FSC curve between two models. Output is a txt file. This option is the name of the second volume.")
	parser.add_argument("--calcsf", type=str, metavar="outputfile", help="Calculate a radial structure factor. Must specify apix.")
	parser.add_argument("--calcradial", type=int,default=-1,help="Calculate the radial density by shell. Output file becomes a text file. 0 - mean amp, 2 - min, 3 - max, 4 - sigma")
	parser.add_argument("--clip", metavar="x[,y,z[,xc,yc,zc]]", type=parse_list_arg([int],[int,int,int],[int,int,int,int,int,int]), help="Make the output have this size by padding/clipping. 1, 3 or 6 arguments. ")
	parser.add_argument("--compressbits", type=int,help="HDF only. Bits to keep for compression. -1 for no compression. This overrides --outmode and related options.",default=-1)
	parser.add_argument("--nooutliers", type=int,help="With --compressbits, if set will truncate outlier values to preserve sigfigs for more useful values. default 1 (enabled)",default=1)
	parser.add_argument("--diffmap", type=str, help="Will match the power spectrum of the specified file to the input file, then subtract it from the input file")

	parser.add_argument("--fftclip", metavar="x,y,z", type=parse_list_arg(int,int,int), help="Make the output have this size, rescaling by padding FFT.")
	parser.add_argument("--filtertable", type=str, action="append",help="Applies a 2 column (S,amp) file as a filter in Fourier space, assumed 0 outside the defined range.")
	parser.add_argument("--first", metavar="n", type=int, default=0, help="the first image in the input to process [0 - n-1])")
	parser.add_argument("--fouriershrink", metavar="n", type=float, action="append", help="Reduce an image size by an arbitrary scaling factor by clipping in Fourier space. eg - 2 will reduce image size to 1/2.")
	parser.add_argument("--fragmentize", metavar="N,thr", type=parse_list_arg(int,float), default=None, help="Randomly removes chunks from the input map and produces N derived maps. thr is the isosurface threshold for chunking. Don't combine with other options.")

	parser.add_argument("--icos2to5",action="store_true",help="Rotate an icosahedral map from 2-fold on Z (MRC standard) to 5-fold on Z (EMAN standard)  orientation")
	parser.add_argument("--icos5to2",action="store_true",help="Rotate an icosahedral map from 5-fold on Z (EMAN standard) to 2-fold on Z (MRC standard) orientation")
	parser.add_argument("--inputto1", action="store_true",help="All voxels in the input file are set to 1 after reading. This can be used with mask.* processors to produce a mask file of the correct size.")

	parser.add_argument("--last", metavar="n", type=int, default=-1, help="the last image in the input to process")

	parser.add_argument("--matchto", type=str, action="append", help="Match filtration of input volume to this specified volume.")
	parser.add_argument("--medianshrink", metavar="n", type=int, action="append", help="Downsamples the volume by a factor of n by computing the local median")
	parser.add_argument("--meanshrink", metavar="n", type=int, action="append", help="Downsamples the volume by a factor of n by computing the local average")
	parser.add_argument("--meanshrinkbig", metavar="n", type=int, default=0, help="Downsamples the volume by a factor of n without reading the entire volume into RAM. The output file (after shrinking) must fit into RAM. If specified, this must be the ONLY option on the command line. Any other options will be ignored. Output data type will match input data type. Works only on single image files, not stack files.")
	parser.add_argument("--mult", metavar="f", type=float, help="Scales the densities by a fixed number in the output")
	parser.add_argument("--multfile", type=str, action="append", help="Multiplies the volume by another volume of identical size. This can be used to apply masks, etc.")

	parser.add_argument("--origin", metavar="x,y,z", type=parse_list_arg(int,int,int), help="Set the coordinates for the pixel (0,0,0) for Chimera. THIS HAS NO IMPACT ON IMAGE PROCESSING !")
	parser.add_argument("--outmode",type=str, default="float", help="All EMAN2 programs write images with 4-byte floating point values when possible by default. This allows specifying an alternate format when supported (int8, int16, int32, uint8, uint16, uint32). Values are rescaled to fill MIN-MAX range.")
	parser.add_argument("--outnorescale",action="store_true",help="If specified, floating point values will not be rescaled when writing data as integers. Values outside of range are truncated.")
	parser.add_argument("--outtype", metavar="image-type", type=str, help="Set output image format, mrc, imagic, hdf, etc")

	parser.add_argument("--ppid", type=int, help="Set the PID of the parent process, used for cross platform PPID",default=-2)
	parser.add_argument("--process", metavar="processor_name:param1=value1:param2=value2", type=str, action="append", help="apply a processor named 'processorname' with all its parameters/values.")

	parser.add_argument("--resetxf",action="store_true",help="Reset an existing transform matrix to the identity matrix")
	parser.add_argument("--ralignzphi", type=str ,action="append", help="Refine Z alignment within +-10 pixels  and phi +-15 degrees (for C symmetries), specify name of alignment reference here not with --alignref")
	parser.add_argument("--rot",type=str,metavar="az,alt,phi, convention:par=val:..., or 'header' to use xform.align3d from header",help="Rotate map. Specify az,alt,phi or convention:par=val:par=val:...  eg - mrc:psi=22:theta=15:omega=7", action="append",default=None)

	parser.add_argument("--scale", metavar="n", type=float, action="append", help="Rescales the data in the image by 'n', opposite behavior of 'shrink' above. Scaling is done by interpolation in real-space. Box size unchanged. See '--clip'")
	parser.add_argument("--setsf", type=str, metavar="inputfile", help="Set the radial structure factor. Must specify apix.")
	parser.add_argument("--setisosf", type=str, metavar="inputfile", help="Make the amplitude rotationally symmetric, and equivalent to provided structure factor")
	parser.add_argument("--step",type=str,default=None,help="Specify <init>,<step>. Processes only a subset of the input data. For example, 0,2 would process only the even numbered particles")
	parser.add_argument("--swap", action="store_true", help="Swap the byte order")
	parser.add_argument("--sym", dest = "sym", action="append", help = "Symmetry to impose - choices are: c<n>, d<n>, h<n>, tet, oct, icos")

	parser.add_argument("--tomoprep", action="store_true", help="Produces a special HDF file designed for rapid interactive tomography annotation. This option should be used alone.")
	parser.add_argument("--tophalf", action="store_true", help="The output only keeps the top half map")
	parser.add_argument("--trans", metavar="dx,dy,dz", type=parse_list_arg(float,float,float), action="append", help="Translate map by dx,dy,dz ")

	parser.add_argument("--unstacking", action="store_true", help="Process a stack of 3D images, then output as a series of numbered single image files")

	optionlist = get_optionlist(sys.argv[1:])

	options, args = parser.parse_args()

	if len(args) != 2:
		print("usage: " + usage)
		print("Please run '" + progname + " -h' for detailed options")
		sys.exit(1)

	if options.step and options.first:
		print('Invalid options. You used --first and --step. The --step option contains both a step size and the first image to step from. Please use only the --step option rather than --step and --first')
		sys.exit(1)

	infile = args[0]
	outfile = args[1]

	out_ext = os.path.splitext(outfile)[1]

	if out_ext == ".lst":
		print("Output file extension may not be .lst: " + outfile)
		sys.exit(1)

	# this option uses one input map and produces a 3-D stack of output maps, so doesn't play with others
	if options.fragmentize:
		N, thr = options.fragmentize
		print(type(N))
		print(type(thr))
		print(N, thr)
		parser.error("N, thr")

		try: os.unlink(outfile)
		except: pass
		map = EMData(infile,0)
		seg = map.process("segment.kmeans",{"ampweight":1,"nseg":N+2,"thr":thr})  # +2 is arbitrary, to decrease the amount of excluded mass
		for i in range(N):
			seg2 = seg.process("threshold.binaryrange",{"low":i-0.1,"high":i+0.1})    # by subtracting 1, we don't remove anything from the first map
			seg2.process_inplace("math.linear",{"scale":-1.0,"shift":1.0})
			map2 = map*seg2
			map2.write_image(outfile,i)
		print("Fragmentization complete! Exiting")
		sys.exit(0)

	# This is a specialized option which doesn't play nice with ANY other options in the command
	# it will do piecewise shrinking of a map which is too large for RAM
	if options.meanshrinkbig > 0:
		print("Dedicated large-map shrinking mode. No other operations will be performed.")
		hdr = EMData(infile,0,True)
		shrink = options.meanshrinkbig
		if shrink > 10: print("Shrinking by >10x is not recommended")

		nx,ny,nz = hdr["nx"],hdr["ny"],hdr["nz"]
		nnx = old_div(nx,shrink)
		nny = old_div(ny,shrink)
		nnz = old_div(nz,shrink)
		print("%d x %d x %d --> %d x %d x %d    %1.1f GB of RAM required"%(nx,ny,nz,nnx,nny,nnz,old_div((nnx*nny*nnz*4+shrink*4*ny*shrink*4),1.0e9)))

		out = EMData(nnx,nny,nnz)
		out.to_zero()
		ltime = 0
		for z in range(0, nz, shrink):
			if time()-ltime > 0.5:
				print("  %d/%d\r"%(z,nz), end=' ')
				sys.stdout.flush()
				ltime = time()
			for y in range(0, ny, 4*shrink):
				tmp = EMData(infile,0,False,Region(0,y,z,nx,4*shrink,shrink))
				tmp.process_inplace("math.meanshrink",{"n":shrink})
				out.insert_clip(tmp,(0,old_div(y,shrink),old_div(z,shrink)))

		stype=EM_FLOAT
		print("  %d/%d"%(nz,nz), end=' ')
		print("\nWriting in data mode ",file_mode_imap[int(stype)])

		if stype != EM_FLOAT:
			out["render_min"] = file_mode_range[stype][0]
			out["render_max"] = file_mode_range[stype][1]

		if options.compressbits >= 0:
			out.write_compressed(outfile,0,options.compressbits,nooutliers=options.nooutliers,erase=erase)
		else:
			try: out.write_image(outfile,0,IMAGE_UNKNOWN,0,None,EMUtil.EMDataType(stype))
			except:
				print("Failed to write in file mode matching input, reverting to floating point output")
				out.write_image(outfile,0)

		print("Complete !")
		sys.exit(0)

	if options.tomoprep > 0:
		print("Tomography processing preparation mode. No other processing will be performed.")

		if outfile[-4:]!=".hdf":
			print("Preprocessed tomograms can only be in HDF format")
			sys.exit(1)

		hdr = EMData(infile,0,True)
		nx,ny,nz = hdr["nx"],hdr["ny"],hdr["nz"]

		# If this is a "y-short" tomogram convert it to z-short
		if min(nx,ny,nz) == ny:
			# Create an empty file of the correct size
			tmp = EMData()
			tmp.set_size(nx,nz,ny)
			tmp.write_image(outfile,0,IMAGE_UNKNOWN,False,None,EM_UCHAR)

			# Write the output volume slice by slice
			for z in range(ny):
				slice = EMData(infile,0,False,Region(0,z,0,nx,1,nz))
				slice.write_image(outfile,0,IMAGE_UNKNOWN,False,Region(0,0,ny-z-1,nx,nz,1),EM_UCHAR)

			# Write
		else:
			# Create an empty file of the correct size
			tmp = EMData()
			tmp.set_size(nx,ny,nz)
			tmp.write_image(outfile,0,IMAGE_UNKNOWN,False,None,EM_UCHAR)

			# write the output volume slice by slice
			for z in range(ny):
				slice = EMData(infile,0,False,Region(0,0,z,nx,nz,1))
				slice.write_image(outfile,0,IMAGE_UNKNOWN,False,Region(0,0,z,nx,nz,1),EM_UCHAR)

		print("Complete !")
		sys.exit(0)

	n0 = options.first
	n1 = options.last
	nimg = 1 if infile[0] == ":" else EMUtil.get_image_count(infile)
	if not (0 <= n1 <= nimg):
		n1 = nimg-1

	# If the output file exists and has exactly one image we delete the file later if writing compressed
	try:
		erase = (EMUtil.get_image_count(outfile) == 1)
	except:
		erase = False

	if options.step != None:
		n0 = int(options.step.split(",")[0])
		n2 = int(options.step.split(",")[1])
	else: n2 = 1

	alignref = EMData(options.alignref,0) if options.alignref else None

	if options.calcradial >= 0:
		print("Computing radial real-space distribution. All other options ignored!")
		curves = []
		for i in range(n0,n1+1,n2):
			img = EMData(infile,i)
			c = img.calc_radial_dist(old_div(img["nx"],2),0,1,options.calcradial)
			curves.append(c)

		with open(outfile,"w") as out:
			out.write("# {} mode {}".format(infile,options.calcradial))
			for l in range(len(curves[0])):
				out.write("\n{}".format(l))
				for c in curves:
					out.write("\t{}".format(c[l]))

		sys.exit(0)

	if options.average:
		print("Averaging particles from %d to %d stepping by %d. All other options ignored !"%(n0,n1,n2))
		avg_dict = parsemodopt(options.averager)
		avgr = Averagers.get(avg_dict[0],avg_dict[1])

		for i in range(n0,n1+1,n2):
			a = EMData(infile,i)
			if options.avg_byxf and a.has_attr("xform.align3d"):
				a.process_inplace('normalize.edgemean')
				a.transform(a["xform.align3d"])
			avgr.add_image(a)
		avg = avgr.finish()

		try:
			avg["ptcl_repr"] = sum([i["ptcl_repr"] for i in ptcls])
		except:
			pass

		if options.compressbits >= 0:
			avg.write_compressed(outfile,0,options.compressbits,nooutliers=options.nooutliers,erase=erase)
		else:
			avg.write_image(outfile,0)
		sys.exit(1)

	if not (0 <= n0 <= nimg):
		print("Your first index is out of range, changed to zero")
		n0 = 0

	if n1 == -1:
		n1 = nimg-1
	elif n1 > nimg-1:
		print("Your last index is out of range, changed to %d" % (nimg-1))
		n1 = nimg-1

	# Steve:  why are all of the images being read at once !?!?. This is nuts
	# modified so for multiple volumes, returns header-only

	datlst = parse_infile(infile, n0, n1, n2, options.apix)

	logid = E2init(sys.argv,options.ppid)

	x = datlst[0].get_xsize()
	y = datlst[0].get_ysize()
	z = datlst[0].get_zsize()

	xc = old_div(x,2)
	yc = old_div(y,2)
	zc = old_div(z,2)

	nx = x
	ny = y
	nz = z

	apix = datlst[0]["apix_x"]  # default to apix_x from file
	if options.apix:
		apix = options.apix

	if not "outtype" in optionlist:
		optionlist.append("outtype")

	for img_index, data in enumerate(datlst):
		index_d = defaultdict(int)

		# if this is a list of images, we have header-only, and need to read the actual volume
		if len(datlst) > 1:
			data = EMData(data["source_path"],data["source_n"])

		if options.apix:
			data.set_attr('apix_x', apix)
			data.set_attr('apix_y', apix)
			data.set_attr('apix_z', apix)

		if options.inputto1:
			data.to_one()			# replace all voxel values with 1.0

		if options.resetxf:
			data["xform.align3d"]=Transform()

		for option1 in optionlist:
			if option1 == "origin":
				data.set_xyz_origin(*options.origin)

			elif option1 == "matchto":
				mt = EMData(options.matchto[0])
				data.process_inplace("filter.matchto",{"to":mt})

			elif option1 == "diffmap":
				mt = EMData(options.diffmap)
				mt.process_inplace("filter.matchto",{"to":data})
				data.sub(mt)

			elif option1 == "calcfsc":
				datafsc = EMData(options.calcfsc)
				fsc = data.calc_fourier_shell_correlation(datafsc)
				third = len(fsc) // 3
				xaxis = fsc[0:third]
				fsc = fsc[third:2*third]
				saxis = [old_div(x,apix) for x in xaxis]
				Util.save_data(saxis[1],saxis[1]-saxis[0],fsc[1:-1],args[1])

			elif option1 == "calcsf":
				dataf = data.do_fft()
				curve = dataf.calc_radial_dist(old_div(ny,2), 0, 1.0,True)
				curve = [old_div(i,(dataf["nx"]*dataf["ny"]*dataf["nz"])) for i in curve]
				Util.save_data(0, 1.0/(apix*ny), curve, options.calcsf)

			elif option1 == "setsf":
				sf = XYData()
				sf.read_file(options.setsf)
				data.process_inplace("filter.setstrucfac",{"apix":data["apix_x"],"strucfac":sf})

			elif option1 == "setisosf":
				sf = XYData()
				sf.read_file(options.setisosf)
				data.process_inplace("filter.setisotropicpow",{"apix":data["apix_x"],"strucfac":sf})

			elif option1 == "filtertable":
				tf = options.filtertable[index_d[option1]]
				xy = XYData()
				xy.read_file(tf)
				ny = data["ny"]
				filt = [xy.get_yatx_smooth(old_div(i,(apix*ny)),1) for i in range(int(ceil(ny*sqrt(3.0)/2)))]
				data.process_inplace("filter.radialtable",{"table":filt})

			elif option1 == "process":
				fi = index_d[option1]
				filtername, param_dict = parsemodopt(options.process[fi])
				if not param_dict: param_dict = {}

				#Parse the options to convert the image file name to EMData object
				for key in list(param_dict.keys()):
					if not str(param_dict[key]).isdigit():
						try:
							if os.path.is_file(param_dict[key]):
								param_dict[key] = EMData(param_dict[key])
						except:
							pass

				if filtername == "misc.directional_sum":
					data=data.process(filtername,param_dict)
				else:
					try:
						data.process_inplace(filtername, param_dict)
					except:
						traceback.print_exc()
						print("Error running processor: ",filtername,param_dict)
				index_d[option1] += 1

			elif option1 == "ralignzphi":
				zalignref = EMData(options.ralignzphi[index_d[option1]],0)
				dang = 80.0/data["ny"]		# 1 pixel at ~3/4 radius
				dzmax = old_div(data["ny"],20)			# max +-z shift
				best = (1000,0,0,data)

				dsd = data.process("math.meanshrink",{"n":2})			# downsampled data
				dsd.process_inplace("filter.lowpass.gauss",{"cutoff_abs":0.25})

				dsr = zalignref.process("math.meanshrink",{"n":2})	# downsampled reference
				dsr.process_inplace("filter.lowpass.gauss",{"cutoff_abs":0.25})

				# coarse search on downsampled/filtered data
				for it in range(3):
					for z in range(best[1]-dzmax,best[1]+dzmax+1):
						zimg = dsd.process("xform",{"transform":Transform({"type":"eman","tz":z,"phi":best[2]})})
						tmp = (dsr.cmp("ccc",zimg),z,best[2],zimg)
						if best[0] > tmp[0]: best=tmp

					for phi in arange(best[2]-20.0,best[2]+20.0,dang*2.0):
						zimg = dsd.process("xform",{"transform":Transform({"type":"eman","tz":best[1],"phi":phi})})
						tmp = dsr.cmp("ccc",zimg),best[1],phi,zimg
						if best[0] > tmp[0]: best = tmp

				# Fix best() for full sampling
				zimg = data.process("xform",{"transform":Transform({"type":"eman","tz":best[1]*2,"phi":best[2]})})
				best = (1000.0,best[1]*2,best[2],zimg)

				# now we do a fine search only in the neighborhood on the original data
				for z in range(best[1]-3,best[1]+4):
					for phi in arange(best[2]-dang*3.0,best[2]+dang*3.5,dang):
						zimg = data.process("xform",{"transform":Transform({"type":"eman","tz":z,"phi":phi})})
						tmp = zalignref.cmp("ccc",zimg),z,best[2],zimg
						if best[0] > tmp[0]: best = tmp

				data = best[3]
				data["xform.align3d"] = Transform({"type":"eman","tz":best[1],"phi":best[2]})

			elif option1 == "alignctod":
				nsym = int(options.alignctod[0][1:])
				angrange = 360.0 /nsym		# probably more than necessary, but we'll do it anyway...
				astep = 360.0/pi*atan(2.0/data["nx"])
				nstep = int(old_div(angrange,astep))

				best=(1e23,0)
				for azi in range(nstep):
					az = azi*astep
					datad = data.process("xform",{"transform":Transform({"type":"eman","alt":180.0,"az":az})})	# rotate 180, then about z
					c = data.cmp("ccc",datad)
					best = min(best,(c,az))

				bcen = best[1]
				for azi in range(-4,5):
					az = bcen+azi*astep/4.0
					datad = data.process("xform",{"transform":Transform({"type":"eman","alt":180.0,"az":az})})	# rotate 180, then about z
					c = data.cmp("ccc",datad)
					best = min(best,(c,az))

				print("alignctod, rotate:",best[1]/2.0)
				data.process_inplace("xform",{"transform":Transform({"type":"eman","az":best[1]/2.0})})	# 1/2 the angle to get it on the 2-fold

			elif option1 == "align":
				if alignref == None:
					print("Error, no alignment reference specified with --alignref")
					sys.exit(1)

				fi = index_d[option1]
				alignername, param_dict = parsemodopt(options.align[fi])
				if not param_dict: param_dict={}

				#Parse the options to convert the image file name to EMData object
				for key in list(param_dict.keys()):
					if not str(param_dict[key]).isdigit():
						try:
							param_dict[key] = EMData(param_dict[key])
						except:
							pass

				# note we cannot really pass xform as string input...
				if "xform.align3d" in param_dict:
					if param_dict["xform.align3d"] == 'none':
						param_dict["xform.align3d"] = Transform()

				# For 'refine' aligners, we normally want to provide a starting alignment, presumably from the previous aligner. If we can't find one with start with identity matrix
				if "refine" in alignername and "xform.align3d" not in param_dict:
					try:
						param_dict["xform.align3d"] = data["xform.align3d"]
						print(alignername," using xform.align3d from image")
					except:
						param_dict["xform.align3d"] = Transform()
						print(alignername," didn't find a starting transform, using identity matrix.")

				# actual alignment
				data = data.align(alignername,alignref, param_dict)
				index_d[option1] += 1

			elif option1 == "mult":
				data.mult(options.mult)

			elif option1 == "addfile":
				af = EMData(options.addfile[index_d[option1]],0)
				data.add(af)
				index_d[option1] += 1

			elif option1 == "multfile":
				mf=EMData(options.multfile[index_d[option1]],0)
				data.mult(mf)
				index_d[option1] += 1

			elif option1 == "add":
				data.add(options.add)

			elif option1 == "icos5to2":
				xf = Transform.icos_5_to_2()
				data.process_inplace("xform",{"transform":xf})

			elif option1 == "icos2to5":
				xf = Transform.icos_5_to_2()
				xf.invert()
				data.process_inplace("xform",{"transform":xf})

			elif option1 == "trans":
				fi = index_d[option1]
				data.translate(*options.trans[fi])
				index_d[option1] += 1

			elif option1 == "rot":
				fi = index_d[option1]
				if options.rot[fi].lower() == "header":
					data.transform(data["xform.align3d"])
				else:
					xform = parse_transform(options.rot[fi])
					data.transform(xform)
				index_d[option1] += 1

			elif option1 == "clip":
				x = data["nx"]
				y = data["ny"]
				z = data["nz"]

				print("options.clip: ", options.clip)
				if len(options.clip) == 6:
					(nx, ny, nz, xc, yc, zc) = options.clip
				elif len(options.clip) == 3:
					(nx, ny, nz) = options.clip
					xc = old_div(x,2)
					yc = old_div(y,2)
					zc = old_div(z,2)
				elif len(options.clip) == 1:
					nx = options.clip[0]
					ny = nx
					nz = nx
					xc = old_div(x,2)
					yc = old_div(y,2)
					zc = old_div(z,2)

				if not (0 <= xc < x and 0 <= yc < y and 0 <= zc < z):
					xc = old_div(x,2)
					yc = old_div(y,2)
					zc = old_div(z,2)

				print("nx: ", nx)
				print("ny: ", ny)
				print("nz: ", nz)
				if x != nx or y != ny or z != nz:
					data.clip_inplace(Region(xc-old_div(nx,2), yc-old_div(ny,2), zc-old_div(nz,2), nx, ny, nz))
					index_d[option1] += 1

			elif option1 == "sym":
				sym = options.sym[index_d[option1]]
				xf = Transform()
				xf.to_identity()
				nsym = xf.get_nsym(sym)
				avg_dict = parsemodopt(options.averager)
				symavgr = Averagers.get(avg_dict[0],avg_dict[1])

				for i in range(nsym):
					ref = data.copy()
					ref.transform(xf.get_sym(sym,i))
					symavgr.add_image(ref)
				data = symavgr.finish()

			elif option1 == "scale":
				scale_f = options.scale[index_d[option1]]
				if scale_f != 1.0:
					data.scale(scale_f)
				index_d[option1] += 1

			elif option1 == "medianshrink":
				shrink_f = options.medianshrink[index_d[option1]]
				if shrink_f > 1:
					data.process_inplace("math.medianshrink",{"n":shrink_f})
					nx = data.get_xsize()
					ny = data.get_ysize()
					nz = data.get_zsize()
				index_d[option1] += 1

			elif option1 == "meanshrink":
				shrink_f = options.meanshrink[index_d[option1]]
				if shrink_f > 1:
					data.process_inplace("math.meanshrink",{"n":shrink_f})
					nx = data.get_xsize()
					ny = data.get_ysize()
					nz = data.get_zsize()
				index_d[option1] += 1

			elif option1 == "fouriershrink":
				shrink_f = options.fouriershrink[index_d[option1]]
				if shrink_f > 1:
					data.process_inplace("math.fft.resample",{"n":shrink_f})
					nx = data.get_xsize()
					ny = data.get_ysize()
					nz = data.get_zsize()
				index_d[option1] += 1

			elif option1 == "fftclip":
				fnx, fny, fnz = options.fftclip

				fft = data.do_fft()
				padfft = fft.get_clip(Region(0, 0, 0, fnx+2, fny, fnz))
				data = padfft.do_ift()

			elif option1 == "tophalf":
				data = data.get_top_half()

			elif option1 == "outtype":
				if not options.outtype:
					options.outtype = "unknown"

		if options.outmode not in ("float","compressed"):
			if options.outnorescale:
				# This sets the minimum and maximum values to the range for the specified type, which should result in no rescaling
				outmode = file_mode_map[options.outmode]
				data["render_min"] = file_mode_range[outmode][0]
				data["render_max"] = file_mode_range[outmode][1]
			else:
				data["render_min"] = data["minimum"]
				data["render_max"] = data["maximum"]
				print("rescale output to range {} - {}".format(data["render_min"],data["render_max"]))

		if options.unstacking:	#output a series numbered single image files
			if options.compressbits >= 0:
				data.write_compressed(os.path.splitext(outfile)[0]+'-'+str(img_index+1).zfill(len(str(nimg)))+ os.path.splitext(outfile)[-1],0,options.compressbits,nooutliers=options.nooutliers,erase=erase)
			else:
				data.write_image(os.path.splitext(outfile)[0]+'-'+str(img_index+1).zfill(len(str(nimg)))+ os.path.splitext(outfile)[-1], -1, EMUtil.ImageType.IMAGE_UNKNOWN, False, None, file_mode_map[options.outmode], not(options.swap))
		else:   #output a single 2D image or a 2D stack
			if options.append:
				if options.compressbits >= 0:
					data.write_compressed(outfile,-1,options.compressbits,nooutliers=options.nooutliers,erase=erase)
				else:
					data.write_image(outfile, -1, EMUtil.get_image_ext_type(options.outtype), False, None, file_mode_map[options.outmode], not(options.swap))
			else:
				if options.compressbits >= 0:
					data.write_compressed(outfile,img_index,options.compressbits,nooutliers=options.nooutliers,erase=erase)
				else:
					data.write_image(outfile, img_index, EMUtil.get_image_ext_type(options.outtype), False, None, file_mode_map[options.outmode], not(options.swap))

	E2end(logid)


if __name__ == "__main__":
	main()
