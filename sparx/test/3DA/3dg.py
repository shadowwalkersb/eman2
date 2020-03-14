#!/usr/bin/env python
from EMAN2  import *
from sparx  import *

from sys   import exit
from time  import time
vol = EMData()
vol.read_image("../model001.tcp")
#nx = 128
#vol = model_circle(61,nx,nx,nx)
#vol.read_image("model.spi")
#info(e)
nx = vol.get_xsize()
r = nx//2-2
delta = 2.0
angles = even_angles(delta,0.,90.,0,359.99,"S")
write_text_col(angles, "angls.txt")
#angles = [None]*len(la)
#for i in xrange(len(la)):
#	angles[i] = fangles[la[i]]
#del fangles
'''
i1 = len(angles)
at = even_angles(delta,0.,180.,0,359.99,"S")
i2 = len(at)

for i in xrange(i2-i1):
	angles.append(at[i+i1-1])
'''
#delta=0.4
#angles=even_angles(delta,41.,42.9,101.0,129.99,"S", phiEqpsi="Minus")
#for i in xrange(len(angles)):
#	angles.append( [180.+angles[i][0], 180.-angles[i][1], 180.-angles[i][2] ])
# 
#for i in xrange(len(angles)):	print angles[i]
#exit()
volft,kb=prep_vol(vol)

stack_data="bdb:data"
import os
#os.system("rm -f  "+stack_data)
#print  angles
nangles = len(angles)
#dropSpiderDoc("angles",angles)
ppp = []
s2x=0
s2y=0
defocus = -1
from random import random,randint
start =  time()
for i in range(nangles):
	#s2x = 4.0*randint(-1,1)
	#s2y = 4.0*randint(-1,1)
	#ppp.append([angles[i][0], angles[i][1], angles[i][2], s2x, s2y])
	if i%100 == 0:   print(i)
	#proj = prgs(volft, kb, [angles[i][0], angles[i][1], angles[i][2], -s2x, -s2y])
	proj = project(vol, [angles[i][0], angles[i][1], angles[i][2], -s2x, -s2y], r)
	#apply CTF
	#defocus = randint(3,3)*100.0
	#proj = projo.copy()
	#proj = filt_ctf(proj, generate_ctf([defocus, 2.0, 300.0, 2.5, 0.0, 0.1]))
	#if(i == 0): st = Util.infomask(proj,None,True)
	#proj += model_gauss_noise(st[1]*3.,nx,nx)
	# Set all parameters for the new 2D image
	# three angles and two shifts to zero
	set_params_proj(proj, [angles[i][0], angles[i][1], angles[i][2], s2x, s2y])
	# CTF parameters, if defocus zero, they are undetermined
	#set_ctf(proj, [defocus, 2.0, 300.0, 2.5, 0.0, 0.1])
	# flags describing the status of the image (1 = true, 0 = false)
	#proj.set_attr('group', i%3)
	# horatio active_refactoring Jy51i1EwmLD4tWZ9_00000_1
	# proj.set_attr_dict({'active':1, 'ctf_applied':0})
	proj.set_attr_dict({'ctf_applied':0})
	proj.write_image(stack_data, i)
exit()
print(time()-start)
del vol
del volft
start=time()
nprojdata = EMUtil.get_image_count(stack_data)
vol1   = recons3d_4nn(stack_data, list(range(nprojdata)))
print(time()-start)
vol1.write_image("b4.hdf", 0)
exit()
del volft
write_text_file(ppp, "params.txt")
exit()
del ppp
nprojdata = EMUtil.get_image_count(stack_data)
snr = 1.0e20
#vol1   = recons3d_4nn_ctf(stack_data, range(0,nprojdata,2), snr)
vol1   = recons3d_4nn(stack_data, list(range(0,nprojdata,2)))
vol1.write_image("v1.hdf", 0)

#vol2   = recons3d_4nn_ctf(stack_data, range(1,nprojdata,2), snr)
vol2   = recons3d_4nn(stack_data, list(range(1,nprojdata,2)))

#mask3d = model_circle(nx//2-5,nx,nx,nx)

#Util.mul_img(vol1, mask3d)
#Util.mul_img(vol2, mask3d)
#del mask3d

vol2.write_image("v2.hdf", 0)
exit()
# THIS HAS TO BE INDEXED BY THE LOOP
fsc(vol1,vol2,1.0,"tdt.txt")
#exit()
#vol = recons3d_wbp(stack_data, range(nprojdata),"general", const=1.0e4)
#dropImage(vol,"newvolwp.spi","s")
#vol = recons3d_4nn(stack_data, range(nprojdata))
#dropImage(vol,"newvolnp.spi","s")
#snr = 1.0
#vol = recons3d_4nn_ctf(stack_data, range(nprojdata), snr)
#dropImage(vol,"newvolp.spi","s")
#exit()
mask3D = []
# do the projection matching
first_ring = 1
last_ring = 35
rstep = 1
xrng  = 1
yrng  = 1
step  = 1
dtheta= 15
# begin a refinement loop, slowly decrease dtheta inside the loop
snr = 1.0
for iter in range(1):
	print(" ITERATION #",iter)
	#proj_ali(vol, mask3D, stack_data, first_ring, last_ring, rstep, xrng, yrng, step, dtheta)

	#calculate new and improved 3D
	#stack_data = "data.hdf"
	nprojdata = EMUtil.get_image_count(stack_data)
	list_p = list(range(nprojdata))
	vol = recons3d_4nn_ctf(stack_data, list_p, snr, 1, "c2")
	vol.write_image("newvol.hdf",0)
	del  vol
	#exit()
	#and now the resolution

	list_p = list(range(0,nprojdata,2))
	vol1   = recons3d_4nn_ctf(stack_data, list_p, snr)

	list_p = list(range(1,nprojdata,2))
	vol2   = recons3d_4nn_ctf(stack_data, list_p, snr)

	mask3d = model_circle(nx//2-5,nx,nx,nx)

	Util.mul_img(vol1, mask3d)
	Util.mul_img(vol2, mask3d)
	del mask3d
	#dropImage(vol1,"v1.spi")

	#dropImage(vol2,"v2.spi")
	# THIS HAS TO BE INDEXED BY THE LOOP
	fsc(vol1,vol2,0.5,"tdt")

	# here figure the filtration parameters and filter vol for the next iteration

	#  here the loop should end
