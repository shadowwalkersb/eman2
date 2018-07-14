#!/usr/bin/env python
from __future__ import print_function
from __future__ import division

from past.utils import old_div
from builtins import range
from EMAN2 import *
from sparx import *
from math import cos, sin, pi
from reconstruction import rec2D

M_PI = pi

m = model_blank( 12, 12 )
m.set_value_at( 2, 2, 1.0 )
m.set_value_at( 6, 4, 2.0 )
m.set_value_at( 10, 6, 3.0 )
printImage( m )

prjft, kb = prep_vol( m )
size = m.get_xsize()

nangle = 40
dangle = old_div(180.0,nangle)

lines = []
for j in range(nangle):
	line = prgs1d( prjft, kb, [dangle*j, 0.0] )
	line.set_attr( "alpha", dangle*j )
	line.set_attr( "s1x", 0.0 )
	lines.append(line)

p = rec2D( lines )
printImage( p )

