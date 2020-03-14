#!/usr/bin/env python
#
# Author: Markus Stabrin 2019 (markus.stabrin@mpi-dortmund.mpg.de)
# Author: Fabian Schoenfeld 2019 (fabian.schoenfeld@mpi-dortmund.mpg.de)
# Author: Thorsten Wagner 2019 (thorsten.wagner@mpi-dortmund.mpg.de)
# Author: Tapu Shaikh 2019 (tapu.shaikh@mpi-dortmund.mpg.de)
# Author: Adnan Ali 2019 (adnan.ali@mpi-dortmund.mpg.de)
# Author: Luca Lusnig 2019 (luca.lusnig@mpi-dortmund.mpg.de)
# Author: Toshio Moriya 2019 (toshio.moriya@kek.jp)
# Author: Pawel A.Penczek 05/27/2009 (Pawel.A.Penczek@uth.tmc.edu)
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
#
import os
import sys

import sp_global_def
from sp_global_def import sxprint, ERROR

from optparse import OptionParser

from   sp_global_def import *
from   EMAN2 import *
from   sp_sparx import *
from sp_global_def import SPARX_MPI_TAG_UNIVERSAL

import mpi

mpi.mpi_init( 0, [] )

def main():
	arglist = []
	for arg in sys.argv:
		arglist.append( arg )
	progname = os.path.basename(arglist[0])
	usage = progname + """ inputvolume  locresvolume maskfile outputfile   --radius --falloff  --MPI

	    Locally filer a volume based on local resolution volume (sxlocres.py) within area outlined by the maskfile
	"""
	parser = OptionParser(usage,version=SPARXVERSION)

	parser.add_option("--radius",	type="int",		        default=-1, 	help="if there is no maskfile, sphere with r=radius will be used, by default the radius is nx/2-1")
	parser.add_option("--falloff",	type="float",		    default=0.1,    help="falloff of tanl filter (default 0.1)")
	parser.add_option("--MPI",      action="store_true",   	default=False,  help="use MPI version")

	(options, args) = parser.parse_args(arglist[1:])
	
	if len(args) <3 or len(args) > 4:
		sxprint("See usage " + usage)
		ERROR( "Wrong number of parameters. Please see usage information above." )
		return

	if sp_global_def.CACHE_DISABLE:
		from sp_utilities import disable_bdb_cache
		disable_bdb_cache()

	if options.MPI:
		number_of_proc = mpi.mpi_comm_size(MPI_COMM_WORLD)
		myid = mpi.mpi_comm_rank(MPI_COMM_WORLD)
		main_node = 0

		if(myid == main_node):
			#print sys.argv
			vi = get_im(sys.argv[1])
			ui = get_im(sys.argv[2])
			#print   Util.infomask(ui, None, True)
			radius = options.radius
			nx = vi.get_xsize()
			ny = vi.get_ysize()
			nz = vi.get_zsize()
			dis = [nx,ny,nz]
		else:
			falloff = 0.0
			radius  = 0
			dis = [0,0,0]
			vi = None
			ui = None
		dis = bcast_list_to_all(dis, myid, source_node = main_node)

		if(myid != main_node):
			nx = int(dis[0])
			ny = int(dis[1])
			nz = int(dis[2])
		radius  = bcast_number_to_all(radius, main_node)
		if len(args) == 3:
			if( radius == -1 ):  
				radius = min(nx,ny,nz)//2 -1
			m = model_circle( radius ,nx,ny,nz)
			outvol = args[2]

		elif len(args) == 4:
			if(myid == main_node): 
				m = binarize(get_im(args[2]), 0.5)
			else:  
				m = model_blank(nx,ny,nz)
			outvol = args[3]
			bcast_EMData_to_all(m, myid, main_node)

		from sp_filter import filterlocal
		filteredvol = filterlocal(ui, vi, m, options.falloff, myid, main_node, number_of_proc)

		if(myid == 0):  
			filteredvol.write_image(outvol)

	else:
		vi = get_im(args[0])
		ui = get_im(args[1])  # resolution volume, values are assumed to be from 0 to 0.5

		nn = vi.get_xsize()

		falloff = options.falloff

		if len(args) == 3:
			radius = options.radius
			if( radius == -1 ):  
				radius = nn//2 -1
			m = model_circle( radius ,nn,nn,nn)
			outvol = args[2]

		elif len(args) == 4:
			m = binarize(get_im(args[2]), 0.5)
			outvol = args[3]

		fftip(vi)  # this is the volume to be filtered

		#  Round all resolution numbers to two digits
		for x in range(nn):
			for y in range(nn):
				for z in range(nn):
					ui.set_value_at_fast( x,y,z, round(ui.get_value_at(x,y,z), 2) )
		st = Util.infomask(ui, m, True)
		

		filteredvol = model_blank(nn,nn,nn)
		cutoff = max(st[2] - 0.01,0.0)
		while(cutoff < st[3] ):
			cutoff = round(cutoff + 0.01, 2)
			pt = Util.infomask( threshold_outside(ui, cutoff - 0.00501, cutoff + 0.005), m, True)
			if(pt[0] != 0.0):
				vovo = fft(filt_tanl(vi, cutoff, falloff) )
				for x in range(nn):
					for y in range(nn):
						for z in range(nn):
							if(m.get_value_at(x,y,z) > 0.5):
								if(round(ui.get_value_at(x,y,z),2) == cutoff):
									filteredvol.set_value_at_fast(x,y,z,vovo.get_value_at(x,y,z))

		sp_global_def.write_command(os.path.dirname(outvol))
		filteredvol.write_image(outvol)

if __name__ == "__main__":
	sp_global_def.print_timestamp( "Start" )
	main()
	sp_global_def.print_timestamp( "Finish" )
	mpi.mpi_finalize()
