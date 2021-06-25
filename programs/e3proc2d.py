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
import EMAN2
from eman.proc import parse_list_arg
from collections import defaultdict, deque
import sys
import os.path
import math
import random
import os
import datetime
import time

# constants

xyplanes = ['xy', 'yx']
xzplanes = ['xz', 'zx']
yzplanes = ['yz', 'yz']


def changed_file_name(input_name, output_pattern, input_number, multiple_inputs):
	# convert an input file name to an output file name
	# by replacing every @ or * in output_pattern with
	# the input file base name (no extension)

	outname = output_pattern

	if multiple_inputs or 'FILL_ONE_FILE' in os.environ :
		base_name = os.path.basename(os.path.splitext(input_name)[0])

		if '@' in outname :
			outname = outname.replace('@', base_name)

		if '*' in outname :
			outname = outname.replace('*', base_name)

		if '%i' in outname :
			outname = outname.replace('%i', str(input_number))

		if '%j' in outname :
			outname = outname.replace('%j', str(input_number-1))

		if '%d' in outname :
			dt = datetime.datetime.now()
			date_str = str(dt.year) + '_' + str(dt.month) + '_' + str(dt.day)
			outname = outname.replace('%d', date_str)

		if '%t' in outname :
			dt = datetime.datetime.now()
			time_str = str(dt.hour) + '_' + str(dt.minute) + '_' + str(dt.second)
			outname = outname.replace('%t', time_str)

		if '%%' in outname :
			outname = outname.replace('%%', '%')

	return outname


def image_from_formula(n_x, n_y, n_z, formula):
	# Create a 2D or 3D image from a formula in x, y, z,
	# with 0 <= x <= n_x-1, 0 <= y <= n_y-1, 0 <= z <= n_z-1,
	# with a formula like "x+y+z" or "x*y+10*z" or "x+y".
	# The formula may contain variables nx, ny, or nz or
	# xn, yn, or zn (x, y, and z normalized from 0.0 to 1.0).

	nx = int(n_x)
	ny = int(n_y)
	nz = int(n_z)

	x1 = 1.0 / max(nx-1, 1)
	y1 = 1.0 / max(ny-1, 1)
	z1 = 1.0 / max(nz-1, 1)

	emd  = EMData(nx, ny, nz)
	emdn = EMNumPy.em2numpy(emd)

	for z in range(0, nz) :
		zn = z * z1

		for y in range(0, ny) :
			yn = y * y1

			for x in range(0, nx) :
				xn = x * x1

				try :
					v = eval(formula)
				except :
					v = 0.0

				if nz > 1 :
					emdn[z][y][x] = v
				else:
					emdn[y][x] = v

	return EMNumPy.numpy2em(emdn)


def parse_infile_arg():
	pass


def main():
	progname = os.path.basename(sys.argv[0])
	usage = progname + """ [options] <inputfile> ... <inputfile> <outputfile>"""
	description = """

	MRC stack files MUST use the .mrcs extension to be treated as a set of 2-D images (or you must 
	use one of the --threed* options)

	If there is more than one input file, then outputfile is a pattern, where @
	in the pattern is replaced by the input file base name (minus any extension).

	Generic 2-D image processing and file format conversion program. Acts on stacks of 2-D images
	(multiple images in one file). All EMAN2 recognized file formats accepted (see Wiki for list).

	You can create a new 2-D or 3-D image from scratch instead of reading from a file by specifying 
	':<nx>:<ny>:<expression_in_x_y>' or ':<nx>:<ny>:<nz>:<expression_in_x_y_z>' as an input filename,
	where 0 <= x < nx, 0 <= y < ny, 0 <= z < nz, and the expression can be just a number.

	If performing certain operations which do not require an output file, specify "none" as the output file.

	Examples:

	convert IMAGIC format test.hed to HDF format:
	e2proc2d.py test.hed test.hdf

	convert all MRC format files in current directory to HDF format:
	e2proc2d.py *.mrc @.hdf

	convert a 'set' (.lst file) to an MRC stack file:
	e2proc2d.py sets/myset.lst myset.mrcs

	create a new image, initialized with 1.0, then mask it:
	e2proc2d.py :128:128:1 mymask.hdf --process mask.soft:outer_radius=50

	apply a 10 A low-pass filter to a stack of particles downsample the particles by a factor of 2
	and write output to a new file.
	e2proc2d.py ptcl.hdf ptcl.filt.hdf --process filter.lowpass.gauss:cutoff_freq=0.1 --meanshrink 2

	'e2help.py processors -v 2' for a detailed list of available procesors
	"""

	parser = EMArgumentParser(description=description, allow_abbrev=False, version=EMANVERSION)

	parser.add_argument("--apix", type=float, help="A/pixel for S scaling")
	parser.add_argument("--average", metavar="N", nargs='?', type=int, help="Averages sets of N sequential frames or ALL. eg - if N=4 and the input contains 100 images, the output would be 25 images")
	parser.add_argument("--averager",type=str,help="If --average is specified, this is the averager to use (e2help.py averager). Default=mean",default="mean")
	parser.add_argument("--calcsf", metavar="outputfile", type=str, help="calculate a radial structure factor for the image and write it to the output file, must specify apix. divide into <n> angular bins")
	parser.add_argument("--calccont", action="store_true", help="Compute the low resolution azimuthal contrast of each image and put it in the header as eval_contrast_lowres. Larger values imply more 'interesting' images.")
	# parser.add_argument("--clip", metavar="xsize,ysize[,xcenter,ycenter]", type=parse_list_arg(int,int), action="append", help="Specify the output size in pixels xsize,ysize[,xcenter,ycenter], images can be made larger or smaller.")
	parser.add_argument("--clip", metavar="xsize,ysize[,xcenter,ycenter]", type=parse_list_arg((int,int),(int,int,int,int)), action="append", help="Specify the output size in pixels xsize,ysize[,xcenter,ycenter], images can be made larger or smaller.")
	# parser.add_argument("--clip", metavar="xsize,ysize[,xcenter,ycenter]", type=parse_list_arg((int,int),(int,int,int),(int,int,int,int)), action="append", help="Specify the output size in pixels xsize,ysize[,xcenter,ycenter], images can be made larger or smaller.")
	# parser.add_argument("--clip", metavar="xsize,ysize[,xcenter,ycenter]", type=parse_list_arg([int,int],[int,int,int,int]), action="append", help="Specify the output size in pixels xsize,ysize[,xcenter,ycenter], images can be made larger or smaller.")
	parser.add_argument("--exclude", metavar="exclude-list-file", type=EMAN2.read_number_file, help="Excludes image numbers, either a list of comma separated values, or a filename with one number per line, first image == 0")
	parser.add_argument("--fftavg", metavar="filename", type=str, help="Incoherent Fourier average of all images and write a single power spectrum image")
	parser.add_argument("--process", metavar="processor_name:param1=value1:param2=value2", type=str, action="append", help="apply a processor named 'processorname' with all its parameters/values.")
	parser.add_argument("--mult", metavar="k", type=float, help="Multiply image by a constant. mult=-1 to invert contrast.")
	parser.add_argument("--add", metavar="f", type=float,action="append",help="Adds a constant 'f' to the densities")
	parser.add_argument("--first", metavar="n", type=int, default=0, help="the first image in the input to process [0 - n-1])")
	parser.add_argument("--last", metavar="n", type=int, default=-1, help="the last image in the input to process")
	parser.add_argument("--list", metavar="listfile", type=EMAN2.read_number_file, help="Works only on the image numbers in LIST file")
	parser.add_argument("--randomn", metavar="n", type=int, default=0, help="Selects a random subset of N particles from the file to operate on.")
	parser.add_argument("--inplace", action="store_true", help="Output overwrites input, USE SAME FILENAME, DO NOT 'clip' images.")
	parser.add_argument("--interlv", metavar="interleave-file", type=str, help="Specifies a 2nd input file. Output will be 2 files interleaved.")
	parser.add_argument("--extractboxes", action="store_true",help="Extracts box locations from the image header to produce a set of .box files for only the particles in the .lst files")
	parser.add_argument("--meanshrink", metavar="n", type=float, action="append", help="Reduce an image size by an integral (1.5 also allowed) scaling factor using average. eg - 2 will reduce image size to 1/2. Clip is not required.")
	parser.add_argument("--medianshrink", metavar="n", type=int, action="append", help="Reduce an image size by an integral scaling factor, uses median filter. eg - 2 will reduce image size to 1/2. Clip is not required.")
	parser.add_argument("--fouriershrink", metavar="n", type=float, action="append", help="Reduce an image size by an arbitrary scaling factor by clipping in Fourier space. eg - 2 will reduce image size to 1/2.")
	parser.add_argument("--compressbits", type=int,help="HDF only. Bits to keep for compression. -1 for no compression",default=-1)
	parser.add_argument("--outmode", type=str, choices=EMAN2.file_mode_map.keys(), default="float", help=f"All EMAN2 programs write images with 4-byte floating point values when possible by default. This allows specifying an alternate format when supported ({EMAN2.file_mode_map.keys()}). Values are rescaled to fill MIN-MAX range.")
	parser.add_argument("--fixintscaling", type=str, default=None, help="When writing to an 8 or 16 bit integer format the data must be scaled. 'full' will ensure the full range of values are included in the output, 'sane' will pick a good range, a number will set the range to mean+=sigma*number")
	# choices = ['noscale', 'full', 'sane']

	parser.add_argument("--norefs", action="store_true", help="Skip any input images which are marked as references (usually used with classes.*)")
	parser.add_argument("--output", metavar="outfile", type=argparse.FileType('w'), help="output file.")
	parser.add_argument("--outtype", metavar="image-type", type=str, default="unknown", help="output image format, 'mrc', 'imagic', 'hdf', etc. if specify spidersingle will output single 2D image rather than 2D stack.")
	parser.add_argument("--radon",  action="store_true", help="Do Radon transform")
	parser.add_argument("--randomize", metavar="da,dxy,flip", type=parse_list_arg(float,float,int), action="append",help="Randomly rotate/translate the image. Specify: da,dxy,flip  da is a uniform distribution over +-da degrees, dxy is a uniform distribution on x/y, if flip is 1, random handedness changes will occur")
	parser.add_argument("--rotavg", action="store_true", help="Compute the 1-D rotational average of each image as a final step before writing the output")
	parser.add_argument("--rotate", type=float, action="append", help="Rotate clockwise (in degrees)")
	parser.add_argument("--fp",  type=int, choices=range(7), help="This generates rotational/translational 'footprints' for each input particle, the number indicates which algorithm to use (0-6)")
	parser.add_argument("--scale", metavar="f", type=float, action="append", help="Scale by specified scaling factor. Clip must also be specified to change the dimensions of the output map.")
	parser.add_argument("--anisotropic", metavar="amount,angle", type=parse_list_arg(float,float), action="append", help="Anisotropic scaling, stretches on one axis and compresses the orthogonal axis. Specify amount,angle. See e2evalrefine")
	parser.add_argument("--setsfpairs",  action="store_true", help="Applies the radial structure factor of the 1st image to the 2nd, the 3rd to the 4th, etc")
	parser.add_argument("--split", metavar="n", type=int, default=1, help="Splits the input file into a set of n output files")
	parser.add_argument("--translate", metavar="x,y", type=parse_list_arg(float,float), action="append", help="Translate by x,y pixels")
	parser.add_argument("--headertransform", type=int, choices=[0, 1], action="append", help="This will take the xform.align2d header value from each particle, and apply it. Pass 0 to perform the transform or 1 to perform the inverse.")
	parser.add_argument("--verbose", "-v", dest="verbose", action="store", metavar="n", type=int, help="verbose level [0-9], higher number means higher level of verboseness",default=1)
	parser.add_argument("--plane", choices=xyplanes + xzplanes + yzplanes, type=str, default='xy', help="Change the plane of image processing, useful for processing 3D mrcs as 2D images.")
	parser.add_argument("--writejunk", action="store_true", help="Writes the image even if its sigma is 0.")
	parser.add_argument("--swap", action="store_true", help="Swap the byte order")
	parser.add_argument("--threed2threed", action="store_true", help="Process 3D image as a stack of 2D slices, then output as a 3D image")
	parser.add_argument("--threed2twod", action="store_true", help="Process 3D image as a stack of 2D slices, then output as a 2D stack")
	parser.add_argument("--twod2threed", action="store_true", help="Process a stack of 2D images, then output as a 3D image.")
	parser.add_argument("--unstacking", action="store_true", help="Process a stack of 2D images, then output as a series of numbered single image files")
	parser.add_argument("--ppid", type=int, help="Set the PID of the parent process, used for cross platform PPID",default=-2)
	parser.add_argument("--step",type=str,default="0,1",help="Specify <init>,<step>. Processes only a subset of the input data. For example, 0,2 would process only the even numbered particles")

	eer_input_group = parser.add_mutually_exclusive_group()
	eer_input_group.add_argument("--eer2x", action="store_true", help="Render EER file on 8k grid.")
	eer_input_group.add_argument("--eer4x", action="store_true", help="Render EER file on 16k grid.")

	# Parallelism
	parser.add_argument("--parallel",action="store_true")

	options, args = parser.parse_args()

	if options.parallel:
		parser.error("Parallelism not supported. Please use e2proc2dpar.py")

	if len(args) < 2:
		print("usage: " + usage)
		print("Please run '" + progname + " -h' for detailed options")
		sys.exit(1)

	try : options.step = int(options.step.split(",")[0]),int(options.step.split(",")[1])	# convert strings to tuple
	except:
		print("Invalid --step specification")
		sys.exit(1)

	if options.step != (0,1) and options.first:
		print('Invalid options. You used --first and --step.')
		print('The --step option contains both a step size and the first image to step from.')
		print('Please use only the --step option rather than --step and --first.')
		sys.exit(1)

	logid = E2init(sys.argv,options.ppid)

	optionlist = deque(get_optionlist(sys.argv[1:]))

	is_multiple_files = (len(args) > 1)

	if options.extractboxes:
		boxes = defaultdict(list)

	for inp_num, infile in enumerate(args, start=1):
		# inp_ext
		inp_ext = ".hdf" if infile[0] == ":" else os.path.splitext(infile)[1]

		# outfile, out_ext
		if options.output:
			outfile = changed_file_name(infile, options.output, inp_num, is_multiple_files)
			out_ext = os.path.splitext(outfile)[1]

			if out_ext == "" and is_multiple_files:
				out_ext = inp_ext
				outfile = outfile + out_ext

			if out_ext == ".lst":
				print("Output file extension may not be .lst: " + outfile)
				continue

		# out_ext == ".mrc"
		if not infile[0] == ":":
			if EMUtil.get_image_count(infile) == 1:
				if gimme_image_dimensions3D(infile)[2] == 1:
					if out_ext == ".mrc":
						if os.path.isfile(outfile):
							if infile == outfile:
								options.inplace = True
							else:
								os.remove(outfile)

		is_inp3d = False

		if not infile[0] == ":" and EMUtil.get_image_count(infile) == 1 and gimme_image_dimensions3D(infile)[2] != 1:
			is_inp3d = True

		# num_out_images, is_out3d
		if out_ext == inp_ext and infile[0] == ":":
			is_out3d = False
		if out_ext == inp_ext and not infile[0] == ":" and EMUtil.get_image_count(infile) == 1 and gimme_image_dimensions3D(infile)[2] != 1:
			is_out3d = True
		if out_ext == inp_ext and not infile[0] == ":" and not (EMUtil.get_image_count(infile) == 1 and gimme_image_dimensions3D(infile)[2] != 1):
			is_out3d = False
		if out_ext != inp_ext and out_ext == ".mrc":
			is_out3d = True
		if out_ext != inp_ext and out_ext != ".mrc":
			is_out3d = False

		# if all of *2* are NONE assign one
		if not (options.threed2threed or options.threed2twod or options.twod2threed):
			options.threed2threed = (    is_inp3d and     is_out3d)
			options.threed2twod   = (    is_inp3d and not is_out3d)
			options.twod2threed   = (not is_inp3d and     is_out3d)

		if options.average:
			averager = parsemodopt(options.averager)
			average = Averagers.get(averager[0], averager[1])

		fftavg = None

		n0 = options.first
		n1 = options.last

		d = EMData()
		threed_xsize = 0
		threed_ysize = 0
		nimg = 1

		# is_3d, nimg
		is_3d = False
		if options.threed2threed or options.threed2twod:
			d.read_image(infile, 0, True)

			nimg = d.get_zsize()

			if nimg == 1:
				print('Error: need 3D image to use this option')
				return
			else:
				if n1 > nimg:
					print('The value for --last is greater than the number of images in the input stack. Exiting')
					n1 = options.last

				if options.step[0] > n0:
					n0 = options.step[0]

				threed_xsize = d.get_xsize()
				threed_ysize = d.get_ysize()
		elif infile[0]==":":
			nimg=1
		else:
			nimg = EMUtil.get_image_count(infile)

			# reads header only
			[tomo_nx, tomo_ny, tomo_nz] = gimme_image_dimensions3D(infile)

			is_3d = (tomo_nz != 1)

		# n1
		plane = options.plane
		if not is_3d:
			if not (nimg > n1 >= 0):
				n1 = nimg - 1
		else:
			if plane in xyplanes:
				n1 = tomo_nz-1
			elif plane in xzplanes:
				n1 = tomo_ny-1
			elif plane in yzplanes:
				n1 = tomo_nx-1

			if 0 <= options.last < n1:
				n1 = options.last
			elif options.last > n1:
				print('The value for --last is greater than the number of images in the input stack.')
				print('It is being set to the maximum length of the images')
				n1 = tomo_nz-1

			threed = EMData()
			threed.read_image(infile)

		if options.step[0] > options.first:
			n0 = options.step[0]

		# inclusion/exclusion lists
		if options.list:
			image_ids = set(EMAN2.read_number_file(options.list))

		elif options.randomn > 0:
			if options.randomn >= nimg:
				imagelist = [1]*nimg
			else:
				imagelist = [0]*nimg
				for nk in range(options.randomn):
					i = random.randrange(nimg)
					if imagelist[i]:
						continue
					imagelist[i] = 1
		else:
			image_ids = range(nimg)

		if options.exclude:
			if "," in options.exclude or options.exclude.isdigit():
				for i in options.exclude.split(","):
					image_ids.remove(i)
			else:
				image_ids - EMAN2.read_number_file(options.exclude)

		# outfilename_no_ext, outfilename_ext when outfile specified
		if options.output:
			outfilename_no_ext = outfile[:-4]
			outfilename_ext = outfile[-3:]

			if outfilename_ext == "rcs" and outfile[-4:] == "mrcs":
				outfilename_ext = outfile[-4:]

		dummy = False

		for count, i in enumerate(range(n0, n1+1, options.step[1]), start=1):
			# ???
			if not i in image_ids:
				continue

			# Split
			if options.split > 1:
				outfile = outfilename_no_ext + ".%02d." % (i % options.split) + outfilename_ext

			# ???
			if not is_3d:
				if options.threed2threed or options.threed2twod:
					d = EMData()
					d.read_image(infile, 0, False, Region(0,0,i,threed_xsize,threed_ysize,1))
				elif infile[0] == ":":
					vals = infile.split(":")

					if len(vals) not in (3,4,5):
						print("Error: Specify new images as ':X:Y:f(x,y)' or ':X:Y:Z:f(x,y,z)', 0<=x<X, 0<=y<Y, 0<=z<Z")
						sys.exit(1)

					n_x = int(vals[1])
					n_y = int(vals[2])
					n_z = 1
					if len(vals) > 4: n_z = int(vals[3])

					if n_x <= 0 or n_y <= 0 or n_z <= 0:
						print("Error: Image dimensions must be positive integers:", n_x, n_y, n_z)
						sys.exit(1)

					func = "0"
					if len(vals) >= 4: func = vals[-1]

					try:
						x  = 0.0
						y  = 0.0
						z  = 0.0
						xn = 0.0
						yn = 0.0
						zn = 0.0
						nx = 1
						ny = 1
						nz = 1
						w = eval(func)
					except:
						print("Error: Syntax error in image expression '" + func + "'")
						sys.exit(1)

					d = image_from_formula(n_x, n_y, n_z, func)
				else:
					d = EMData()

					if (options.eer2x or options.eer4x) and infile[-4:] != ".eer":
						print("Error: --eer2x and --eer4x options can be used only with EER files.")
						sys.exit(1)

					if options.eer2x:
						img_type = IMAGE_EER2X
					elif options.eer4x:
						img_type = IMAGE_EER4X
					else:
						img_type = IMAGE_UNKNOWN

					d.read_image(infile, i, False, None, False, img_type)
			else:
				x, y, z = 0, 0, 0

				if plane in xyplanes:
					z, tomo_nz = i, 1
				elif plane in xzplanes:
					y, tomo_ny = i, 1
				elif plane in yzplanes:
					x, tomo_nx = i, 1

				roi = Region(x, y, z, tomo_nx, tomo_ny, tomo_nz)
				d = threed.get_clip(roi)
				d.set_size(tomo_nx, tomo_ny, tomo_nz)

			if not "outtype" in optionlist:
				optionlist.append("outtype")

			while optionlist:
				option1 = optionlist.pop()
				val = getattr(options, option1)
				val = val.pop(0) if isinstance(val, list) else val

				nx = d.get_xsize()
				ny = d.get_ysize()

				if option1 == "apix":
					apix = options.apix
					d.set_attr('apix_x', apix)
					d.set_attr('apix_y', apix)
					d.set_attr('apix_z', apix)

					try:
						d["ctf"].apix = apix
					except: pass

				if option1 == "process":
					processorname, param_dict = parsemodopt(val)

					if not param_dict: param_dict = {}

					# Parse the options to convert the image file name to EMData object
					for key in list(param_dict.keys()):
						if not str(param_dict[key]).isdigit():
							try:
								param_dict[key] = EMData(param_dict[key])
							except:
								pass

					if processorname in EMAN2.outplaceprocs:
						d = d.process(processorname, param_dict)
					else: d.process_inplace(processorname, param_dict)

				elif option1 == "extractboxes":
					try:
						bf = base_name(d["ptcl_source_image"])
						bl = d["ptcl_source_coord"]
						boxes[bf].append(bl)
						boxsize = d["nx"]
					except:
						pass

				elif option1 == "add":
					d.add(val)

				elif option1 == "mult":
					d.mult(options.mult)

				elif option1 == "calccont":
					f = d.process("math.rotationalsubtract").do_fft()

					if d["apix_x"] <= 0:
						raise Exception("Error: 'calccont' requires an A/pix value, which is missing in the input images")

					lopix = int(d["nx"]*d["apix_x"]/150.0)
					hipix = min(int(d["nx"] * d["apix_x"] / 25.0), old_div(d["ny"], 2) - 6)  # if A/pix is very large, this makes sure we get at least some info

					if lopix == hipix:
						lopix,hipix = 3,old_div(d["nx"],5)  # in case the A/pix value is drastically out of range

					r = f.calc_radial_dist(old_div(d["ny"],2),0,1.0,1)
					lo = sum(r[lopix:hipix]) / (hipix-lopix)
					hi = sum(r[hipix+1:-1]) / (len(r)-hipix-2)

					d["eval_contrast_lowres"] = old_div(lo,hi)

				elif option1 == "norefs" and d["ptcl_repr"] <= 0:
					continue

				elif option1 == "setsfpairs":
					dataf = d.do_fft()
					x0 = 0
					step = 0.5

					if i%2 == 0:
						sfcurve1 = dataf.calc_radial_dist(nx, x0, step)
					else:
						sfcurve2 = dataf.calc_radial_dist(nx, x0, step)

						for j in range(nx):
							if sfcurve1[j] > 0 and sfcurve2[j] > 0:
								sfcurve2[j] = sqrt(old_div(sfcurve1[j], sfcurve2[j]))
							else:
								sfcurve2[j] = 0

							dataf.apply_radial_func(x0, step, sfcurve2)
							d = dataf.do_ift()

				elif option1 == "fp":
					d = d.make_footprint(options.fp)

				elif option1 == "anisotropic":
					amount, angle = val

					rt=Transform({"type":"2d","alpha":angle})
					xf=rt*Transform([amount,0,0,0,0,1./amount,0,0,0,0,1,0])*rt.inverse()
					d.transform(xf)

				elif option1 == "scale":
					scale_f = val

					if scale_f != 1.0:
						d.scale(scale_f)

				elif option1 == "rotate":
					rotatef = val

					if rotatef != 0.0: d.rotate(rotatef,0,0)

				elif option1 == "translate":
					tdx, tdy = val

					if tdx != 0.0 or tdy != 0.0:
						d.translate(tdx,tdy,0.0)

				elif option1 == "clip":
					clipcx = old_div(nx,2)
					clipcy = old_div(ny,2)

					try: clipx,clipy,clipcx,clipcy = val
					except: clipx, clipy = val

					clipx, clipy = int(clipx),int(clipy)
					clipcx, clipcy = int(clipcx),int(clipcy)

					d = d.get_clip(Region(clipcx-old_div(clipx,2), clipcy-old_div(clipy,2), clipx, clipy))

					try: d.set_attr("avgnimg", d.get_attr("avgnimg"))
					except: pass

				elif option1 == "randomize":
					rnd = val

					t = Transform()
					t.set_params({"type":"2d", "alpha":random.uniform(-rnd[0],rnd[0]),
								  "mirror":random.randint(0,rnd[2]), "tx":random.uniform(-rnd[1],rnd[1]),
								  "ty":random.uniform(-rnd[1],rnd[1])})
					d.transform(t)

				elif option1 == "medianshrink":
					shrink_f = val

					if shrink_f > 1:
						d.process_inplace("math.medianshrink",{"n":shrink_f})

				elif option1 == "meanshrink":
					mshrink = val

					if mshrink > 1:
						d.process_inplace("math.meanshrink",{"n":mshrink})

				elif option1 == "fouriershrink":
					fshrink = val

					if fshrink > 1:
						d.process_inplace("math.fft.resample",{"n":fshrink})

				elif option1 == "headertransform":
					xfmode = val

					try: xform=d["xform.align2d"]
					except: print("Error: particle has no xform.align2d header value")

					if xfmode == 1: xform.invert()

					d.process_inplace("xform",{"transform":xform})

				elif option1 == "radon":
					d = d.do_radon()

				elif option1 == "average":
					average.add_image(d)
					continue

				elif option1 == "fftavg":
					if not fftavg:
						fftavg = EMData()
						fftavg.set_size(nx+2, ny)
						fftavg.set_complex(1)
						fftavg.to_zero()

					d.process_inplace("mask.ringmean")
					d.process_inplace("normalize")
					df = d.do_fft()
					df.mult(df.get_ysize())
					fftavg.add_incoherent(df)

					continue

				elif option1 == "calcsf":
					dataf = d.do_fft()
					curve = dataf.calc_radial_dist(old_div(ny,2), 0, 1.0,True)
					curve=[old_div(i,(dataf["nx"]*dataf["ny"]*dataf["nz"])) for i in curve]

					sf_dx = 1.0 / (d["apix_x"] * ny)
					Util.save_data(0, sf_dx, curve, options.calcsf)

				elif option1 == "interlv":
					d.append_image(outfile, EMUtil.get_image_ext_type(options.outtype))
					d.read_image(options.interlv, i)

				elif option1 == "outtype":
					if i == 0:
						original_outfile = outfile

					if options.outtype in ["mrc", "pif", "png", "pgm"]:
						if n1 != 0:
							outfile = "%03d." % (i + 100) + original_outfile
					elif options.outtype == "spidersingle":
						if n1 != 0:
							if i == 0:
								nameprefix = outfile[:-4] if outfile.find('.spi') > 0 else outfile

							spiderformat = "%s%%0%dd.spi" % (nameprefix, int(math.log10(n1+1-n0))+1)
							outfile = spiderformat % i

					if options.fixintscaling:
						if options.fixintscaling == "sane":
							sca = 2.5
							d["render_min"] = d["mean"] - d["sigma"]*sca
							d["render_max"] = d["mean"] + d["sigma"]*sca
						elif options.fixintscaling == "full":
							d["render_min"]=d["minimum"]*1.001
							d["render_max"]=d["maximum"]*1.001
						else:
							try:
								sca = float(options.fixintscaling)
							except:
								sca = 2.5

								print("Warning: bad fixintscaling value - 2.5 used")

							d["render_min"] = d["mean"] - d["sigma"]*sca
							d["render_max"] = d["mean"] + d["sigma"]*sca

					elif options.outmode != "float":
							# This sets the minimum and maximum values to the range
							# for the specified type, which should result in no rescaling
							outmode = EMAN2.file_mode_map[options.outmode]

							d["render_min"] = EMAN2.file_mode_range[outmode][0]
							d["render_max"] = EMAN2.file_mode_range[outmode][1]

					if options.average > 1:
						average.add_image(d)
						if count%options.average == 0:
							d=average.finish()

					if not options.average and (options.average<=1 or count%options.average==0):  # skip writing the input image to output file
						# write processed image to file

						out_type = EMUtil.get_image_ext_type(options.outtype)
						out_mode = EMAN2.file_mode_map[options.outmode]
						not_swap = not options.swap

						if options.threed2threed or options.twod2threed:    # output a single 3D image
							if not dummy:
								if options.list:
									f = open(options.list,'r')
									lines = f.read().split(',')

									f.close()
									z = len(lines)

								elif options.exclude:
									f = open(options.exclude,'r')
									lines = f.read().split(',')

									f.close()
									z = nimg - len(lines)

								else:
									z = nimg

								out3d_img = EMData(d.get_xsize(), d.get_ysize(), z)

								try:
									out3d_img["apix_x"] = d["apix_x"]
									out3d_img["apix_y"] = d["apix_y"]
									out3d_img["apix_z"] = d["apix_z"]
								except:
									pass

								out3d_img.write_image(outfile, 0, out_type, False, None, out_mode, not_swap)
								dummy = True

							if options.list or options.exclude:
								if imagelist[i] != 0:
									region = Region(0, 0, imagelist[0:i].count(1), d.get_xsize(), d.get_ysize(), 1)
							else:
								region = Region(0, 0, i, d.get_xsize(), d.get_ysize(), 1)

							d.write_image(outfile, 0, out_type, False, region, out_mode, not_swap)

						elif options.unstacking:  # output a series numbered single image files
							out_name = os.path.splitext(outfile)[0]+'-'+str(i+1).zfill(len(str(nimg)))+os.path.splitext(outfile)[-1]
							if d["sigma"] == 0:
								if not options.writejunk:
									continue

							d.write_image(out_name, 0, out_type, False, None, out_mode, not_swap)

						else:   # output a single 2D image or a 2D stack
							# optionally replace the output image with its rotational average
							if options.rotavg:
								rd = d.calc_radial_dist(d["nx"],0,0.5,0)
								d = EMData(len(rd),1,1)

								d[:len(rd)] = rd[:len(rd)]

							if d["sigma"] == 0:
								if not options.writejunk:
									continue

							if options.output:
								if options.inplace:
									if options.compressbits>=0:
										d.write_compressed(outfile,i,options.compressbits,nooutliers=True)
									else:
										d.write_image(outfile, i, out_type, False, None, out_mode, not_swap)
								else:  # append the image
									if options.compressbits>=0:
										d.write_compressed(outfile,-1,options.compressbits,nooutliers=True)
									else:
										d.write_image(outfile, -1, out_type, False, None, out_mode, not_swap)

		# end of image loop

		if options.average:
			avg = average.finish()

			if options.inplace:
				if options.compressbits >= 0:
					avg.write_compressed(outfile,0,options.compressbits,nooutliers=True)
				else: avg.write_image(outfile,0)
			else:
				if options.compressbits >= 0:
					avg.write_compressed(outfile,-1,options.compressbits,nooutliers=True)
				else: avg.write_image(outfile,-1)

		if options.fftavg:
			fftavg.mult(1.0 / sqrt(n1 - n0 + 1))  # n1-n0 or count
			fftavg.write_image(options.fftavg, 0)

			curve = fftavg.calc_radial_dist(ny, 0, 0.5, 1)

			sf_dx = 1.0 / (apix * 2.0 * ny)
			Util.save_data(0, sf_dx, curve, options.fftavg+".txt")

		if options.extractboxes:
			for k in list(boxes.keys()):
				with open(k+".box","w") as out:
					for c in boxes[k]:
						out.write("{:1d}\t{:1d}\t{:1d}\t{:1d}\n".format(int(c[0]-old_div(boxsize,2)),int(c[1]-old_div(boxsize,2)),int(boxsize),int(boxsize)))

	E2end(logid)


if __name__ == "__main__":
	main()
