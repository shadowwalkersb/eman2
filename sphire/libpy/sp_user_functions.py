#
# Author: Markus Stabrin 2019 (markus.stabrin@mpi-dortmund.mpg.de)
# Author: Fabian Schoenfeld 2019 (fabian.schoenfeld@mpi-dortmund.mpg.de)
# Author: Thorsten Wagner 2019 (thorsten.wagner@mpi-dortmund.mpg.de)
# Author: Tapu Shaikh 2019 (tapu.shaikh@mpi-dortmund.mpg.de)
# Author: Adnan Ali 2019 (adnan.ali@mpi-dortmund.mpg.de)
# Author: Luca Lusnig 2019 (luca.lusnig@mpi-dortmund.mpg.de)
# Author: Toshio Moriya 2019 (toshio.moriya@kek.jp)
# Author: Pawel A.Penczek, 09/09/2006 (Pawel.A.Penczek@uth.tmc.edu)
#
# Copyright (c) 2019 Max Planck Institute of Molecular Physiology
# Copyright (c) 2000-2006 The University of Texas - Houston Medical School
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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307 USA
#

#  This file contains fuctions that perform project-dependent tasks in various
#   alignment programs, for example preparation of the reference during 2D and 3D alignment
#  To write you own function, modify the existing one (for example, wei_func is a version
#   of ref_ali2d) and add the name to the factory.  Once it is done, the function can be called
#   from appropriate application, in this case "sxali2d_c.py ...  --function=wei_func
# 

def ref_ali2d( ref_data ):
	from sp_utilities    import print_msg
	from sp_filter       import fit_tanh, filt_tanl
	from sp_utilities    import center_2D
	#  Prepare the reference in 2D alignment, i.e., low-pass filter and center.
	#  Input: list ref_data
	#   0 - mask
	#   1 - center flag
	#   2 - raw average
	#   3 - fsc result
	#  Output: filtered, centered, and masked reference image
	#  apply filtration (FRC) to reference image:
	global  ref_ali2d_counter
	ref_ali2d_counter += 1
	print_msg("ref_ali2d   #%6d\n"%(ref_ali2d_counter))
	fl, aa = fit_tanh(ref_data[3])
	aa = min(aa, 0.2)
	fl = max(min(0.4,fl),0.12)
	msg = "Tangent filter:  cut-off frequency = %10.3f        fall-off = %10.3f\n"%(fl, aa)
	print_msg(msg)
	st = Util.infomask(ref_data[2], ref_data[0], True)
	tavg = filt_tanl((ref_data[2]-st[0])*ref_data[0], fl, aa)
	cs = [0.0]*2
	if(ref_data[1] > 0):
		tavg, cs[0], cs[1] = center_2D(tavg, ref_data[1], self_defined_reference = ref_data[0])
		msg = "Center x =      %10.3f        Center y       = %10.3f\n"%(cs[0], cs[1])
		print_msg(msg)
	return  tavg, cs

def ref_ali2d_c( ref_data ):
	from sp_utilities    import print_msg
	from sp_filter       import fit_tanh, filt_tanl
	from sp_utilities    import center_2D
	#  Prepare the reference in 2D alignment, i.e., low-pass filter and center.
	#  Input: list ref_data
	#   0 - mask
	#   1 - center flag
	#   2 - raw average
	#   3 - fsc result
	#  Output: filtered, centered, and masked reference image
	#  apply filtration (FRC) to reference image:
	global  ref_ali2d_counter
	ref_ali2d_counter += 1
	print_msg("ref_ali2d   #%6d\n"%(ref_ali2d_counter))
	fl = min(0.1+ref_ali2d_counter*0.003, 0.4)
	aa = 0.1
	msg = "Tangent filter:  cut-off frequency = %10.3f        fall-off = %10.3f\n"%(fl, aa)
	print_msg(msg)
	tavg = filt_tanl(ref_data[2], fl, aa)
	cs = [0.0]*2
	if(ref_data[1] > 0):
		tavg, cs[0], cs[1] = center_2D(tavg, ref_data[1])
		msg = "Center x = %10.3f, y       = %10.3f\n"%(cs[0], cs[1])
		print_msg(msg)
	return  tavg, cs

def julien( ref_data ):
        from sp_utilities    import print_msg
        from sp_filter       import fit_tanh, filt_tanl
        from sp_utilities    import center_2D
        #  Prepare the reference in 2D alignment, i.e., low-pass filter and center.
        #  Input: list ref_data
        #   0 - mask
        #   1 - center flag
        #   2 - raw average
        #   3 - fsc result
        #  Output: filtered, centered, and masked reference image
        #  apply filtration (FRC) to reference image:
        global  ref_ali2d_counter
        ref_ali2d_counter += 1
        ref_ali2d_counter  = ref_ali2d_counter % 50
        print_msg("ref_ali2d   #%6d\n"%(ref_ali2d_counter))
        fl = min(0.1+ref_ali2d_counter*0.003, 0.4)
        aa = 0.1
        msg = "Tangent filter:  cut-off frequency = %10.3f        fall-off = %10.3f\n"%(fl, aa)
        print_msg(msg)
        tavg = filt_tanl(ref_data[2], fl, aa)
        cs = [0.0]*2
        if ref_data[1] > 0:
                tavg, cs[0], cs[1] = center_2D(tavg, ref_data[1])
                msg = "Center x = %10.3f, y       = %10.3f\n"%(cs[0], cs[1])
                print_msg(msg)
        return  tavg, cs

def ref_ali2d_m( ref_data ):
	from sp_utilities    import print_msg
	from sp_filter       import fit_tanh, filt_tanl
	from sp_utilities    import center_2D
	#  Prepare the reference in 2D alignment, i.e., low-pass filter and center.
	#  Input: list ref_data
	#   0 - mask
	#   1 - center flag
	#   2 - raw average
	#   3 - fsc result
	#  Output: filtered, centered, and masked reference image
	#  apply filtration (FRC) to reference image:
	global  ref_ali2d_counter
	ref_ali2d_counter += 1
	print_msg("ref_ali2d   #%6d\n"%(ref_ali2d_counter))
	fl = 0.4
	aa = 0.2
	msg = "Tangent filter:  cut-off frequency = %10.3f        fall-off = %10.3f\n"%(fl, aa)
	print_msg(msg)
	tavg = filt_tanl(ref_data[2], fl, aa)
	cs = [0.0]*2
	if(ref_data[1] > 0):
		tavg, cs[0], cs[1] = center_2D(tavg, ref_data[1])
		msg = "Center x = %10.3f, y = %10.3f\n"%(cs[0], cs[1])
		print_msg(msg)
	return  tavg, cs

def ref_ali3dm( refdata ):
	from sp_filter import fit_tanh, filt_tanl
	from sp_utilities import get_im
	from sp_fundamentals import rot_shift3D
	import os

	numref = refdata[0]
	outdir = refdata[1]
	fscc   = refdata[2]
	total_iter = refdata[3]
	#varf   = refdata[4]
	mask   = refdata[5]

	sxprint('filter every volume at (0.4, 0.1)')
	for iref in range(numref):
		v = get_im(os.path.join(outdir, "vol%04d.hdf"%total_iter), iref)
		v = filt_tanl(v, 0.4, 0.1)
		v *= mask
		v.write_image(os.path.join(outdir, "volf%04d.hdf"%total_iter), iref)
		
def ref_sort3d(refdata):
	from sp_filter import fit_tanh, filt_tanl
	from sp_utilities import get_im
	from sp_fundamentals import rot_shift3D
	import os
	numref          = refdata[0]
	outdir          = refdata[1]
	fscc            = refdata[2]
	total_iter      = refdata[3]
	#varf           = refdata[4]
	mask            = refdata[5]
	low_pass_filter = refdata[6]
	import time
	from time import strftime, localtime
	theme='filter every volume at (%f, 0.1)'%low_pass_filter
	line = strftime("%Y-%m-%d_%H:%M:%S", localtime()) + " =>"
	sxprint((line+theme))
	sxprint('filter every volume at (%f, 0.1)'%low_pass_filter)
	for iref in range(numref):
		v = get_im(os.path.join(outdir, "vol%04d.hdf"%total_iter), iref)
		v = filt_tanl(v, low_pass_filter, 0.1)
		v *= mask
		v.write_image(os.path.join(outdir, "volf%04d.hdf"%total_iter), iref)

def ref_ali3dm_ali_50S( refdata ):
	from sp_filter       import fit_tanh, filt_tanl
	from sp_utilities    import get_im
	from sp_fundamentals import rot_shift3D
	import  os

	numref     = refdata[0]
	outdir     = refdata[1]
	fscc       = refdata[2]
	total_iter = refdata[3]
	varf       = refdata[4]

	#mask_50S = get_im( "mask-50S.spi" )

	flmin = 1.0
	flmax = -1.0
	for iref in range(numref):
		fl, aa = fit_tanh( fscc[iref] )
		if (fl < flmin):
			flmin = fl
			aamin = aa
		if (fl > flmax):
			flmax = fl
			aamax = aa
		sxprint('iref,fl,aa: ', iref, fl, aa)
		# filter to minimum resolution
	sxprint('flmin,aamin:', flmin, aamin)
	for iref in range(numref):
		v = get_im(os.path.join(outdir, "vol%04d.hdf"%total_iter), iref)
		v = filt_tanl(v, flmin, aamin)
		
		if ali50s:
			from sp_utilities    import get_params3D, set_params3D, combine_params3
			from sp_applications import ali_vol_shift, ali_vol_rotate
			if iref==0:
				v50S_ref = alivol_mask_getref( v, mask_50S )
			else:
				v = alivol_mask( v, v50S_ref, mask_50S )

		if not(varf is None):
			sxprint('filtering by fourier variance')
			v.filter_by_image( varf )
	
		v.write_image(os.path.join(outdir, "volf%04d.hdf"%total_iter), iref)

def ref_random( ref_data ):
	from sp_utilities    import print_msg
	from sp_filter       import fit_tanh, filt_tanl
	from sp_utilities    import center_2D
	#  Prepare the reference in 2D alignment, i.e., low-pass filter and center.
	#  Input: list ref_data
	#   0 - mask
	#   1 - center flag
	#   2 - raw average
	#   3 - fsc result
	#  Output: filtered, centered, and masked reference image
	#  apply filtration (FRC) to reference image:
	global  ref_ali2d_counter
	ref_ali2d_counter += 1
	print_msg("ref_ali2d   #%6d\n"%(ref_ali2d_counter))
	"""
	fl, aa = fit_tanh(ref_data[3])
	msg = "Tangent filter:  cut-off frequency = %10.3f        fall-off = %10.3f\n"%(fl, aa)
	print_msg(msg)
	tavg = filt_tanl(ref_data[2], fl, aa)
	"""	
	# ONE CAN USE BUTTERWORTH FILTER
	#lowfq, highfq = filt_params( ref_data[3], low = 0.1)
	#tavg  = filt_btwl( ref_data[2], lowfq, highfq)
	#msg = "Low frequency = %10.3f        High frequency = %10.3f\n"%(lowfq, highfq)
	#print_msg(msg)
	#  ONE CAN CHANGE THE MASK AS THE PROGRAM PROGRESSES
	#from morphology import adaptive_mask
	#ref_data[0] = adaptive_mask(tavg)
	#  CENTER
	cs = [0.0]*2
	tavg, cs[0], cs[1] = center_2D(ref_data[2], ref_data[1])
	'''
	from math import exp
	nx = tavg.get_xsize()
	ft = []
	good = True
	for i in xrange(nx):
		if(good):
			ex = exp((float(i)/float(nx))**2/2.0/0.12**2)
			if(ex>100.): good = False
		ft.append(ex)
	from sp_filter import filt_table
	tavg = filt_table(tavg, ft)
	'''
	if(ref_data[1] > 0):
		msg = "Center x =      %10.3f        Center y       = %10.3f\n"%(cs[0], cs[1])
		print_msg(msg)
	return  tavg, cs

def ref_ali3d( ref_data ):
	from sp_utilities      import print_msg
	from sp_filter         import fit_tanh, filt_tanl
	from sp_fundamentals   import fshift
	from sp_morphology     import threshold
	#  Prepare the reference in 3D alignment, i.e., low-pass filter and center.
	#  Input: list ref_data
	#   0 - mask
	#   1 - center flag
	#   2 - raw average
	#   3 - fsc result
	#  Output: filtered, centered, and masked reference image
	#  apply filtration (FSC) to reference image:

	global  ref_ali2d_counter
	ref_ali2d_counter += 1

	fl = ref_data[2].cmp("dot",ref_data[2], {"negative":0, "mask":ref_data[0]} )
	print_msg("ref_ali3d    Step = %5d        GOAL = %10.3e\n"%(ref_ali2d_counter,fl))

	cs = [0.0]*3
	#filt = filt_from_fsc(fscc, 0.05)
	#vol  = filt_table(vol, filt)
	# here figure the filtration parameters and filter vol for the  next iteration
	#fl, fh = filt_params(res)
	#vol	= filt_btwl(vol, fl, fh)
	# store the filtered reference volume
	#lk = 0
	#while(res[1][lk] >0.9 and res[0][lk]<0.25):
	#	lk+=1
	#fl = res[0][lk]
	#fh = min(fl+0.1,0.49)
	#vol = filt_btwl(vol, fl, fh)
	#fl, fh = filt_params(fscc)
	#print "fl, fh, iter",fl,fh,Iter
	#vol = filt_btwl(vol, fl, fh)
	stat = Util.infomask(ref_data[2], ref_data[0], False)
	volf = ref_data[2] - stat[0]
	Util.mul_scalar(volf, 1.0/stat[1])
	#volf = threshold(volf)
	Util.mul_img(volf, ref_data[0])
	fl, aa = fit_tanh(ref_data[3])
	#fl = 0.4
	#aa = 0.1
	msg = "Tangent filter:  cut-off frequency = %10.3f        fall-off = %10.3f\n"%(fl, aa)
	print_msg(msg)
	volf = filt_tanl(volf, fl, aa)
	if ref_data[1] == 1:
		cs = volf.phase_cog()
		msg = "Center x = %10.3f        Center y = %10.3f        Center z = %10.3f\n"%(cs[0], cs[1], cs[2])
		print_msg(msg)
		volf  = fshift(volf, -cs[0], -cs[1], -cs[2])
	return  volf, cs

def helical( ref_data ):
	from sp_utilities      import print_msg
	from sp_filter         import fit_tanh, filt_tanl
	from sp_morphology     import threshold
	#  Prepare the reference in helical refinement, i.e., low-pass filter .
	#  Input: list ref_data
	#   0 - raw volume
	#  Output: filtered, and masked reference image

	global  ref_ali2d_counter
	ref_ali2d_counter += 1
	print_msg("helical   #%6d\n"%(ref_ali2d_counter))
	stat = Util.infomask(ref_data[0], None, True)
	volf = ref_data[0] - stat[0]
	nx = volf.get_xsize()
	ny = volf.get_ysize()
	nz = volf.get_zsize()
	#for i in xrange(nz):
	#	volf.insert_clip(filt_tanl(volf.get_clip(Region(0,0,i,nx,ny,1)),0.4,0.1),[0,0,i])

	volf = threshold(volf)
	fl = 0.45#0.17
	aa = 0.1
	msg = "Tangent filter:  cut-off frequency = %10.3f        fall-off = %10.3f\n"%(fl, aa)
	print_msg(msg)
	volf = filt_tanl(volf, fl, aa)
	return  volf#,[0.,0.,0.]

def helical2( ref_data ):
	from sp_utilities      import print_msg
	from sp_filter	    import fit_tanh, filt_tanl
	from sp_morphology     import threshold
	#  Prepare the reference in helical refinement, i.e., low-pass filter.
	#  Input: list ref_data
	#  2 - raw volume
	#  Output: filtered, and masked reference image

	global  ref_ali2d_counter
	ref_ali2d_counter += 1
	print_msg("helical2   #%6d\n"%(ref_ali2d_counter))
	volf = ref_data[0]
	#stat = Util.infomask(ref_data[1], None, True)
	#volf = ref_data[0] - stat[0]
	#volf = threshold(volf)
	fl = 0.17
	aa = 0.2
	msg = "Tangent filter:  cut-off frequency = %10.3f	  fall-off = %10.3f\n"%(fl, aa)
	print_msg(msg)
	volf = filt_tanl(volf, fl, aa)
	return  volf


def reference3( ref_data ):
	from sp_utilities      import print_msg
	from sp_filter         import fit_tanh1, filt_tanl
	from sp_fundamentals   import fshift
	from sp_morphology     import threshold
	#  Prepare the reference in 3D alignment, i.e., low-pass filter and center.
	#  Input: list ref_data
	#   0 - mask
	#   1 - center flag
	#   2 - raw average
	#   3 - fsc result
	#  Output: filtered, centered, and masked reference image
	#  apply filtration (FSC) to reference image:

	print_msg("reference3\n")
	cs = [0.0]*3

	stat = Util.infomask(ref_data[2], ref_data[0], False)
	volf = ref_data[2] - stat[0]
	Util.mul_scalar(volf, 1.0/stat[1])
	volf = threshold(volf)
	Util.mul_img(volf, ref_data[0])
	#fl, aa = fit_tanh1(ref_data[3], 0.1)
	fl = 0.2
	aa = 0.2
	msg = "Tangent filter:  cut-off frequency = %10.3f        fall-off = %10.3f\n"%(fl, aa)
	print_msg(msg)
	volf = filt_tanl(volf, fl, aa)
	if ref_data[1] == 1:
		cs = volf.phase_cog()
		msg = "Center x = %10.3f        Center y = %10.3f        Center z = %10.3f\n"%(cs[0], cs[1], cs[2])
		print_msg(msg)
		volf  = fshift(volf, -cs[0], -cs[1], -cs[2])
	return  volf, cs

def reference4( ref_data ):
	from sp_utilities      import print_msg
	from sp_filter         import fit_tanh, filt_tanl, filt_gaussl
	from sp_fundamentals   import fshift, fft
	from sp_morphology     import threshold
	#  Prepare the reference in 3D alignment, i.e., low-pass filter and center.
	#  Input: list ref_data
	#   0 - mask
	#   1 - center flag
	#   2 - raw average
	#   3 - fsc result
	#  Output: filtered, centered, and masked reference image
	#  apply filtration (FSC) to reference image:

	#print_msg("reference4\n")
	cs = [0.0]*3

	stat = Util.infomask(ref_data[2], ref_data[0], False)
	volf = ref_data[2] - stat[0]
	Util.mul_scalar(volf, 1.0/stat[1])
	volf = threshold(volf)
	#Util.mul_img(volf, ref_data[0])
	#fl, aa = fit_tanh(ref_data[3])
	fl = 0.25
	aa = 0.1
	#msg = "Tangent filter:  cut-off frequency = %10.3f        fall-off = %10.3f\n"%(fl, aa)
	#print_msg(msg)
	volf = fft(filt_gaussl(filt_tanl(fft(volf),0.35,0.2),0.3))
	if ref_data[1] == 1:
		cs = volf.phase_cog()
		msg = "Center x = %10.3f        Center y = %10.3f        Center z = %10.3f\n"%(cs[0], cs[1], cs[2])
		print_msg(msg)
		volf  = fshift(volf, -cs[0], -cs[1], -cs[2])
	return  volf, cs

def ref_aliB_cone( ref_data ):
	from sp_utilities      import print_msg
	from sp_filter         import fit_tanh, filt_tanl
	from sp_fundamentals   import fshift
	from sp_morphology     import threshold
	from math           import sqrt
	#  Prepare the reference in 3D alignment, i.e., low-pass filter and center.
	#  Input: list ref_data
	#   0 - mask
	#   1 - reference PW
	#   2 - raw average
	#   3 - fsc result
	#  Output: filtered, centered, and masked reference image
	#  apply filtration (FSC) to reference image:

	print_msg("ref_aliB_cone\n")
	#cs = [0.0]*3

	stat = Util.infomask(ref_data[2], None, True)
	volf = ref_data[2] - stat[0]
	Util.mul_scalar(volf, 1.0/stat[1])

	volf = threshold(volf)
	Util.mul_img(volf, ref_data[0])

	from  sp_fundamentals  import  rops_table
	pwem = rops_table(volf)
	ftb = []
	for idum in range(len(pwem)):
		ftb.append(sqrt(ref_data[1][idum]/pwem[idum]))
	from sp_filter import filt_table
	volf = filt_table(volf, ftb)

	fl, aa = fit_tanh(ref_data[3])
	#fl = 0.41
	#aa = 0.15
	msg = "Tangent filter:  cut-off frequency = %10.3f        fall-off = %10.3f\n"%(fl, aa)
	print_msg(msg)
	volf = filt_tanl(volf, fl, aa)
	stat = Util.infomask(volf, None, True)
	volf -= stat[0]
	Util.mul_scalar(volf, 1.0/stat[1])
	"""
	if(ref_data[1] == 1):
		cs    = volf.phase_cog()
		msg = "Center x = %10.3f        Center y = %10.3f        Center z = %10.3f\n"%(cs[0], cs[1], cs[2])
		print_msg(msg)
		volf  = fshift(volf, -cs[0], -cs[1], -cs[2])
	"""
	return  volf

def ref_7grp( ref_data ):
	from sp_utilities      import print_msg
	from sp_filter         import fit_tanh, filt_tanl, filt_gaussinv
	from sp_fundamentals   import fshift
	from sp_morphology     import threshold
	from math           import sqrt
	#  Prepare the reference in 3D alignment, i.e., low-pass filter and center.
	#  Input: list ref_data
	#   0 - mask
	#   1 - center flag
	#   2 - raw average
	#   3 - fsc result
	#  Output: filtered, centered, and masked reference image
	#  apply filtration (FSC) to reference image:
	#cs = [0.0]*3

	stat = Util.infomask(ref_data[2], None, False)
	volf = ref_data[2] - stat[0]
	Util.mul_scalar(volf, 1.0/stat[1])
	volf = Util.muln_img(threshold(volf), ref_data[0])

	fl, aa = fit_tanh(ref_data[3])
	msg = "Tangent filter:  cut-off frequency = %10.3f        fall-off = %10.3f\n"%(fl, aa)
	print_msg(msg)
	volf = filt_tanl(volf, fl, aa)
	if(ref_data[1] == 1):
		cs    = volf.phase_cog()
		msg = "Center x =	%10.3f        Center y       = %10.3f        Center z       = %10.3f\n"%(cs[0], cs[1], cs[2])
		print_msg(msg)
		volf  = fshift(volf, -cs[0], -cs[1], -cs[2])
	B_factor = 10.0
	volf = filt_gaussinv( volf, 10.0 )
	return  volf,cs

def spruce_up( ref_data ):
	from sp_utilities      import print_msg
	from sp_filter         import filt_tanl, fit_tanh
	from sp_morphology     import threshold
	#  Prepare the reference in 3D alignment, i.e., low-pass filter and center.
	#  Input: list ref_data
	#   0 - mask
	#   1 - center flag
	#   2 - raw average
	#   3 - fsc result
	#  Output: filtered, centered, and masked reference image
	#  apply filtration (FSC) to reference image:

	print_msg("Changed4 spruce_up\n")
	cs = [0.0]*3

	stat = Util.infomask(ref_data[2], None, True)
	volf = ref_data[2] - stat[0]
	Util.mul_scalar(volf, 1.0/stat[1])
	volf = threshold(volf)
	# Apply B-factor
	from sp_filter import filt_gaussinv
	from math import sqrt
	B = 1.0/sqrt(2.*14.0)
	volf = filt_gaussinv(volf, B, False)
	nx = volf.get_xsize()
	from sp_utilities import model_circle
	stat = Util.infomask(volf, model_circle(nx//2-2,nx,nx,nx)-model_circle(nx//2-6,nx,nx,nx), True)

	volf -= stat[0]
	Util.mul_img(volf, ref_data[0])
	fl, aa = fit_tanh(ref_data[3])
	#fl = 0.35
	#aa = 0.1
	aa /= 2
	msg = "Tangent filter:  cut-off frequency = %10.3f        fall-off = %10.3f\n"%(fl, aa)
	print_msg(msg)
	volf = filt_tanl(volf, fl, aa)
	return  volf, cs

def spruce_up_variance( ref_data ):
	from sp_utilities      import print_msg
	from sp_filter         import filt_tanl, fit_tanh, filt_gaussl
	from sp_morphology     import threshold
	#  Prepare the reference in 3D alignment, i.e., low-pass filter and center.
	#  Input: list ref_data
	#   0 - mask
	#   1 - center flag
	#   2 - raw average
	#   3 - fsc result
	#   4 1.0/variance
	#  Output: filtered, centered, and masked reference image
	#  apply filtration (FSC) to reference image:
	mask   = ref_data[0]
	center = ref_data[1]
	vol    = ref_data[2]
	fscc   = ref_data[3]
	varf   = ref_data[4]

	print_msg("spruce_up with variance\n")
	cs = [0.0]*3

	if not(varf is None):
		volf = vol.filter_by_image(varf)

	#fl, aa = fit_tanh(ref_data[3])
	fl = 0.22
	aa = 0.15
	msg = "Tangent filter:  cut-off frequency = %10.3f        fall-off = %10.3f\n"%(fl, aa)
	print_msg(msg)
	volf = filt_tanl(volf, fl, aa)

	stat = Util.infomask(volf, None, True)
	volf = volf - stat[0]
	Util.mul_scalar(volf, 1.0/stat[1])

	from sp_utilities import model_circle
	nx = volf.get_xsize()
	stat = Util.infomask(volf, model_circle(nx//2-2,nx,nx,nx)-model_circle(nx//2-6,nx,nx,nx), True)

	volf -= stat[0]
	Util.mul_img(volf, mask)

	volf = threshold(volf)
	
	volf = filt_gaussl(volf, 0.4)
	return  volf, cs

def minfilt( fscc ):
	from sp_filter import fit_tanh
	numref = len(fscc)
	flmin = 1.0
	flmax = -1.0
	for iref in range(numref):
		fl, aa = fit_tanh( fscc[iref] )
		if (fl < flmin):
			flmin = fl
			aamin = aa
			idmin = iref
		if (fl > flmax):
			flmax = fl
			aamax = aa
	return flmin,aamin,idmin

def ref_ali3dm_new( refdata ):
	from sp_utilities    import print_msg
	from sp_utilities    import model_circle, get_im
	from sp_filter       import filt_tanl, filt_gaussl, filt_table
	from sp_morphology   import threshold
	from sp_fundamentals import rops_table
	from sp_alignment    import ali_nvol
	from math         import sqrt
	import   os

	numref     = refdata[0]
	outdir     = refdata[1]
	fscc       = refdata[2]
	total_iter = refdata[3]
	varf       = refdata[4]
	mask       = refdata[5]
	ali50S     = refdata[6]

	if fscc is None:
		flmin = 0.38
		aamin = 0.1
		idmin = 0
	else:
		flmin, aamin, idmin = minfilt( fscc )
		aamin /= 2.0
	msg = "Minimum tangent filter derived from volume %2d:  cut-off frequency = %10.3f, fall-off = %10.3f\n"%(idmin, flmin, aamin)
	print_msg(msg)

	vol = []
	for i in range(numref):
		vol.append(get_im( os.path.join(outdir, "vol%04d.hdf"%total_iter), i ))
		stat = Util.infomask( vol[i], mask, False )
		vol[i] -= stat[0]
		vol[i] /= stat[1]
		vol[i] *= mask
		vol[i] = threshold(vol[i])
	del stat

	reftab = rops_table( vol[idmin] )
	for i in range(numref):
		if(i != idmin):
			vtab = rops_table( vol[i] )
			ftab = [None]*len(vtab)
			for j in range(len(vtab)):
		        	ftab[j] = sqrt( reftab[j]/vtab[j] )
			vol[i] = filt_table( vol[i], ftab )

	if ali50S:
		vol = ali_nvol(vol, get_im( "mask-50S.spi" ))
	for i in range(numref):
		if(not (varf is None) ):   vol[i] = vol[i].filter_by_image( varf )
		filt_tanl( vol[i], flmin, aamin ).write_image( os.path.join(outdir, "volf%04d.hdf" % total_iter), i )

def spruce_up_var_m( refdata ):
	from sp_utilities  import print_msg
	from sp_utilities  import model_circle, get_im
	from sp_filter     import filt_tanl, filt_gaussl
	from sp_morphology import threshold
	import os

	numref     = refdata[0]
	outdir     = refdata[1]
	fscc       = refdata[2]
	total_iter = refdata[3]
	varf       = refdata[4]
	mask       = refdata[5]
	ali50S     = refdata[6]

	if ali50S:
		mask_50S = get_im( "mask-50S.spi" )


	if fscc is None:
		flmin = 0.4
		aamin = 0.1
	else:
		flmin,aamin,idmin=minfilt( fscc )
		aamin = aamin

	msg = "Minimum tangent filter:  cut-off frequency = %10.3f     fall-off = %10.3f\n"%(fflmin, aamin)
	print_msg(msg)

	for i in range(numref):
		volf = get_im( os.path.join(outdir, "vol%04d.hdf"% total_iter) , i )
		if(not (varf is None) ):   volf = volf.filter_by_image( varf )
		volf = filt_tanl(volf, flmin, aamin)
		stat = Util.infomask(volf, mask, True)
		volf -= stat[0]
		Util.mul_scalar(volf, 1.0/stat[1])

		nx = volf.get_xsize()
		stat = Util.infomask(volf,model_circle(nx//2-2,nx,nx,nx)-model_circle(nx//2-6,nx,nx,nx), True)
		volf -= stat[0]
		Util.mul_img( volf, mask )

		volf = threshold(volf)
		volf = filt_gaussl( volf, 0.4)

		if ali50S:
			if i==0:
				v50S_0 = volf.copy()
				v50S_0 *= mask_50S
			else:
				from sp_applications import ali_vol_3
				from sp_fundamentals import rot_shift3D
				v50S_i = volf.copy()
				v50S_i *= mask_50S

				params = ali_vol_3(v50S_i, v50S_0, 10.0, 0.5, mask=mask_50S)
				volf = rot_shift3D( volf, params[0], params[1], params[2], params[3], params[4], params[5], 1.0)

		volf.write_image( os.path.join(outdir, "volf%04d.hdf"%total_iter), i )

def steady( ref_data ):
	from sp_utilities    import print_msg
	from sp_filter       import fit_tanh, filt_tanl
	from sp_utilities    import center_2D
	#  Prepare the reference in 2D alignment, i.e., low-pass filter and center.
	#  Input: list ref_data
	#   0 - mask
	#   1 - center flag
	#   2 - raw average
	#   3 - fsc result
	#  Output: filtered, centered, and masked reference image
	#  apply filtration (FRC) to reference image:
	global  ref_ali2d_counter
	ref_ali2d_counter += 1
	print_msg("steady   #%6d\n"%(ref_ali2d_counter))
	fl = 0.12 + (ref_ali2d_counter//3)*0.1
	aa = 0.1
	msg = "Tangent filter:  cut-off frequency = %10.3f        fall-off = %10.3f\n"%(fl, aa)
	print_msg(msg)
	tavg = filt_tanl(ref_data[2], fl, aa)
	cs = [0.0]*2
	return  tavg, cs


def constant( ref_data ):
	from sp_utilities    import print_msg
	from sp_filter       import fit_tanh, filt_tanl
	from sp_utilities    import center_2D
	from sp_morphology   import threshold
	#  Prepare the reference in 2D alignment, i.e., low-pass filter and center.
	#  Input: list ref_data
	#   0 - mask
	#   1 - center flag
	#   2 - raw average
	#   3 - fsc result
	#  Output: filtered, centered, and masked reference image
	#  apply filtration (FRC) to reference image:
	global  ref_ali2d_counter
	ref_ali2d_counter += 1
	#print_msg("steady   #%6d\n"%(ref_ali2d_counter))
	fl = 0.4
	aa = 0.1
	#msg = "Tangent filter:  cut-off frequency = %10.3f        fall-off = %10.3f\n"%(fl, aa)
	#print_msg(msg)
	from sp_utilities import model_circle
	nx = ref_data[2].get_xsize()
	stat = Util.infomask(ref_data[2], model_circle(nx//2-2,nx,nx), False)
	ref_data[2] -= stat[0]
	#tavg = filt_tanl(threshold(ref_data[2]), fl, aa)
	tavg = filt_tanl(ref_data[2], fl, aa)
	cs = [0.0]*2
	return  tavg, cs


def temp_dovolume( ref_data ):
	from sp_utilities      import print_msg, read_text_row
	from sp_filter         import fit_tanh, filt_tanl
	from sp_fundamentals   import fshift
	from sp_morphology     import threshold
	#  Prepare the reference in 3D alignment, this function corresponds to what do_volume does.
	#  Input: list ref_data
	#   0 - mask
	#   1 - center flag
	#   2 - raw average
	#   3 - fsc result
	#  Output: filtered, centered, and masked reference image
	#  apply filtration (FSC) to reference image:

	global  ref_ali2d_counter
	ref_ali2d_counter += 1

	fl = ref_data[2].cmp("dot",ref_data[2], {"negative":0, "mask":ref_data[0]} )
	print_msg("do_volume user function    Step = %5d        GOAL = %10.3e\n"%(ref_ali2d_counter,fl))

	stat = Util.infomask(ref_data[2], ref_data[0], False)
	vol = ref_data[2] - stat[0]
	Util.mul_scalar(vol, 1.0/stat[1])
	vol = threshold(vol)
	#Util.mul_img(vol, ref_data[0])
	try:
		aa = read_text_row("flaa.txt")[0]
		fl = aa[0]
		aa=aa[1]
	except:
		fl = 0.12
		aa = 0.1
	msg = "Tangent filter:  cut-off frequency = %10.3f        fall-off = %10.3f\n"%(fl, aa)
	print_msg(msg)

	from sp_utilities    import read_text_file
	from sp_fundamentals import rops_table, fftip, fft
	from sp_filter       import filt_table, filt_btwl
	fftip(vol)
	try:
		rt = read_text_file( "pwreference.txt" )
		ro = rops_table(vol)
		#  Here unless I am mistaken it is enough to take the beginning of the reference pw.
		for i in range(1,len(ro)):  ro[i] = (rt[i]/ro[i])**0.5
		vol = fft( filt_table( filt_tanl(vol, fl, aa), ro) )
		msg = "Power spectrum adjusted\n"
		print_msg(msg)
	except:
		vol = fft( filt_tanl(vol, fl, aa) )

	stat = Util.infomask(vol, ref_data[0], False)
	vol -= stat[0]
	Util.mul_scalar(vol, 1.0/stat[1])
	vol = threshold(vol)
	vol = filt_btwl(vol, 0.38, 0.5)
	Util.mul_img(vol, ref_data[0])

	if ref_data[1] == 1:
		cs = volf.phase_cog()
		msg = "Center x = %10.3f        Center y = %10.3f        Center z = %10.3f\n"%(cs[0], cs[1], cs[2])
		print_msg(msg)
		volf  = fshift(volf, -cs[0], -cs[1], -cs[2])
	else:  	cs = [0.0]*3

	return  vol, cs


def dovolume( ref_data ):
	from sp_utilities      import print_msg, read_text_row
	from sp_filter         import fit_tanh, filt_tanl
	from sp_fundamentals   import fshift
	from sp_morphology     import threshold
	#  Prepare the reference in 3D alignment, this function corresponds to what do_volume does.
	#  Input: list ref_data
	#   0 - mask
	#   1 - center flag
	#   2 - raw average
	#   3 - fsc result
	#  Output: filtered, centered, and masked reference image
	#  apply filtration (FSC) to reference image:

	global  ref_ali2d_counter
	ref_ali2d_counter += 1

	fl = ref_data[2].cmp("dot",ref_data[2], {"negative":0, "mask":ref_data[0]} )
	print_msg("do_volume user function    Step = %5d        GOAL = %10.3e\n"%(ref_ali2d_counter,fl))

	stat = Util.infomask(ref_data[2], ref_data[0], False)
	vol = ref_data[2] - stat[0]
	Util.mul_scalar(vol, 1.0/stat[1])
	vol = threshold(vol)
	#Util.mul_img(vol, ref_data[0])
	try:
		aa = read_text_row("flaa.txt")[0]
		fl = aa[0]
		aa=aa[1]
	except:
		fl = 0.4
		aa = 0.2
	msg = "Tangent filter:  cut-off frequency = %10.3f        fall-off = %10.3f\n"%(fl, aa)
	print_msg(msg)

	from sp_utilities    import read_text_file
	from sp_fundamentals import rops_table, fftip, fft
	from sp_filter       import filt_table, filt_btwl
	fftip(vol)
	try:
		rt = read_text_file( "pwreference.txt" )
		ro = rops_table(vol)
		#  Here unless I am mistaken it is enough to take the beginning of the reference pw.
		for i in range(1,len(ro)):  ro[i] = (rt[i]/ro[i])**0.5
		vol = fft( filt_table( filt_tanl(vol, fl, aa), ro) )
		msg = "Power spectrum adjusted\n"
		print_msg(msg)
	except:
		vol = fft( filt_tanl(vol, fl, aa) )

	stat = Util.infomask(vol, ref_data[0], False)
	vol -= stat[0]
	Util.mul_scalar(vol, 1.0/stat[1])
	vol = threshold(vol)
	vol = filt_btwl(vol, 0.38, 0.5)
	Util.mul_img(vol, ref_data[0])

	if ref_data[1] == 1:
		cs = volf.phase_cog()
		msg = "Center x = %10.3f        Center y = %10.3f        Center z = %10.3f\n"%(cs[0], cs[1], cs[2])
		print_msg(msg)
		volf  = fshift(volf, -cs[0], -cs[1], -cs[2])
	else:  	cs = [0.0]*3

	return  vol, cs

def do_volume_mrk02(ref_data):
	"""
		data - projections (scattered between cpus) or the volume.  If volume, just do the volume processing
		options - the same for all cpus
		return - volume the same for all cpus
	"""
	from EMAN2          import Util
	from mpi            import mpi_comm_rank, mpi_comm_size, MPI_COMM_WORLD
	from sp_filter         import filt_table
	from sp_reconstruction import recons3d_4nn_MPI, recons3d_4nn_ctf_MPI
	from sp_utilities      import bcast_EMData_to_all, bcast_number_to_all, model_blank
	from sp_fundamentals import rops_table, fftip, fft
	import types

	# Retrieve the function specific input arguments from ref_data
	# Retrieve the function specific input arguments from ref_data
	data     = ref_data[0]
	Tracker  = ref_data[1]
	myid     = ref_data[2]
	nproc    = ref_data[3]

	mpi_comm = MPI_COMM_WORLD
	myid  = mpi_comm_rank(mpi_comm)
	nproc = mpi_comm_size(mpi_comm)
	
	try:     local_filter = Tracker["local_filter"]
	except:  local_filter = False
	#=========================================================================
	# volume reconstruction
	if( type(data) == list ):
		if Tracker["constants"]["CTF"]:
			vol = recons3d_4nn_ctf_MPI(myid, data, Tracker["constants"]["snr"], \
					symmetry=Tracker["constants"]["sym"], npad=Tracker["constants"]["npad"], mpi_comm=mpi_comm, smearstep = Tracker["smearstep"])
		else:
			vol = recons3d_4nn_MPI    (myid, data,\
					symmetry=Tracker["constants"]["sym"], npad=Tracker["constants"]["npad"], mpi_comm=mpi_comm)
	else:
		vol = data

	if myid == 0:
		from sp_morphology import threshold
		from sp_filter     import filt_tanl, filt_btwl
		from sp_utilities  import model_circle, get_im
		import types
		nx = vol.get_xsize()
		if(Tracker["constants"]["mask3D"] == None):
			mask3D = model_circle(int(Tracker["constants"]["radius"]*float(nx)/float(Tracker["constants"]["nnxo"])+0.5), nx, nx, nx)
		elif(Tracker["constants"]["mask3D"] == "auto"):
			from sp_utilities import adaptive_mask
			mask3D = adaptive_mask(vol)
		else:
			if( type(Tracker["constants"]["mask3D"]) == bytes ):  mask3D = get_im(Tracker["constants"]["mask3D"])
			else:  mask3D = (Tracker["constants"]["mask3D"]).copy()
			nxm = mask3D.get_xsize()
			if( nx != nxm):
				from sp_fundamentals import rot_shift3D
				mask3D = Util.window(rot_shift3D(mask3D,scale=float(nx)/float(nxm)),nx,nx,nx)
				nxm = mask3D.get_xsize()
				assert(nx == nxm)

		stat = Util.infomask(vol, mask3D, False)
		vol -= stat[0]
		Util.mul_scalar(vol, 1.0/stat[1])
		vol = threshold(vol)
		Util.mul_img(vol, mask3D)
		if( Tracker["PWadjustment"] ):
			from sp_utilities    import read_text_file, write_text_file
			rt = read_text_file( Tracker["PWadjustment"] )
			fftip(vol)
			ro = rops_table(vol)
			#  Here unless I am mistaken it is enough to take the beginning of the reference pw.
			for i in range(1,len(ro)):  ro[i] = (rt[i]/ro[i])**Tracker["upscale"]
			#write_text_file(rops_table(filt_table( vol, ro),1),"foo.txt")
			if Tracker["constants"]["sausage"]:
				ny = vol.get_ysize()
				y = float(ny)
				from math import exp
				for i in range(len(ro)):  ro[i] *= \
				  (1.0+1.0*exp(-(((i/y/Tracker["constants"]["pixel_size"])-0.10)/0.025)**2)+1.0*exp(-(((i/y/Tracker["constants"]["pixel_size"])-0.215)/0.025)**2))

			if local_filter:
				# skip low-pass filtration
				vol = fft( filt_table( vol, ro) )
			else:
				if( type(Tracker["lowpass"]) == list ):
					vol = fft( filt_table( filt_table(vol, Tracker["lowpass"]), ro) )
				else:
					vol = fft( filt_table( filt_tanl(vol, Tracker["lowpass"], Tracker["falloff"]), ro) )
			del ro
		else:
			if Tracker["constants"]["sausage"]:
				ny = vol.get_ysize()
				y = float(ny)
				ro = [0.0]*(ny//2+2)
				from math import exp
				for i in range(len(ro)):  ro[i] = \
				  (1.0+1.0*exp(-(((i/y/Tracker["constants"]["pixel_size"])-0.10)/0.025)**2)+1.0*exp(-(((i/y/Tracker["constants"]["pixel_size"])-0.215)/0.025)**2))
				fftip(vol)
				filt_table(vol, ro)
				del ro
			if not local_filter:
				if( type(Tracker["lowpass"]) == list ):
					vol = filt_table(vol, Tracker["lowpass"])
				else:
					vol = filt_tanl(vol, Tracker["lowpass"], Tracker["falloff"])
			if Tracker["constants"]["sausage"]: vol = fft(vol)

	if local_filter:
		from sp_morphology import binarize
		if(myid == 0): nx = mask3D.get_xsize()
		else:  nx = 0
		nx = bcast_number_to_all(nx, source_node = 0)
		#  only main processor needs the two input volumes
		if(myid == 0):
			mask = binarize(mask3D, 0.5)
			locres = get_im(Tracker["local_filter"])
			lx = locres.get_xsize()
			if(lx != nx):
				if(lx < nx):
					from sp_fundamentals import fdecimate, rot_shift3D
					mask = Util.window(rot_shift3D(mask,scale=float(lx)/float(nx)),lx,lx,lx)
					vol = fdecimate(vol, lx,lx,lx)
				else:  ERROR("local filter cannot be larger than input volume","user function",1)
			stat = Util.infomask(vol, mask, False)
			vol -= stat[0]
			Util.mul_scalar(vol, 1.0/stat[1])
		else:
			lx = 0
			locres = model_blank(1,1,1)
			vol = model_blank(1,1,1)
		lx = bcast_number_to_all(lx, source_node = 0)
		if( myid != 0 ):  mask = model_blank(lx,lx,lx)
		bcast_EMData_to_all(mask, myid, 0, comm=mpi_comm)
		from sp_filter import filterlocal
		vol = filterlocal( locres, vol, mask, Tracker["falloff"], myid, 0, nproc)

		if myid == 0:
			if(lx < nx):
				from sp_fundamentals import fpol
				vol = fpol(vol, nx,nx,nx)
			vol = threshold(vol)
			vol = filt_btwl(vol, 0.38, 0.5)#  This will have to be corrected.
			Util.mul_img(vol, mask3D)
			del mask3D
			# vol.write_image('toto%03d.hdf'%iter)
		else:
			vol = model_blank(nx,nx,nx)
	else:
		if myid == 0:
			#from utilities import write_text_file
			#write_text_file(rops_table(vol,1),"goo.txt")
			stat = Util.infomask(vol, mask3D, False)
			vol -= stat[0]
			Util.mul_scalar(vol, 1.0/stat[1])
			vol = threshold(vol)
			vol = filt_btwl(vol, 0.38, 0.5)#  This will have to be corrected.
			Util.mul_img(vol, mask3D)
			del mask3D
			# vol.write_image('toto%03d.hdf'%iter)
	# broadcast volume
	bcast_EMData_to_all(vol, myid, 0, comm=mpi_comm)
	#=========================================================================
	return vol


def do_volume_mrk03(ref_data):
	"""
		data - projections (scattered between cpus) or the volume.  If volume, just do the volume processing
		options - the same for all cpus
		return - volume the same for all cpus
	"""
	from EMAN2          import Util
	from mpi            import mpi_comm_rank, mpi_comm_size, MPI_COMM_WORLD
	from sp_filter         import filt_table
	from sp_reconstruction import recons3d_4nn_MPI, recons3d_4nnw_MPI  #  recons3d_4nn_ctf_MPI
	from sp_utilities      import bcast_EMData_to_all, bcast_number_to_all, model_blank
	from sp_fundamentals   import rops_table, fftip, fft
	import types

	# Retrieve the function specific input arguments from ref_data
	data     = ref_data[0]
	Tracker  = ref_data[1]
	myid     = ref_data[2]
	nproc    = ref_data[3]

	mpi_comm = MPI_COMM_WORLD
	
	try:     local_filter = Tracker["local_filter"]
	except:  local_filter = False
	#=========================================================================
	# volume reconstruction
	if( type(data) == list ):
		if Tracker["constants"]["CTF"]:
			#vol = recons3d_4nn_ctf_MPI(myid, data, Tracker["constants"]["snr"], \
			#		symmetry=Tracker["constants"]["sym"], npad=Tracker["constants"]["npad"], mpi_comm=mpi_comm, smearstep = Tracker["smearstep"])
			vol = recons3d_4nnw_MPI(myid, data, Tracker["bckgnoise"], Tracker["constants"]["snr"], \
				symmetry=Tracker["constants"]["sym"], npad=Tracker["constants"]["npad"], mpi_comm=mpi_comm, smearstep = Tracker["smearstep"])
		else:
			vol = recons3d_4nn_MPI    (myid, data,\
					symmetry=Tracker["constants"]["sym"], npad=Tracker["constants"]["npad"], mpi_comm=mpi_comm)
	else:
		vol = data

	if myid == 0:
		from sp_morphology import threshold
		from sp_filter     import filt_tanl, filt_btwl
		from sp_utilities  import model_circle, get_im
		import types
		nx = vol.get_xsize()
		if(Tracker["constants"]["mask3D"] == None):
			mask3D = model_circle(int(Tracker["constants"]["radius"]*float(nx)/float(Tracker["constants"]["nnxo"])+0.5), nx, nx, nx)
		elif(Tracker["constants"]["mask3D"] == "auto"):
			from sp_utilities import adaptive_mask
			mask3D = adaptive_mask(vol)
		else:
			if( type(Tracker["constants"]["mask3D"]) == bytes ):  mask3D = get_im(Tracker["constants"]["mask3D"])
			else:  mask3D = (Tracker["constants"]["mask3D"]).copy()
			nxm = mask3D.get_xsize()
			if( nx != nxm ):
				from sp_fundamentals import rot_shift3D
				mask3D = Util.window(rot_shift3D(mask3D,scale=float(nx)/float(nxm)),nx,nx,nx)
				nxm = mask3D.get_xsize()
				assert(nx == nxm)

		if not local_filter:
			if( type(Tracker["lowpass"]) == list ):
				vol = filt_table(vol, Tracker["lowpass"])
			else:
				vol = filt_tanl(vol, Tracker["lowpass"], Tracker["falloff"])

	if local_filter:
		from sp_morphology import binarize
		if(myid == 0): nx = mask3D.get_xsize()
		else:  nx = 0
		if( nproc > 1 ): nx = bcast_number_to_all(nx, source_node = 0)
		#  only main processor needs the two input volumes
		if(myid == 0):
			mask = binarize(mask3D, 0.5)
			locres = get_im(Tracker["local_filter"])
			lx = locres.get_xsize()
			if(lx != nx):
				if(lx < nx):
					from sp_fundamentals import fdecimate, rot_shift3D
					mask = Util.window(rot_shift3D(mask,scale=float(lx)/float(nx)),lx,lx,lx)
					vol = fdecimate(vol, lx,lx,lx)
				else:  ERROR("local filter cannot be larger than input volume","user function",1)
			stat = Util.infomask(vol, mask, False)
			vol -= stat[0]
			Util.mul_scalar(vol, 1.0/stat[1])
		else:
			lx = 0
			locres = model_blank(1,1,1)
			vol = model_blank(1,1,1)
		if( nproc > 1 ):
			lx = bcast_number_to_all(lx, source_node = 0)
			if( myid != 0 ):  mask = model_blank(lx,lx,lx)
			bcast_EMData_to_all(mask, myid, 0, comm=mpi_comm)
		from sp_filter import filterlocal
		vol = filterlocal( locres, vol, mask, Tracker["falloff"], myid, 0, nproc)

		if myid == 0:
			if(lx < nx):
				from sp_fundamentals import fpol
				vol = fpol(vol, nx,nx,nx)
			vol = threshold(vol)
			Util.mul_img(vol, mask3D)
			del mask3D
			# vol.write_image('toto%03d.hdf'%iter)
		else:
			vol = model_blank(nx,nx,nx)
	else:
		if myid == 0:
			#from utilities import write_text_file
			#write_text_file(rops_table(vol,1),"goo.txt")
			stat = Util.infomask(vol, mask3D, False)
			vol -= stat[0]
			Util.mul_scalar(vol, 1.0/stat[1])
			#vol = threshold(vol)
			# vol.write_image('toto%03d.hdf'%iter)
	# broadcast volume
	if( nproc > 1 ):
		bcast_EMData_to_all(vol, myid, 0, comm=mpi_comm)
		#  Deal with mask 3D and MPI
		#=========================================================================
		return  vol, None
	else:
		mvol = Util.muln_img(vol, mask3D)
		return mvol, vol


def do_volume_mrk04(ref_data):
	"""
		data - projections (scattered between cpus) or the volume.  If volume, just do the volume processing
		options - the same for all cpus
		return - volume the same for all cpus
	"""
	from EMAN2          import Util
	from mpi            import mpi_comm_rank, mpi_comm_size, MPI_COMM_WORLD
	from sp_filter         import filt_table
	from sp_reconstruction import recons3d_4nn_MPI, recons3d_4nn_ctf_MPI
	from sp_utilities      import bcast_EMData_to_all, bcast_number_to_all, model_blank
	from sp_fundamentals   import rops_table, fftip, fft
	import types

	# Retrieve the function specific input arguments from ref_data
	data     = ref_data[0]
	Tracker  = ref_data[1]
	myid     = ref_data[2]
	nproc    = ref_data[3]

	mpi_comm = MPI_COMM_WORLD
	
	try:     local_filter = Tracker["local_filter"]
	except:  local_filter = False
	#=========================================================================
	# volume reconstruction
	if( type(data) == list ):
		if Tracker["constants"]["CTF"]:
			ERROR("should not be here","mrk04",1)
			vol = recons3d_4nn_ctf_MPI(myid, data, Tracker["constants"]["snr"], \
					symmetry=Tracker["constants"]["sym"], npad=Tracker["constants"]["npad"], mpi_comm=mpi_comm, smearstep = Tracker["smearstep"])
		else:
			vol = recons3d_4nn_MPI    (myid, data,\
					symmetry=Tracker["constants"]["sym"], npad=Tracker["constants"]["npad"], mpi_comm=mpi_comm)
	else:
		vol = data

	if myid == 0:
		from sp_morphology import threshold
		from sp_filter     import filt_tanl, filt_btwl
		from sp_utilities  import model_circle, get_im
		import types
		nx = vol.get_xsize()
		if(Tracker["constants"]["mask3D"] == None):
			mask3D = model_circle(int(Tracker["constants"]["radius"]*float(nx)/float(Tracker["constants"]["nnxo"])+0.5), nx, nx, nx)
		elif(Tracker["constants"]["mask3D"] == "auto"):
			from sp_utilities import adaptive_mask
			mask3D = adaptive_mask(vol)
		else:
			if( type(Tracker["constants"]["mask3D"]) == bytes ):  mask3D = get_im(Tracker["constants"]["mask3D"])
			else:  mask3D = (Tracker["constants"]["mask3D"]).copy()
			nxm = mask3D.get_xsize()
			if( nx != nxm):
				from sp_fundamentals import rot_shift3D
				mask3D = Util.window(rot_shift3D(mask3D,scale=float(nx)/float(nxm)),nx,nx,nx)
				nxm = mask3D.get_xsize()
				assert(nx == nxm)

		stat = Util.infomask(vol, mask3D, False)
		vol -= stat[0]
		Util.mul_scalar(vol, 1.0/stat[1])
		vol = threshold(vol)
		Util.mul_img(vol, mask3D)

	if local_filter:
		from sp_morphology import binarize
		if(myid == 0): nx = mask3D.get_xsize()
		else:  nx = 0
		if( nproc > 1 ):  nx = bcast_number_to_all(nx, source_node = 0)
		#  only main processor needs the two input volumes
		if(myid == 0):
			mask = binarize(mask3D, 0.5)
			locres = get_im(Tracker["local_filter"])
			lx = locres.get_xsize()
			if(lx != nx):
				if(lx < nx):
					from sp_fundamentals import fdecimate, rot_shift3D
					mask = Util.window(rot_shift3D(mask,scale=float(lx)/float(nx)),lx,lx,lx)
					vol = fdecimate(vol, lx,lx,lx)
				else:  ERROR("local filter cannot be larger than input volume","user function",1)
			stat = Util.infomask(vol, mask, False)
			vol -= stat[0]
			Util.mul_scalar(vol, 1.0/stat[1])
		else:
			lx = 0
			locres = model_blank(1,1,1)
			vol = model_blank(1,1,1)
		if( nproc > 1 ):
			lx = bcast_number_to_all(lx, source_node = 0)
			if( myid != 0 ):  mask = model_blank(lx,lx,lx)
			bcast_EMData_to_all(mask, myid, 0, comm=mpi_comm)
		from sp_filter import filterlocal
		vol = filterlocal( locres, vol, mask, Tracker["falloff"], myid, 0, nproc)

		if myid == 0:
			if(lx < nx):
				from sp_fundamentals import fpol
				vol = fpol(vol, nx,nx,nx)
			vol = threshold(vol)
			vol = filt_btwl(vol, 0.38, 0.5)#  This will have to be corrected.
			Util.mul_img(vol, mask3D)
			del mask3D
			# vol.write_image('toto%03d.hdf'%iter)
		else:
			vol = model_blank(nx,nx,nx)
	else:
		pass
		"""
		if myid == 0:
			#from utilities import write_text_file
			#write_text_file(rops_table(vol,1),"goo.txt")
			stat = Util.infomask(vol, mask3D, False)
			vol -= stat[0]
			Util.mul_scalar(vol, 1.0/stat[1])
			vol = threshold(vol)
			vol = filt_btwl(vol, 0.38, 0.5)#  This will have to be corrected.
			Util.mul_img(vol, mask3D)
			del mask3D
			# vol.write_image('toto%03d.hdf'%iter)
		"""
	# broadcast volume
	if( nproc > 1 ):  bcast_EMData_to_all(vol, myid, 0, comm=mpi_comm)
	#=========================================================================
	return vol

def do_volume_mrk05(ref_data):
	"""
		vol - volume
		return - volume the same for all cpus
	"""
	from EMAN2          import Util
	from mpi            import mpi_comm_rank, mpi_comm_size, MPI_COMM_WORLD
	from sp_filter         import filt_table
	from sp_reconstruction import recons3d_4nn_MPI, recons3d_4nn_ctf_MPI
	from sp_utilities      import bcast_EMData_to_all, bcast_number_to_all, model_blank
	from sp_fundamentals   import rops_table, fftip, fft
	import types

	# Retrieve the function specific input arguments from ref_data
	vol     = ref_data[0]
	Tracker = ref_data[1]
	
	from sp_morphology import threshold
	from sp_filter     import filt_tanl, filt_btwl
	from sp_utilities  import model_circle, get_im
	import types
	nx = vol.get_xsize()
	if(Tracker["constants"]["mask3D"] == None):
		mask3D = model_circle(int(Tracker["constants"]["radius"]*float(nx)/float(Tracker["constants"]["nnxo"])+0.5), nx, nx, nx)
	elif(Tracker["constants"]["mask3D"] == "auto"):
		from sp_utilities import adaptive_mask
		mask3D = adaptive_mask(vol)
	else:
		if( type(Tracker["constants"]["mask3D"]) == bytes ):  mask3D = get_im(Tracker["constants"]["mask3D"])
		else:  mask3D = (Tracker["constants"]["mask3D"]).copy()
		nxm = mask3D.get_xsize()
		if( nx != nxm):
			from sp_fundamentals import rot_shift3D
			mask3D = Util.window(rot_shift3D(mask3D,scale=float(nx)/float(nxm)),nx,nx,nx)
			nxm = mask3D.get_xsize()
			assert(nx == nxm)

	stat = Util.infomask(vol, mask3D, False)
	vol -= stat[0]
	Util.mul_scalar(vol, 1.0/stat[1])
	
	#=========================================================================
	return Util.muln_img(vol, mask3D)#, vol



# rewrote factory dict to provide a flexible interface for providing user functions dynamically.
#    factory is a class that checks how it's called. static labels are rerouted to the original
#    functions, new are are routed to build_user_function (provided below), to load from file
#    and pathname settings....
# Note: this is a workaround to provide backwards compatibility and to avoid rewriting all functions
#    using user_functions. this can be removed when it is no longer necessary....

class factory_class:

	def __init__(self):
		self.contents = {}
		self.contents["ref_ali2d"]          = ref_ali2d
		self.contents["ref_ali2d_c"]        = ref_ali2d_c
		self.contents["julien"]             = julien	
		self.contents["ref_ali2d_m"]        = ref_ali2d_m
		self.contents["ref_random"]         = ref_random
		self.contents["ref_ali3d"]          = ref_ali3d
		self.contents["ref_ali3dm"]         = ref_ali3dm
		self.contents["ref_sort3d"]         = ref_sort3d
		self.contents["ref_ali3dm_new"]     = ref_ali3dm_new
		self.contents["ref_ali3dm_ali_50S"] = ref_ali3dm_ali_50S
		self.contents["helical"]            = helical
		self.contents["helical2"]           = helical2
		self.contents["spruce_up_var_m"]    = spruce_up_var_m
		self.contents["reference3"]         = reference3
		self.contents["reference4"]         = reference4
		self.contents["spruce_up"]          = spruce_up
		self.contents["spruce_up_variance"] = spruce_up_variance
		self.contents["ref_aliB_cone"]      = ref_aliB_cone
		self.contents["ref_7grp"]           = ref_7grp
		self.contents["steady"]             = steady
		self.contents["dovolume"]           = dovolume	 
		self.contents["temp_dovolume"]      = temp_dovolume
		self.contents["do_volume_mrk02"]    = do_volume_mrk02	 
		self.contents["do_volume_mrk03"]    = do_volume_mrk03
		self.contents["do_volume_mrk04"]    = do_volume_mrk04
		self.contents["do_volume_mrk05"]    = do_volume_mrk05
		self.contents["constant"]           = constant	 

		# User function used in meridien
		self.contents["do_volume_mask"]     = sp_user_functions_meridien.do_volume_mask
		self.contents["ai_spa"]     = sp_user_functions_meridien.ai_spa
		self.contents["ai_filament"]     = sp_user_functions_meridien.ai_filament

	def __getitem__(self,index):

		if (type(index) is str):
			# we need to consider 2 possible strings: either function name to be
			#    handled by real factory, or a string-converted list passed by
			#    --user="[...]" type parameter.
			# string-type list?
			if (index.startswith("[") and index.endswith("]")):
				try:
					# strip [] and seperate with commas
					my_path,my_module,my_func=index[1:-1].split(",")

					# and build the user function with it
					return build_user_function(module_name=my_module,function_name=my_func,
								   path_name=my_path)
				except:
					return None
			# doesn' seem to be a string-converted list, so try using it as
			#    function name
			else:
				try:
					return self.contents[index]
				except KeyError:
					return None
				except:
					return None

		if (type(index) is list):
			try:
				# try building with module, function and path
				return build_user_function(module_name=index[1],function_name=index[2],
							   path_name=index[0])
			except IndexError:
				# we probably have a list [module,function] only, no path
				return build_user_function(module_name=index[0],function_name=index[1])
			except:
				# the parameter is something we can't understand... return None or
				#    raise an exception....
				return None

		#print type(index)
		return None
	

						   
# build_user_function: instead of a static user function factory that has to be updated for
#    every change, we use the imp import mechanism: a module can be supplied at runtime (as
#    an argument of the function), which will be imported. from that modules we try to import
#    the function (function name is supplied as a second argument). this function object is
#    returned to the caller.
# Note that the returned function (at this time) does not support dynamic argument lists,
#    so the interface of the function (i.e. number of arguments and the way that they are used)
#    has to be known and is static!

def build_user_function(module_name=None,function_name=None,path_name=None):

	if (module_name is None) or (function_name is None):
		return None

	# set default path list here. this can be extended to include user directories, for
	#    instance $HOME,$HOME/sparx. list is necessary, since find_module expects a list
	#    of paths to try as second argument
	import os
	if (path_name is None):
		path_list = [os.path.expanduser("~"),os.path.expanduser("~")+os.sep+"sparx",]

	if (type(path_name) is list):
		path_list = path_name

	if (type(path_name) is str):
		path_list = [path_name,]

	import imp

	try:
		(file,path,descript) = imp.find_module(module_name,path_list)
	except ImportError:
		sxprint("could not find module "+str(module_name)+" in path "+str(path_name))
		return None

	try:
		dynamic_mod = imp.load_module(module_name,file,path,descript)
	except ImportError:
		sxprint("could not load module "+str(module_name)+" in path "+str(path))
		return None
		
	# function name has to be taken from dict, since otherwise we would be trying an
	#    equivalent of "import dynamic_mod.function_name"
	try:
		dynamic_func = dynamic_mod.__dict__[function_name]
	except KeyError:
		# key error means function is not defined in the module....
		sxprint("could not import user function "+str(function_name)+" from module")
		sxprint(str(path))
		return None
	except:
		sxprint("unknown error getting function!")
		return None
	else:
		return dynamic_func



from sp_global_def import *
from EMAN2_cppwrap import *

import sp_user_functions_meridien

ref_ali2d_counter = -1
factory=factory_class()
