


































































'''0
Temporarily disabled as list cannot be passed to projector.
def prl(vol, params, radius, stack = None):
	"""
		Name
			prl - calculate a set of 2-D projection of a 3-D volume
		Input
			vol: input volume, all dimensions have to be the same (nx=ny=nz)
			params: a list of input parameters given as a list [i][phi, theta, psi, s2x, s2y], projection in calculated using the three Eulerian angles and then shifted by s2x,s2y
			radius: integer radius of a sphere - projection is calculated using voxels within this sphere.
		Output
			proj
				either: an in-core stack of generated 2-D projection
			stack
	"""
	from sp_fundamentals import rot_shift2D
	for i in xrange(len(params)):
        	myparams = {"angletype":"SPIDER", "anglelist":params[i][0:3], "radius":radius}
        	proj = vol.project("pawel", myparams)
		if(params[i][3]!=0. or params[i][4]!=0.): proj = rot_shift2D(proj, sx = params[i][3], sy = params[i][4], interpolation_method = "linear")
		proj.set_attr_dict({'phi':params[i][0], 'theta':params[i][1], 'psi':params[i][2], 's2x':-params[i][3], 's2y':-params[i][4]})
		proj.set_attr_dict({ 'ctf_applied':0})
		
		if(stack):
			proj.write_image(stack, i)
		else:
			if(i == 0): out= []
			out.append(proj)
	if(stack): return
	else:      return out
'''





















































































































































































































































































































"""1
	c  = 2
	kc = 10
	# draw reperes
	for i in xrange(nx):
		im.set_value_at(i, int(nx / 2.0), 0.006)
		im.set_value_at(int(nx / 2.0), i, 0.006)

	# draw the circles
	lth = range(0, 90, kc)
	lth.append(90)

	for th in lth:

		if th == 90: color = 0.03
		else:        color = 0.006

		rc  = sin((float(th) / 180.0) * pi)
		rc *= (nx - 1)
		
		for n in xrange(3600):
			a  = (n / 1800.0) * pi
			px = nx / 2.0 + (rc - 1) / 2.0 * cos(a)
			py = nx / 2.0 + (rc - 1) / 2.0 * sin(a)
			im.set_value_at(int(px), int(py), color)
	"""




































































































































































































































































































































































































































































































































































"""2
		if(ite>1 and ite%5 == 0  and ite<140):
			if(myid == main_node):
				for i in xrange(0,len(tlistprj),5):
					ind          = 4*i
					Ori[ind]      =  360.*random()
					Ori[ind+1]    =  180.*random()
					Ori[ind+2]    =  360.*random()
					Ori[ind+3]    =  -1
				for i in xrange(len(tlistprj)):
					ind          = 4*i
					Ori[ind+3]    = float(Ori[ind+3])
			nnn = len(Ori)
			Ori = mpi_bcast(Ori, nnn, MPI_FLOAT, main_node, MPI_COMM_WORLD)
			Ori = map(float, Ori)
			for i in xrange(len(tlistprj)):
				ind          = 4*i
				Ori[ind+3]    = int(Ori[ind+3])
		"""






































































































































































































