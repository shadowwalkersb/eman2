/*
 * Author: Tao Ju, 5/16/2007 <taoju@cs.wustl.edu>, code ported by Grant Tang
 * code extensively modified and optimized by David Woolford
 * Copyright (c) 2000-2006 Baylor College of Medicine
 *
 * This software is issued under a joint BSD/GNU license. You may use the
 * source code in this file under either license. However, note that the
 * complete EMAN2 and SPARX software packages have some GPL dependencies,
 * so you are responsible for compliance with the licenses of these packages
 * if you opt to use BSD licensing. The warranty disclaimer below holds
 * in either instance.
 *
 * This complete copyright notice must be included in any revised version of the
 * source code. Additional authorship citations may be added, but existing
 * author citations must be preserved.
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
 *
 * */
#ifdef USE_OPENGL

#ifdef _WIN32
	#include <windows.h>
#endif	//_WIN32

#ifndef GL_GLEXT_PROTOTYPES
	#define GL_GLEXT_PROTOTYPES
#endif	//GL_GLEXT_PROTOTYPES


#include "marchingcubes.h"

#include <ctime>
#include <cmath>

using namespace EMAN;
#include "transform.h"
#include "emobject.h"
#include "vec3.h"

//a2fVertexOffset lists the positions, relative to vertex0, of each of the 8 vertices of a cube
static const int a2fVertexOffset[8][3] =
{
		{0, 0, 0},{1, 0, 0},{1, 1, 0},{0, 1, 0},
		{0, 0, 1},{1, 0, 1},{1, 1, 1},{0, 1, 1}
};


static const int a2fPosXOffset[4][3] =
{
	{2, 0, 0},{2, 1, 0},
	{2, 0, 1},{2, 1, 1}
};

static const int a2fPosYOffset[4][3] =
{
	{1, 2, 0},{0, 2, 0},
 	{1, 2, 1},{0, 2, 1}
};

static const int a2fPosZOffset[4][3] =
{
	{0, 0, 2},{1, 0, 2},
	{1, 1, 2},{0, 1, 2}
};

static const int a2fPosXPosYOffset[2][3] =
{
	{2, 2, 0},{2, 2, 1}
};

static const int a2fPosXPosZOffset[2][3] =
{
 	{2, 0, 2},{2, 1, 2}
};

static const int a2fPosYPosZOffset[2][3] =
{
	{1, 2, 2},{0, 2, 2}
};


static const int a2fPosXPosZPosYOffset[3] =
{
	2, 2, 2
};

//a2fVertexOffset lists the positions, relative to vertex0, of each of the 8 vertices of a cube
static const int a2OddXOffset[8] =
{
	1,0,0,1,
 	1,0,0,1
};

static const int a2OddYOffset[8] =
{
	1,1,0,0,
	1,1,0,0
};

static const int a2OddZOffset[8] =
{
	1,1,1,1,
	0,0,0,0
};

//a2iEdgeConnection lists the index of the endpoint vertices for each of the 12 edges of the cube
static const int a2iEdgeConnection[12][2] =
{
		{0,1}, {1,2}, {2,3}, {3,0},
		{4,5}, {5,6}, {6,7}, {7,4},
		{0,4}, {1,5}, {2,6}, {3,7}
};

//a2fEdgeDirection lists the direction vector (vertex1-vertex0) for each edge in the cube
static const float a2fEdgeDirection[12][3] =
{
		{1.0, 0.0, 0.0},{0.0, 1.0, 0.0},{-1.0, 0.0, 0.0},{0.0, -1.0, 0.0},
		{1.0, 0.0, 0.0},{0.0, 1.0, 0.0},{-1.0, 0.0, 0.0},{0.0, -1.0, 0.0},
		{0.0, 0.0, 1.0},{0.0, 0.0, 1.0},{ 0.0, 0.0, 1.0},{0.0,  0.0, 1.0}
};

// right = 0, up = 1, back = 2
static const int edgeLookUp[12][4] =
{
	{0,0,0,0},{1,0,0,1},{0,1,0,0},{0,0,0,1},
	{0,0,1,0},{1,0,1,1},{0,1,1,0},{0,0,1,1},
	{0,0,0,2},{1,0,0,2},{1,1,0,2},{0,1,0,2}
};

// For any edge, if one vertex is inside of the surface and the other is outside of the surface
// then the edge intersects the surface
// For each of the 8 vertices of the cube can be two possible states : either inside or outside of the surface
// For any cube the are 2^8=256 possible sets of vertex states
// This table lists the edges intersected by the surface for all 256 possible vertex states
// There are 12 edges.  For each entry in the table, if edge #n is intersected, then bit #n is set to 1

int aiCubeEdgeFlags[256]=
{
        0x000, 0x109, 0x203, 0x30a, 0x406, 0x50f, 0x605, 0x70c, 0x80c, 0x905, 0xa0f, 0xb06, 0xc0a, 0xd03, 0xe09, 0xf00,
        0x190, 0x099, 0x393, 0x29a, 0x596, 0x49f, 0x795, 0x69c, 0x99c, 0x895, 0xb9f, 0xa96, 0xd9a, 0xc93, 0xf99, 0xe90,
        0x230, 0x339, 0x033, 0x13a, 0x636, 0x73f, 0x435, 0x53c, 0xa3c, 0xb35, 0x83f, 0x936, 0xe3a, 0xf33, 0xc39, 0xd30,
        0x3a0, 0x2a9, 0x1a3, 0x0aa, 0x7a6, 0x6af, 0x5a5, 0x4ac, 0xbac, 0xaa5, 0x9af, 0x8a6, 0xfaa, 0xea3, 0xda9, 0xca0,
        0x460, 0x569, 0x663, 0x76a, 0x066, 0x16f, 0x265, 0x36c, 0xc6c, 0xd65, 0xe6f, 0xf66, 0x86a, 0x963, 0xa69, 0xb60,
        0x5f0, 0x4f9, 0x7f3, 0x6fa, 0x1f6, 0x0ff, 0x3f5, 0x2fc, 0xdfc, 0xcf5, 0xfff, 0xef6, 0x9fa, 0x8f3, 0xbf9, 0xaf0,
        0x650, 0x759, 0x453, 0x55a, 0x256, 0x35f, 0x055, 0x15c, 0xe5c, 0xf55, 0xc5f, 0xd56, 0xa5a, 0xb53, 0x859, 0x950,
        0x7c0, 0x6c9, 0x5c3, 0x4ca, 0x3c6, 0x2cf, 0x1c5, 0x0cc, 0xfcc, 0xec5, 0xdcf, 0xcc6, 0xbca, 0xac3, 0x9c9, 0x8c0,
        0x8c0, 0x9c9, 0xac3, 0xbca, 0xcc6, 0xdcf, 0xec5, 0xfcc, 0x0cc, 0x1c5, 0x2cf, 0x3c6, 0x4ca, 0x5c3, 0x6c9, 0x7c0,
        0x950, 0x859, 0xb53, 0xa5a, 0xd56, 0xc5f, 0xf55, 0xe5c, 0x15c, 0x055, 0x35f, 0x256, 0x55a, 0x453, 0x759, 0x650,
        0xaf0, 0xbf9, 0x8f3, 0x9fa, 0xef6, 0xfff, 0xcf5, 0xdfc, 0x2fc, 0x3f5, 0x0ff, 0x1f6, 0x6fa, 0x7f3, 0x4f9, 0x5f0,
        0xb60, 0xa69, 0x963, 0x86a, 0xf66, 0xe6f, 0xd65, 0xc6c, 0x36c, 0x265, 0x16f, 0x066, 0x76a, 0x663, 0x569, 0x460,
        0xca0, 0xda9, 0xea3, 0xfaa, 0x8a6, 0x9af, 0xaa5, 0xbac, 0x4ac, 0x5a5, 0x6af, 0x7a6, 0x0aa, 0x1a3, 0x2a9, 0x3a0,
        0xd30, 0xc39, 0xf33, 0xe3a, 0x936, 0x83f, 0xb35, 0xa3c, 0x53c, 0x435, 0x73f, 0x636, 0x13a, 0x033, 0x339, 0x230,
        0xe90, 0xf99, 0xc93, 0xd9a, 0xa96, 0xb9f, 0x895, 0x99c, 0x69c, 0x795, 0x49f, 0x596, 0x29a, 0x393, 0x099, 0x190,
        0xf00, 0xe09, 0xd03, 0xc0a, 0xb06, 0xa0f, 0x905, 0x80c, 0x70c, 0x605, 0x50f, 0x406, 0x30a, 0x203, 0x109, 0x000
};

//  For each of the possible vertex states listed in aiCubeEdgeFlags there is a specific triangulation
//  of the edge intersection points.  a2iTriangleConnectionTable lists all of thminvals[cur_level]-> in the form of
//  0-5 edge triples with the list terminated by the invalid value -1.
//  For example: a2iTriangleConnectionTable[3] list the 2 triangles formed when corner[0]
//  and corner[1] are inside of the surface, but the rest of the cube is not.
//
//  I found this table in an example program someone wrote long ago.  It was probably generated by hand

int a2iTriangleConnectionTable[256][16] =
{
        {-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1},
        {0, 8, 3, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1},
        {0, 1, 9, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1},
        {1, 8, 3, 9, 8, 1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1},
        {1, 2, 10, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1},
        {0, 8, 3, 1, 2, 10, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1},
        {9, 2, 10, 0, 2, 9, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1},
        {2, 8, 3, 2, 10, 8, 10, 9, 8, -1, -1, -1, -1, -1, -1, -1},
        {3, 11, 2, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1},
        {0, 11, 2, 8, 11, 0, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1},
        {1, 9, 0, 2, 3, 11, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1},
        {1, 11, 2, 1, 9, 11, 9, 8, 11, -1, -1, -1, -1, -1, -1, -1},
        {3, 10, 1, 11, 10, 3, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1},
        {0, 10, 1, 0, 8, 10, 8, 11, 10, -1, -1, -1, -1, -1, -1, -1},
        {3, 9, 0, 3, 11, 9, 11, 10, 9, -1, -1, -1, -1, -1, -1, -1},
        {9, 8, 10, 10, 8, 11, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1},
        {4, 7, 8, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1},
        {4, 3, 0, 7, 3, 4, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1},
        {0, 1, 9, 8, 4, 7, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1},
        {4, 1, 9, 4, 7, 1, 7, 3, 1, -1, -1, -1, -1, -1, -1, -1},
        {1, 2, 10, 8, 4, 7, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1},
        {3, 4, 7, 3, 0, 4, 1, 2, 10, -1, -1, -1, -1, -1, -1, -1},
        {9, 2, 10, 9, 0, 2, 8, 4, 7, -1, -1, -1, -1, -1, -1, -1},
        {2, 10, 9, 2, 9, 7, 2, 7, 3, 7, 9, 4, -1, -1, -1, -1},
        {8, 4, 7, 3, 11, 2, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1},
        {11, 4, 7, 11, 2, 4, 2, 0, 4, -1, -1, -1, -1, -1, -1, -1},
        {9, 0, 1, 8, 4, 7, 2, 3, 11, -1, -1, -1, -1, -1, -1, -1},
        {4, 7, 11, 9, 4, 11, 9, 11, 2, 9, 2, 1, -1, -1, -1, -1},
        {3, 10, 1, 3, 11, 10, 7, 8, 4, -1, -1, -1, -1, -1, -1, -1},
        {1, 11, 10, 1, 4, 11, 1, 0, 4, 7, 11, 4, -1, -1, -1, -1},
        {4, 7, 8, 9, 0, 11, 9, 11, 10, 11, 0, 3, -1, -1, -1, -1},
        {4, 7, 11, 4, 11, 9, 9, 11, 10, -1, -1, -1, -1, -1, -1, -1},
        {9, 5, 4, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1},
        {9, 5, 4, 0, 8, 3, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1},
        {0, 5, 4, 1, 5, 0, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1},
        {8, 5, 4, 8, 3, 5, 3, 1, 5, -1, -1, -1, -1, -1, -1, -1},
        {1, 2, 10, 9, 5, 4, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1},
        {3, 0, 8, 1, 2, 10, 4, 9, 5, -1, -1, -1, -1, -1, -1, -1},
        {5, 2, 10, 5, 4, 2, 4, 0, 2, -1, -1, -1, -1, -1, -1, -1},
        {2, 10, 5, 3, 2, 5, 3, 5, 4, 3, 4, 8, -1, -1, -1, -1},
        {9, 5, 4, 2, 3, 11, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1},
        {0, 11, 2, 0, 8, 11, 4, 9, 5, -1, -1, -1, -1, -1, -1, -1},
        {0, 5, 4, 0, 1, 5, 2, 3, 11, -1, -1, -1, -1, -1, -1, -1},
        {2, 1, 5, 2, 5, 8, 2, 8, 11, 4, 8, 5, -1, -1, -1, -1},
        {10, 3, 11, 10, 1, 3, 9, 5, 4, -1, -1, -1, -1, -1, -1, -1},
        {4, 9, 5, 0, 8, 1, 8, 10, 1, 8, 11, 10, -1, -1, -1, -1},
        {5, 4, 0, 5, 0, 11, 5, 11, 10, 11, 0, 3, -1, -1, -1, -1},
        {5, 4, 8, 5, 8, 10, 10, 8, 11, -1, -1, -1, -1, -1, -1, -1},
        {9, 7, 8, 5, 7, 9, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1},
        {9, 3, 0, 9, 5, 3, 5, 7, 3, -1, -1, -1, -1, -1, -1, -1},
        {0, 7, 8, 0, 1, 7, 1, 5, 7, -1, -1, -1, -1, -1, -1, -1},
        {1, 5, 3, 3, 5, 7, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1},
        {9, 7, 8, 9, 5, 7, 10, 1, 2, -1, -1, -1, -1, -1, -1, -1},
        {10, 1, 2, 9, 5, 0, 5, 3, 0, 5, 7, 3, -1, -1, -1, -1},
        {8, 0, 2, 8, 2, 5, 8, 5, 7, 10, 5, 2, -1, -1, -1, -1},
        {2, 10, 5, 2, 5, 3, 3, 5, 7, -1, -1, -1, -1, -1, -1, -1},
        {7, 9, 5, 7, 8, 9, 3, 11, 2, -1, -1, -1, -1, -1, -1, -1},
        {9, 5, 7, 9, 7, 2, 9, 2, 0, 2, 7, 11, -1, -1, -1, -1},
        {2, 3, 11, 0, 1, 8, 1, 7, 8, 1, 5, 7, -1, -1, -1, -1},
        {11, 2, 1, 11, 1, 7, 7, 1, 5, -1, -1, -1, -1, -1, -1, -1},
        {9, 5, 8, 8, 5, 7, 10, 1, 3, 10, 3, 11, -1, -1, -1, -1},
        {5, 7, 0, 5, 0, 9, 7, 11, 0, 1, 0, 10, 11, 10, 0, -1},
        {11, 10, 0, 11, 0, 3, 10, 5, 0, 8, 0, 7, 5, 7, 0, -1},
        {11, 10, 5, 7, 11, 5, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1},
        {10, 6, 5, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1},
        {0, 8, 3, 5, 10, 6, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1},
        {9, 0, 1, 5, 10, 6, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1},
        {1, 8, 3, 1, 9, 8, 5, 10, 6, -1, -1, -1, -1, -1, -1, -1},
        {1, 6, 5, 2, 6, 1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1},
        {1, 6, 5, 1, 2, 6, 3, 0, 8, -1, -1, -1, -1, -1, -1, -1},
        {9, 6, 5, 9, 0, 6, 0, 2, 6, -1, -1, -1, -1, -1, -1, -1},
        {5, 9, 8, 5, 8, 2, 5, 2, 6, 3, 2, 8, -1, -1, -1, -1},
        {2, 3, 11, 10, 6, 5, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1},
        {11, 0, 8, 11, 2, 0, 10, 6, 5, -1, -1, -1, -1, -1, -1, -1},
        {0, 1, 9, 2, 3, 11, 5, 10, 6, -1, -1, -1, -1, -1, -1, -1},
        {5, 10, 6, 1, 9, 2, 9, 11, 2, 9, 8, 11, -1, -1, -1, -1},
        {6, 3, 11, 6, 5, 3, 5, 1, 3, -1, -1, -1, -1, -1, -1, -1},
        {0, 8, 11, 0, 11, 5, 0, 5, 1, 5, 11, 6, -1, -1, -1, -1},
        {3, 11, 6, 0, 3, 6, 0, 6, 5, 0, 5, 9, -1, -1, -1, -1},
        {6, 5, 9, 6, 9, 11, 11, 9, 8, -1, -1, -1, -1, -1, -1, -1},
        {5, 10, 6, 4, 7, 8, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1},
        {4, 3, 0, 4, 7, 3, 6, 5, 10, -1, -1, -1, -1, -1, -1, -1},
        {1, 9, 0, 5, 10, 6, 8, 4, 7, -1, -1, -1, -1, -1, -1, -1},
        {10, 6, 5, 1, 9, 7, 1, 7, 3, 7, 9, 4, -1, -1, -1, -1},
        {6, 1, 2, 6, 5, 1, 4, 7, 8, -1, -1, -1, -1, -1, -1, -1},
        {1, 2, 5, 5, 2, 6, 3, 0, 4, 3, 4, 7, -1, -1, -1, -1},
        {8, 4, 7, 9, 0, 5, 0, 6, 5, 0, 2, 6, -1, -1, -1, -1},
        {7, 3, 9, 7, 9, 4, 3, 2, 9, 5, 9, 6, 2, 6, 9, -1},
        {3, 11, 2, 7, 8, 4, 10, 6, 5, -1, -1, -1, -1, -1, -1, -1},
        {5, 10, 6, 4, 7, 2, 4, 2, 0, 2, 7, 11, -1, -1, -1, -1},
        {0, 1, 9, 4, 7, 8, 2, 3, 11, 5, 10, 6, -1, -1, -1, -1},
        {9, 2, 1, 9, 11, 2, 9, 4, 11, 7, 11, 4, 5, 10, 6, -1},
        {8, 4, 7, 3, 11, 5, 3, 5, 1, 5, 11, 6, -1, -1, -1, -1},
        {5, 1, 11, 5, 11, 6, 1, 0, 11, 7, 11, 4, 0, 4, 11, -1},
        {0, 5, 9, 0, 6, 5, 0, 3, 6, 11, 6, 3, 8, 4, 7, -1},
        {6, 5, 9, 6, 9, 11, 4, 7, 9, 7, 11, 9, -1, -1, -1, -1},
        {10, 4, 9, 6, 4, 10, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1},
        {4, 10, 6, 4, 9, 10, 0, 8, 3, -1, -1, -1, -1, -1, -1, -1},
        {10, 0, 1, 10, 6, 0, 6, 4, 0, -1, -1, -1, -1, -1, -1, -1},
        {8, 3, 1, 8, 1, 6, 8, 6, 4, 6, 1, 10, -1, -1, -1, -1},
        {1, 4, 9, 1, 2, 4, 2, 6, 4, -1, -1, -1, -1, -1, -1, -1},
        {3, 0, 8, 1, 2, 9, 2, 4, 9, 2, 6, 4, -1, -1, -1, -1},
        {0, 2, 4, 4, 2, 6, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1},
        {8, 3, 2, 8, 2, 4, 4, 2, 6, -1, -1, -1, -1, -1, -1, -1},
        {10, 4, 9, 10, 6, 4, 11, 2, 3, -1, -1, -1, -1, -1, -1, -1},
        {0, 8, 2, 2, 8, 11, 4, 9, 10, 4, 10, 6, -1, -1, -1, -1},
        {3, 11, 2, 0, 1, 6, 0, 6, 4, 6, 1, 10, -1, -1, -1, -1},
        {6, 4, 1, 6, 1, 10, 4, 8, 1, 2, 1, 11, 8, 11, 1, -1},
        {9, 6, 4, 9, 3, 6, 9, 1, 3, 11, 6, 3, -1, -1, -1, -1},
        {8, 11, 1, 8, 1, 0, 11, 6, 1, 9, 1, 4, 6, 4, 1, -1},
        {3, 11, 6, 3, 6, 0, 0, 6, 4, -1, -1, -1, -1, -1, -1, -1},
        {6, 4, 8, 11, 6, 8, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1},
        {7, 10, 6, 7, 8, 10, 8, 9, 10, -1, -1, -1, -1, -1, -1, -1},
        {0, 7, 3, 0, 10, 7, 0, 9, 10, 6, 7, 10, -1, -1, -1, -1},
        {10, 6, 7, 1, 10, 7, 1, 7, 8, 1, 8, 0, -1, -1, -1, -1},
        {10, 6, 7, 10, 7, 1, 1, 7, 3, -1, -1, -1, -1, -1, -1, -1},
        {1, 2, 6, 1, 6, 8, 1, 8, 9, 8, 6, 7, -1, -1, -1, -1},
        {2, 6, 9, 2, 9, 1, 6, 7, 9, 0, 9, 3, 7, 3, 9, -1},
        {7, 8, 0, 7, 0, 6, 6, 0, 2, -1, -1, -1, -1, -1, -1, -1},
        {7, 3, 2, 6, 7, 2, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1},
        {2, 3, 11, 10, 6, 8, 10, 8, 9, 8, 6, 7, -1, -1, -1, -1},
        {2, 0, 7, 2, 7, 11, 0, 9, 7, 6, 7, 10, 9, 10, 7, -1},
        {1, 8, 0, 1, 7, 8, 1, 10, 7, 6, 7, 10, 2, 3, 11, -1},
        {11, 2, 1, 11, 1, 7, 10, 6, 1, 6, 7, 1, -1, -1, -1, -1},
        {8, 9, 6, 8, 6, 7, 9, 1, 6, 11, 6, 3, 1, 3, 6, -1},
        {0, 9, 1, 11, 6, 7, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1},
        {7, 8, 0, 7, 0, 6, 3, 11, 0, 11, 6, 0, -1, -1, -1, -1},
        {7, 11, 6, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1},
        {7, 6, 11, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1},
        {3, 0, 8, 11, 7, 6, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1},
        {0, 1, 9, 11, 7, 6, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1},
        {8, 1, 9, 8, 3, 1, 11, 7, 6, -1, -1, -1, -1, -1, -1, -1},
        {10, 1, 2, 6, 11, 7, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1},
        {1, 2, 10, 3, 0, 8, 6, 11, 7, -1, -1, -1, -1, -1, -1, -1},
        {2, 9, 0, 2, 10, 9, 6, 11, 7, -1, -1, -1, -1, -1, -1, -1},
        {6, 11, 7, 2, 10, 3, 10, 8, 3, 10, 9, 8, -1, -1, -1, -1},
        {7, 2, 3, 6, 2, 7, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1},
        {7, 0, 8, 7, 6, 0, 6, 2, 0, -1, -1, -1, -1, -1, -1, -1},
        {2, 7, 6, 2, 3, 7, 0, 1, 9, -1, -1, -1, -1, -1, -1, -1},
        {1, 6, 2, 1, 8, 6, 1, 9, 8, 8, 7, 6, -1, -1, -1, -1},
        {10, 7, 6, 10, 1, 7, 1, 3, 7, -1, -1, -1, -1, -1, -1, -1},
        {10, 7, 6, 1, 7, 10, 1, 8, 7, 1, 0, 8, -1, -1, -1, -1},
        {0, 3, 7, 0, 7, 10, 0, 10, 9, 6, 10, 7, -1, -1, -1, -1},
        {7, 6, 10, 7, 10, 8, 8, 10, 9, -1, -1, -1, -1, -1, -1, -1},
        {6, 8, 4, 11, 8, 6, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1},
        {3, 6, 11, 3, 0, 6, 0, 4, 6, -1, -1, -1, -1, -1, -1, -1},
        {8, 6, 11, 8, 4, 6, 9, 0, 1, -1, -1, -1, -1, -1, -1, -1},
        {9, 4, 6, 9, 6, 3, 9, 3, 1, 11, 3, 6, -1, -1, -1, -1},
        {6, 8, 4, 6, 11, 8, 2, 10, 1, -1, -1, -1, -1, -1, -1, -1},
        {1, 2, 10, 3, 0, 11, 0, 6, 11, 0, 4, 6, -1, -1, -1, -1},
        {4, 11, 8, 4, 6, 11, 0, 2, 9, 2, 10, 9, -1, -1, -1, -1},
        {10, 9, 3, 10, 3, 2, 9, 4, 3, 11, 3, 6, 4, 6, 3, -1},
        {8, 2, 3, 8, 4, 2, 4, 6, 2, -1, -1, -1, -1, -1, -1, -1},
        {0, 4, 2, 4, 6, 2, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1},
        {1, 9, 0, 2, 3, 4, 2, 4, 6, 4, 3, 8, -1, -1, -1, -1},
        {1, 9, 4, 1, 4, 2, 2, 4, 6, -1, -1, -1, -1, -1, -1, -1},
        {8, 1, 3, 8, 6, 1, 8, 4, 6, 6, 10, 1, -1, -1, -1, -1},
        {10, 1, 0, 10, 0, 6, 6, 0, 4, -1, -1, -1, -1, -1, -1, -1},
        {4, 6, 3, 4, 3, 8, 6, 10, 3, 0, 3, 9, 10, 9, 3, -1},
        {10, 9, 4, 6, 10, 4, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1},
        {4, 9, 5, 7, 6, 11, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1},
        {0, 8, 3, 4, 9, 5, 11, 7, 6, -1, -1, -1, -1, -1, -1, -1},
        {5, 0, 1, 5, 4, 0, 7, 6, 11, -1, -1, -1, -1, -1, -1, -1},
        {11, 7, 6, 8, 3, 4, 3, 5, 4, 3, 1, 5, -1, -1, -1, -1},
        {9, 5, 4, 10, 1, 2, 7, 6, 11, -1, -1, -1, -1, -1, -1, -1},
        {6, 11, 7, 1, 2, 10, 0, 8, 3, 4, 9, 5, -1, -1, -1, -1},
        {7, 6, 11, 5, 4, 10, 4, 2, 10, 4, 0, 2, -1, -1, -1, -1},
        {3, 4, 8, 3, 5, 4, 3, 2, 5, 10, 5, 2, 11, 7, 6, -1},
        {7, 2, 3, 7, 6, 2, 5, 4, 9, -1, -1, -1, -1, -1, -1, -1},
        {9, 5, 4, 0, 8, 6, 0, 6, 2, 6, 8, 7, -1, -1, -1, -1},
        {3, 6, 2, 3, 7, 6, 1, 5, 0, 5, 4, 0, -1, -1, -1, -1},
        {6, 2, 8, 6, 8, 7, 2, 1, 8, 4, 8, 5, 1, 5, 8, -1},
        {9, 5, 4, 10, 1, 6, 1, 7, 6, 1, 3, 7, -1, -1, -1, -1},
        {1, 6, 10, 1, 7, 6, 1, 0, 7, 8, 7, 0, 9, 5, 4, -1},
        {4, 0, 10, 4, 10, 5, 0, 3, 10, 6, 10, 7, 3, 7, 10, -1},
        {7, 6, 10, 7, 10, 8, 5, 4, 10, 4, 8, 10, -1, -1, -1, -1},
        {6, 9, 5, 6, 11, 9, 11, 8, 9, -1, -1, -1, -1, -1, -1, -1},
        {3, 6, 11, 0, 6, 3, 0, 5, 6, 0, 9, 5, -1, -1, -1, -1},
        {0, 11, 8, 0, 5, 11, 0, 1, 5, 5, 6, 11, -1, -1, -1, -1},
        {6, 11, 3, 6, 3, 5, 5, 3, 1, -1, -1, -1, -1, -1, -1, -1},
        {1, 2, 10, 9, 5, 11, 9, 11, 8, 11, 5, 6, -1, -1, -1, -1},
        {0, 11, 3, 0, 6, 11, 0, 9, 6, 5, 6, 9, 1, 2, 10, -1},
        {11, 8, 5, 11, 5, 6, 8, 0, 5, 10, 5, 2, 0, 2, 5, -1},
        {6, 11, 3, 6, 3, 5, 2, 10, 3, 10, 5, 3, -1, -1, -1, -1},
        {5, 8, 9, 5, 2, 8, 5, 6, 2, 3, 8, 2, -1, -1, -1, -1},
        {9, 5, 6, 9, 6, 0, 0, 6, 2, -1, -1, -1, -1, -1, -1, -1},
        {1, 5, 8, 1, 8, 0, 5, 6, 8, 3, 8, 2, 6, 2, 8, -1},
        {1, 5, 6, 2, 1, 6, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1},
        {1, 3, 6, 1, 6, 10, 3, 8, 6, 5, 6, 9, 8, 9, 6, -1},
        {10, 1, 0, 10, 0, 6, 9, 5, 0, 5, 6, 0, -1, -1, -1, -1},
        {0, 3, 8, 5, 6, 10, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1},
        {10, 5, 6, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1},
        {11, 5, 10, 7, 5, 11, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1},
        {11, 5, 10, 11, 7, 5, 8, 3, 0, -1, -1, -1, -1, -1, -1, -1},
        {5, 11, 7, 5, 10, 11, 1, 9, 0, -1, -1, -1, -1, -1, -1, -1},
        {10, 7, 5, 10, 11, 7, 9, 8, 1, 8, 3, 1, -1, -1, -1, -1},
        {11, 1, 2, 11, 7, 1, 7, 5, 1, -1, -1, -1, -1, -1, -1, -1},
        {0, 8, 3, 1, 2, 7, 1, 7, 5, 7, 2, 11, -1, -1, -1, -1},
        {9, 7, 5, 9, 2, 7, 9, 0, 2, 2, 11, 7, -1, -1, -1, -1},
        {7, 5, 2, 7, 2, 11, 5, 9, 2, 3, 2, 8, 9, 8, 2, -1},
        {2, 5, 10, 2, 3, 5, 3, 7, 5, -1, -1, -1, -1, -1, -1, -1},
        {8, 2, 0, 8, 5, 2, 8, 7, 5, 10, 2, 5, -1, -1, -1, -1},
        {9, 0, 1, 5, 10, 3, 5, 3, 7, 3, 10, 2, -1, -1, -1, -1},
        {9, 8, 2, 9, 2, 1, 8, 7, 2, 10, 2, 5, 7, 5, 2, -1},
        {1, 3, 5, 3, 7, 5, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1},
        {0, 8, 7, 0, 7, 1, 1, 7, 5, -1, -1, -1, -1, -1, -1, -1},
        {9, 0, 3, 9, 3, 5, 5, 3, 7, -1, -1, -1, -1, -1, -1, -1},
        {9, 8, 7, 5, 9, 7, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1},
        {5, 8, 4, 5, 10, 8, 10, 11, 8, -1, -1, -1, -1, -1, -1, -1},
        {5, 0, 4, 5, 11, 0, 5, 10, 11, 11, 3, 0, -1, -1, -1, -1},
        {0, 1, 9, 8, 4, 10, 8, 10, 11, 10, 4, 5, -1, -1, -1, -1},
        {10, 11, 4, 10, 4, 5, 11, 3, 4, 9, 4, 1, 3, 1, 4, -1},
        {2, 5, 1, 2, 8, 5, 2, 11, 8, 4, 5, 8, -1, -1, -1, -1},
        {0, 4, 11, 0, 11, 3, 4, 5, 11, 2, 11, 1, 5, 1, 11, -1},
        {0, 2, 5, 0, 5, 9, 2, 11, 5, 4, 5, 8, 11, 8, 5, -1},
        {9, 4, 5, 2, 11, 3, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1},
        {2, 5, 10, 3, 5, 2, 3, 4, 5, 3, 8, 4, -1, -1, -1, -1},
        {5, 10, 2, 5, 2, 4, 4, 2, 0, -1, -1, -1, -1, -1, -1, -1},
        {3, 10, 2, 3, 5, 10, 3, 8, 5, 4, 5, 8, 0, 1, 9, -1},
        {5, 10, 2, 5, 2, 4, 1, 9, 2, 9, 4, 2, -1, -1, -1, -1},
        {8, 4, 5, 8, 5, 3, 3, 5, 1, -1, -1, -1, -1, -1, -1, -1},
        {0, 4, 5, 1, 0, 5, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1},
        {8, 4, 5, 8, 5, 3, 9, 0, 5, 0, 3, 5, -1, -1, -1, -1},
        {9, 4, 5, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1},
        {4, 11, 7, 4, 9, 11, 9, 10, 11, -1, -1, -1, -1, -1, -1, -1},
        {0, 8, 3, 4, 9, 7, 9, 11, 7, 9, 10, 11, -1, -1, -1, -1},
        {1, 10, 11, 1, 11, 4, 1, 4, 0, 7, 4, 11, -1, -1, -1, -1},
        {3, 1, 4, 3, 4, 8, 1, 10, 4, 7, 4, 11, 10, 11, 4, -1},
        {4, 11, 7, 9, 11, 4, 9, 2, 11, 9, 1, 2, -1, -1, -1, -1},
        {9, 7, 4, 9, 11, 7, 9, 1, 11, 2, 11, 1, 0, 8, 3, -1},
        {11, 7, 4, 11, 4, 2, 2, 4, 0, -1, -1, -1, -1, -1, -1, -1},
        {11, 7, 4, 11, 4, 2, 8, 3, 4, 3, 2, 4, -1, -1, -1, -1},
        {2, 9, 10, 2, 7, 9, 2, 3, 7, 7, 4, 9, -1, -1, -1, -1},
        {9, 10, 7, 9, 7, 4, 10, 2, 7, 8, 7, 0, 2, 0, 7, -1},
        {3, 7, 10, 3, 10, 2, 7, 4, 10, 1, 10, 0, 4, 0, 10, -1},
        {1, 10, 2, 8, 7, 4, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1},
        {4, 9, 1, 4, 1, 7, 7, 1, 3, -1, -1, -1, -1, -1, -1, -1},
        {4, 9, 1, 4, 1, 7, 0, 8, 1, 8, 7, 1, -1, -1, -1, -1},
        {4, 0, 3, 7, 4, 3, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1},
        {4, 8, 7, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1},
        {9, 10, 8, 10, 11, 8, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1},
        {3, 0, 9, 3, 9, 11, 11, 9, 10, -1, -1, -1, -1, -1, -1, -1},
        {0, 1, 10, 0, 10, 8, 8, 10, 11, -1, -1, -1, -1, -1, -1, -1},
        {3, 1, 10, 11, 3, 10, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1},
        {1, 2, 11, 1, 11, 9, 9, 11, 8, -1, -1, -1, -1, -1, -1, -1},
        {3, 0, 9, 3, 9, 11, 1, 2, 9, 2, 11, 9, -1, -1, -1, -1},
        {0, 2, 11, 8, 0, 11, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1},
        {3, 2, 11, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1},
        {2, 3, 8, 2, 8, 10, 10, 8, 9, -1, -1, -1, -1, -1, -1, -1},
        {9, 10, 2, 0, 9, 2, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1},
        {2, 3, 8, 2, 8, 10, 0, 1, 8, 1, 10, 8, -1, -1, -1, -1},
        {1, 10, 2, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1},
        {1, 3, 8, 9, 1, 8, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1},
        {0, 9, 1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1},
        {0, 3, 8, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1},
        {-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1}
};

ColorRGBGenerator::ColorRGBGenerator()
	: rgbmode(0), originx(0), originy(0), originz(0), inner(0.0), outer(0.0), minimum(0.0), maximum(0.0), needtorecolor(1), colormap(0), em_data(0)
{
}

ColorRGBGenerator::ColorRGBGenerator(EMData* data)
	: rgbmode(0), minimum(0.0), maximum(0.0), needtorecolor(1), colormap(0)
{
	set_data(data);
}

void ColorRGBGenerator::set_data(EMData* data)
{
	em_data = data;
	originx = data->get_xsize()/2;
	originy = data->get_ysize()/2;
	originz = data->get_zsize()/2;
	inner = 0;
	outer = (float)originx;
}

void ColorRGBGenerator::set_cmap_data(EMData* data)
{
	cmap = data;
	setMinMax(data->get_attr("minimum"), data->get_attr("maximum"));
}

void ColorRGBGenerator::generateRadialColorMap()
{

	int size = int(sqrt((float)originx*originx + originy*originy + originz*originz));

	if(colormap) delete colormap;
	colormap = new float[size*3];

	for(int i = 0; i < size; i++){
		float normrad = 4.189f*(i - inner)/(outer - inner);
		if(normrad < 2.094){
			if (normrad < 0.0) normrad = 0.0;
			colormap[i*3] = 0.5f*(1 + cos(normrad)/cos(1.047f - normrad));
			colormap[i*3 + 1] = 1.5f - colormap[i*3];
			colormap[i*3 + 2] = 0.0;
		}
		if(normrad >= 2.094){
			if (normrad > 4.189f) normrad = 4.189f;
			normrad -= 2.094f;
			colormap[i*3] = 0.0;
			colormap[i*3 + 1] = 0.5f*(1 + cos(normrad)/cos(1.047f - normrad));
			colormap[i*3 + 2] = 1.5f - colormap[i*3 + 1];
		}
	}
}

float* ColorRGBGenerator::getRGBColor(int x, int y, int z)
{
	// Get data using radial color info
	if (rgbmode == 1){
		//calculate radius
		float rad = sqrt(float(pow(x-originx,2) + pow(y-originy,2) + pow(z-originz,2)));

		//This indicates that new color info needs to be bound (to the GPU)
		if(needtorecolor){
			generateRadialColorMap();
			needtorecolor = false;
		}

		return &colormap[int(rad)*3];
	}
	// Get data using color map
	if (rgbmode == 2){
		float value = cmap->get_value_at(x, y, z);
		value = 4.189f*(value - minimum)/(maximum - minimum);
		if(value < 2.094){
			if (value < 0.0) value = 0.0;
			rgb[0] = 0.5f*(1 + cos(value)/cos(1.047f - value));
			rgb[1] = 1.5f - rgb[0];
			rgb[2] = 0.0;
		}
		if(value >= 2.094){
			if (value > 4.189f) value = 4.189f;
			value -= 2.094f;
			rgb[0] = 0.0;
			rgb[1] = 0.5f*(1 + cos(value)/cos(1.047f - value));
			rgb[2] = 1.5f - rgb[1];
		}

		return &rgb[0];
	}

	return &colormap[0];
}

MarchingCubes::MarchingCubes()
	: _isodl(0), needtobind(1)
{
if ((int(glGetString(GL_VERSION)[0])-48)>2)
	rgbgenerator = ColorRGBGenerator();
}

MarchingCubes::MarchingCubes(EMData * em)
	: _isodl(0)
{
if ((int(glGetString(GL_VERSION)[0])-48)>2)
	rgbgenerator = ColorRGBGenerator();

set_data(em);
}



void MarchingCubes::clear_min_max_vals()
{
	for (vector<EMData*>::iterator it = minvals.begin(); it != minvals.end(); ++it)
	{
		if ( (*it) != 0 ) delete *it;
	}
	minvals.clear();

	for (vector<EMData*>::iterator it = maxvals.begin(); it != maxvals.end(); ++it)
	{
		if ( (*it) != 0 ) delete *it;
	}
	maxvals.clear();
}

bool MarchingCubes::calculate_min_max_vals()
{

	if (_emdata == NULL ) throw NullPointerException("Error, cannot generate search tree if the overriding EMData object is NULL");

	clear_min_max_vals();

	int nx = _emdata->get_xsize();
	int ny = _emdata->get_ysize();
	int nz = _emdata->get_zsize();

	// Create the binary min max tree
	while ( nx > 1 || ny > 1 || nz > 1 )
	{
		int size = minvals.size();

		if ( size == 0 ){
			Dict a;
			// Setting search to 3 at the bottom level is most important.
			// FIXME - d.woolford add comments heere
			a["search"] = 3;
			minvals.push_back(_emdata->process("math.minshrink",a));
			maxvals.push_back(_emdata->process("math.maxshrink",a));
		}else {
			minvals.push_back(minvals[size-1]->process("math.minshrink"));
			maxvals.push_back(maxvals[size-1]->process("math.maxshrink"));
		}

		nx = minvals[size]->get_xsize();
		ny = minvals[size]->get_ysize();
		nz = minvals[size]->get_zsize();
#if MARCHING_CUBES_DEBUG
		cout << "dims are " << nx << " " << ny << " " << nz << endl;
#endif
	}

	drawing_level = -1;

	return true;
}

MarchingCubes::~MarchingCubes() {
	clear_min_max_vals();
}

Dict MarchingCubes::get_isosurface()
{
	calculate_surface();
	Dict d;
	d.put("points", (float*)pp.data());
	for (unsigned int i = 0; i < ff.size(); ++i ) ff[i] /= 3;
	d.put("faces", (unsigned int*)ff.data());
	d.put("normals", (float*)nn.data());
	d.put("size", (unsigned int)ff.size());
	return d;
}

void MarchingCubes::surface_face_z()
{
	float* f = pp.data();
	float* n = nn.data();
	for (unsigned int i = 0; i < pp.size(); i += 3 ) {
		if (f[i+2] == 0.5) continue;
		Vec3f z(0,0,1.0);
		Vec3f axis(-n[i+1],n[i],0);
		axis.normalize();

		Dict d;
		d["type"] = "spin";
		d["Omega"] =  90.f;
		d["n1"] = axis[0];
		d["n2"] = axis[1];
		d["n3"] = 0;
		Transform t(d);
		Vec3f delta = t*z;

		f[i] += delta[0]*.25f;
		f[i+1] += delta[1]*.25f;
		f[i+2] = 0.5;
	}

	for (unsigned int i = 0; i < nn.size(); i += 3 ) {
		n[i] = 0;
		n[i+1] = 0;
		n[i+2] = 1;
	}
}

void MarchingCubes::set_data(EMData* data)
{
	if ( data->get_zsize() == 1 ) throw ImageDimensionException("The z dimension of the image must be greater than 1");
	_emdata = data;
	calculate_min_max_vals();
	rgbgenerator.set_data(data);
}

void MarchingCubes::set_surface_value(const float value) {
	if(_surf_value == value)
		return;

	_surf_value = value;
}

void MarchingCubes::calculate_surface() {

	if ( _emdata == 0 ) throw NullPointerException("Error, attempt to generate isosurface, but the emdata image object has not been set");
	if ( minvals.size() == 0 || maxvals.size() == 0 ) throw NotExistingObjectException("Vector of EMData pointers", "Error, the min and max val search trees have not been created");

	point_map.clear();
	pp.clear();
	nn.clear();
	ff.clear();
	vv.clear();

#if MARCHING_CUBES_DEBUG
	int time0 = clock();
#endif

	float min = minvals[minvals.size()-1]->get_value_at(0,0,0);
	float max = maxvals[minvals.size()-1]->get_value_at(0,0,0);
	if ( min < _surf_value &&  max > _surf_value)
		draw_cube(0,0,0,minvals.size()-1);

#if MARCHING_CUBES_DEBUG
	int time1 = clock();
	cout << "It took " << (time1-time0) << " " << (float)(time1-time0)/CLOCKS_PER_SEC << " to traverse the search tree and generate polygons" << endl;
	cout << "... using surface value " << _surf_value << endl;
#endif
}

void MarchingCubes::draw_cube(const int x, const int y, const int z, const int cur_level ) {

	if ( cur_level == drawing_level )
	{
		EMData* e;
		if ( drawing_level == - 1 ) e = _emdata;
		else e = minvals[drawing_level];
		if ( x < (e->get_xsize()-1) && y < (e->get_ysize()-1) && z < (e->get_zsize()-1))
			marching_cube(x,y,z, cur_level);
	}
	else
	{
		EMData* e;
		if ( cur_level > 0 ) {
			int xsize = minvals[cur_level-1]->get_xsize();
			int ysize = minvals[cur_level-1]->get_ysize();
			int zsize = minvals[cur_level-1]->get_zsize();
			e = minvals[cur_level-1];
			for(int i=0; i<8; ++i )	{
				int xx = 2*x+a2fVertexOffset[i][0];
				if ( xx >= xsize ) continue;
				int yy = 2*y+a2fVertexOffset[i][1];
				if ( yy >= ysize ) continue;
				int zz = 2*z+a2fVertexOffset[i][2];
				if ( zz >= zsize ) continue;

				float min = minvals[cur_level-1]->get_value_at(xx,yy,zz);
				float max = maxvals[cur_level-1]->get_value_at(xx,yy,zz);
				if ( min < _surf_value &&  max > _surf_value)
					draw_cube(xx,yy,zz,cur_level-1);
			}
		}
		else {
			e = _emdata;
			for(int i=0; i<8; ++i )	{
					draw_cube(2*x+a2fVertexOffset[i][0],2*y+a2fVertexOffset[i][1],2*z+a2fVertexOffset[i][2],cur_level-1);
			}
		}

		if ( x == (minvals[cur_level]->get_xsize()-1) ) {
			if ( e->get_xsize() > 2*x ){
				for(int i=0; i<4; ++i )	{
					draw_cube(2*x+a2fPosXOffset[i][0],2*y+a2fPosXOffset[i][1],2*z+a2fPosXOffset[i][2],cur_level-1);
				}
			}
			if ( y == (minvals[cur_level]->get_ysize()-1) ) {
				if ( e->get_ysize() > 2*y ) {
					for(int i=0; i<2; ++i )	{
						draw_cube(2*x+a2fPosXPosYOffset[i][0],2*y+a2fPosXPosYOffset[i][1],2*z+a2fPosXPosYOffset[i][2],cur_level-1);
					}
				}
				if (  z == (minvals[cur_level]->get_zsize()-1) ){
					if ( e->get_zsize() > 2*z ) {
						draw_cube(2*x+2,2*y+2,2*z+2,cur_level-1);
					}
				}
			}
			if ( z == (minvals[cur_level]->get_zsize()-1) ) {
				if ( e->get_zsize() > 2*z ) {
					for(int i=0; i<2; ++i )	{
						draw_cube(2*x+a2fPosXPosZOffset[i][0],2*y+a2fPosXPosZOffset[i][1],2*z+a2fPosXPosZOffset[i][2],cur_level-1);
					}
				}
			}
		}
		if ( y == (minvals[cur_level]->get_ysize()-1) ) {
			if ( e->get_ysize() > 2*y ) {
				for(int i=0; i<4; ++i )	{
					draw_cube(2*x+a2fPosYOffset[i][0],2*y+a2fPosYOffset[i][1],2*z+a2fPosYOffset[i][2],cur_level-1);
				}
			}
			if ( z == (minvals[cur_level]->get_ysize()-1) ) {
				if ( e->get_zsize() > 2*z ) {
					for(int i=0; i<2; ++i )	{
						draw_cube(2*x+a2fPosYPosZOffset[i][0],2*y+a2fPosYPosZOffset[i][1],2*z+a2fPosYPosZOffset[i][2],cur_level-1);
					}
				}
			}
		}
		if ( z == (minvals[cur_level]->get_zsize()-1) ) {
			if ( e->get_zsize() > 2*z ) {
				for(int i=0; i<4; ++i )	{
					draw_cube(2*x+a2fPosZOffset[i][0],2*y+a2fPosZOffset[i][1],2*z+a2fPosZOffset[i][2],cur_level-1);
				}
			}
		}

	}
}

void MarchingCubes::get_normal(Vector3 &normal, int fX, int fY, int fZ)
{
    normal[0] = _emdata->get_value_at(fX-1, fY, fZ) - _emdata->get_value_at(fX+1, fY, fZ);
    normal[1] = _emdata->get_value_at(fX, fY-1, fZ) - _emdata->get_value_at(fX, fY+1, fZ);
    normal[2] = _emdata->get_value_at(fX, fY, fZ-1) - _emdata->get_value_at(fX, fY, fZ+1);
    normal.normalize();
}

float MarchingCubes::get_offset(float fValue1, float fValue2, float fValueDesired)
{
        float fDelta = fValue2 - fValue1;

        if(fDelta == 0.0f)
        {
                return 0.5f;
        }
        return (fValueDesired - fValue1)/fDelta;
}

int MarchingCubes::get_edge_num(int x, int y, int z, int edge) {
	// edge direction is right, down, back (x, y, z)
	return (x << 22) | (y << 12) | (z << 2) | edge;
}

void MarchingCubes::color_vertices()
{
	cc.clear();
	int scaling = pow(2,drawing_level + 1);		// Needed to account for sampling rate
	//Color vertices. We don't need to rerun marching cubes on color vertices, so this method improves effciency
	for(unsigned int i = 0; i < vv.size(); i+=3){
		float* color = rgbgenerator.getRGBColor(scaling*vv[i], scaling*vv[i+1], scaling*vv[i+2]);
		cc.insert(end(cc), color, color+3);
	}
	rgbgenerator.setNeedToRecolor(false);
}

void MarchingCubes::marching_cube(int fX, int fY, int fZ, int cur_level)
{
//	extern int aiCubeEdgeFlags[256];
//	extern int a2iTriangleConnectionTable[256][16];

	int iCorner, iVertex, iVertexTest, iEdge, iTriangle, iFlagIndex, iEdgeFlags;
	float fOffset;
	Vector3 sColor;
	float afCubeValue[8];
	float asEdgeVertex[12][3];
	int pointIndex[12];

	int fxScale = 1, fyScale = 1, fzScale = 1;
	if ( cur_level != -1 )
	{
		fxScale = _emdata->get_xsize()/minvals[cur_level]->get_xsize();
		fyScale = _emdata->get_ysize()/minvals[cur_level]->get_ysize();
		fzScale = _emdata->get_zsize()/minvals[cur_level]->get_zsize();
		for(iVertex = 0; iVertex < 8; iVertex++)
		{
			afCubeValue[iVertex] = _emdata->get_value_at( fxScale*(fX + a2fVertexOffset[iVertex][0]),
						fyScale*(fY + a2fVertexOffset[iVertex][1]), fzScale*(fZ + a2fVertexOffset[iVertex][2]));
		}
	}
	else
	{
		//Make a local copy of the values at the cube's corners
		for(iVertex = 0; iVertex < 8; iVertex++)
		{
			afCubeValue[iVertex] = _emdata->get_value_at( fX + a2fVertexOffset[iVertex][0],
					fY + a2fVertexOffset[iVertex][1], fZ + a2fVertexOffset[iVertex][2]);
		}
	}

	//Find which vertices are inside of the surface and which are outside
	iFlagIndex = 0;
	for(iVertexTest = 0; iVertexTest < 8; iVertexTest++)
	{
		if (_surf_value >= 0 ){
			if(afCubeValue[iVertexTest] <= _surf_value)
				iFlagIndex |= 1<<iVertexTest;
		}
		else {
			if(afCubeValue[iVertexTest] >= _surf_value)
				iFlagIndex |= 1<<iVertexTest;
		}
	}

	//Find which edges are intersected by the surface
	iEdgeFlags = aiCubeEdgeFlags[iFlagIndex];

	//If the cube is entirely inside or outside of the surface, then there will be no intersections
	if(iEdgeFlags == 0)
		return;

	//Find the point of intersection of the surface with each edge
	//Then find the normal to the surface at those points
	for(iEdge = 0; iEdge < 12; iEdge++)
	{
		//if there is an intersection on this edge
		if(iEdgeFlags & (1<<iEdge))
		{
			fOffset = get_offset(afCubeValue[ a2iEdgeConnection[iEdge][0] ],
								 afCubeValue[ a2iEdgeConnection[iEdge][1] ], _surf_value);

			if ( cur_level == -1 ){
				asEdgeVertex[iEdge][0] = fX + (a2fVertexOffset[ a2iEdgeConnection[iEdge][0] ][0]  +  fOffset * a2fEdgeDirection[iEdge][0]) + 0.5f;
				asEdgeVertex[iEdge][1] = fY + (a2fVertexOffset[ a2iEdgeConnection[iEdge][0] ][1]  +  fOffset * a2fEdgeDirection[iEdge][1]) + 0.5f;
				asEdgeVertex[iEdge][2] = fZ + (a2fVertexOffset[ a2iEdgeConnection[iEdge][0] ][2]  +  fOffset * a2fEdgeDirection[iEdge][2]) + 0.5f;
			} else {
				asEdgeVertex[iEdge][0] = fxScale*(fX + (a2fVertexOffset[ a2iEdgeConnection[iEdge][0] ][0]  +  fOffset * a2fEdgeDirection[iEdge][0])) + 0.5f;
				asEdgeVertex[iEdge][1] = fyScale*(fY + (a2fVertexOffset[ a2iEdgeConnection[iEdge][0] ][1]  +  fOffset * a2fEdgeDirection[iEdge][1])) + 0.5f;
				asEdgeVertex[iEdge][2] = fzScale*(fZ + (a2fVertexOffset[ a2iEdgeConnection[iEdge][0] ][2]  +  fOffset * a2fEdgeDirection[iEdge][2])) + 0.5f;
			}

			pointIndex[iEdge] = get_edge_num(fX+edgeLookUp[iEdge][0], fY+edgeLookUp[iEdge][1], fZ+edgeLookUp[iEdge][2], edgeLookUp[iEdge][3]);
		}
	}

	//Save voxel coords for later color processing
	int vox[3] = {fX, fY, fZ};

	//Draw the triangles that were found.  There can be up to five per cube
	for(iTriangle = 0; iTriangle < 5; iTriangle++)
	{
		if(a2iTriangleConnectionTable[iFlagIndex][3*iTriangle] < 0)
			break;

		float pts[3][3];
		for(iCorner = 0; iCorner < 3; iCorner++)
		{
			iVertex = a2iTriangleConnectionTable[iFlagIndex][3*iTriangle+iCorner];
			memcpy(&pts[iCorner][0],  &asEdgeVertex[iVertex][0], 3*sizeof(float));
		}



		float v1[3] = {pts[1][0]-pts[0][0],pts[1][1]-pts[0][1],pts[1][2]-pts[0][2]};
		float v2[3] = {pts[2][0]-pts[1][0],pts[2][1]-pts[1][1],pts[2][2]-pts[1][2]};

		float n[3] = { v1[1]*v2[2] - v1[2]*v2[1], v1[2]*v2[0] - v1[0]*v2[2], v1[0]*v2[1] - v1[1]*v2[0] };


		for(iCorner = 0; iCorner < 3; iCorner++)
		{
//			With vertex normalization
			iVertex = a2iTriangleConnectionTable[iFlagIndex][3*iTriangle+iCorner];
			map<int,int>::iterator it = point_map.find(pointIndex[iVertex]);
			if ( it == point_map.end() ){
				vv.insert(end(vv), vox, vox+3);
				int ss = pp.size();
				pp.insert(end(pp), pts[iCorner], pts[iCorner]+3);
				nn.insert(end(nn), n, n+3);
				ff.push_back(ss);
				point_map[pointIndex[iVertex]] = ss;
			} else {
				int idx = it->second;
				ff.push_back(idx);
				nn[idx] += n[0];
				nn[idx+1] += n[1];
				nn[idx+2] += n[2];
			}
		}
	}
}

#endif
