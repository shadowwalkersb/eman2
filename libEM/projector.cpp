/*
 * Author: Steven Ludtke, 04/10/2003 (sludtke@bcm.edu)
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

#include "projector.h"
#include "emdata.h"
#include "interp.h"
#include "emutil.h"
#include "plugins/projector_template.h"

#ifdef WIN32
	#define M_PI 3.14159265358979323846f
#endif	//WIN32

#ifdef EMAN2_USING_CUDA
#include "cuda/cuda_util.h"
#include "cuda/cuda_projector.h"
#endif

using namespace std;
using namespace EMAN;

const string FourierGriddingProjector::NAME = "fourier_gridding";
const string PawelProjector::NAME = "pawel";
const string StandardProjector::NAME = "standard";
const string MaxValProjector::NAME = "maxval";
const string ChaoProjector::NAME = "chao";

template <> Factory < Projector >::Factory()
{
	force_add<PawelProjector>();
	force_add<StandardProjector>();
	force_add<MaxValProjector>();
	force_add<FourierGriddingProjector>();
	force_add<ChaoProjector>();
	
//	force_add<XYZProjector>();
}

void PawelProjector::prepcubes(int nx, int ny, int nz, int ri, Vec3i origin,
		                       int& nn, IPCube* ipcube) const {
	const float r = float(ri)*float(ri);
	const int ldpx = origin[0];
	const int ldpy = origin[1];
	const int ldpz = origin[2];
	//cout<<"  ldpx  "<<ldpx<<"  i2  "<<ldpy<<"  i1 "<<ldpz<<endl;
	float t;
	nn = -1;
	for (int i1 = 0; i1 < nz; i1++) {
		t = float(i1 - ldpz);
		const float xx = t*t;
		for (int i2 = 0; i2 < ny; i2++) {
			t = float(i2 - ldpy);
			const float yy = t*t + xx;
			bool first = true;
			for (int i3 = 0; i3 < nx; i3++) {
				t = float(i3 - ldpx);
				const float rc = t*t + yy;
				if (first) {
					// first pixel on this line
					if (rc > r) continue;
					first = false;
					nn++;
					if (ipcube != NULL) {
						ipcube[nn].start = i3;
						ipcube[nn].end   = i3;
						ipcube[nn].loc[0] = i3 - ldpx;
						ipcube[nn].loc[1] = i2 - ldpy;
						ipcube[nn].loc[2] = i1 - ldpz;
						//cout<<"  start  "<<i3<<"  i2  "<<i2<<"  i1 "<<i1<<endl;
					}
				} else {
					// second or later pixel on this line
					if (ipcube != NULL) {
						if (rc <= r) ipcube[nn].end = i3;
					}
				}
			}
		}
	}
}

EMData *PawelProjector::project3d(EMData * image) const
{
	if (!image)  return 0;
	int ri;
	int nx = image->get_xsize();
	int ny = image->get_ysize();
	int nz = image->get_zsize();
	int dim = Util::get_max(nx,ny,nz);
	int dimc = dim/2;
	if (nz == 1) {
		LOGERR("The PawelProjector needs a volume!");
		return 0;
	}

	Vec3i origin(0,0,0);

	if (params.has_key("radius")) {ri = params["radius"];}
	else {ri = dim/2 - 1;}

	Transform* rotation = params["transform"];
	//int nangles = 0;
	//vector<float> anglelist;
	// Do we have a list of angles?
	/*
	if (params.has_key("anglelist")) {
		anglelist = params["anglelist"];
		nangles = anglelist.size() / 3;
	} else {*/

		//if ( rotation == NULL ) throw NullPointerException("The transform object (required for projection), was not specified");
		/*
		Dict p = t3d->get_rotation("spider");

		string angletype = "SPIDER";
		float phi = p["phi"];
		float theta = p["theta"];
		float psi = p["psi"];
		anglelist.push_back(phi);
		anglelist.push_back(theta);
		anglelist.push_back(psi);
		*/
		int nangles = 1;
	//}

	//for (int i = 0 ; i <= nn; i++)  cout<<" IPCUBE "<<ipcube[i].start<<"  "<<ipcube[i].end<<"  "<<ipcube[i].loc[0]<<"  "<<ipcube[i].loc[1]<<"  "<<ipcube[i].loc[2]<<endl;
	// loop over sets of angles
	//for (int ia = 0; ia < nangles; ia++) {
	EMData* ret = new EMData();
	int ia = 0;
		//int indx = 3*ia;
		//Dict d("type","spider","phi",anglelist[indx],"theta",anglelist[indx+1],"psi",anglelist[indx+2]);
		//Transform rotation(d);
		if (2*(ri+1)+1 > dim) {
			// initialize return object
			ret->set_size(dim, dim, nangles);
			ret->to_zero();
			origin[0] = dimc;
			origin[1] = dimc;
			origin[2] = dimc;
			Vec3i loc(-dimc,0,0);
			Vec3i vorg(nx/2,ny/2,nz/2);
			// This code is for arbitrary dimensions, so must check x and y boundaries
			for (int l = 0 ; l < dim; l++) {  // Z
				loc[2] = l - dimc;
				for (int k = 0 ; k < dim; k++) {  // Y
					loc[1] = k - dimc;
					Vec3f vb = loc*(*rotation) + vorg;
					for (int j = 0; j < dim; j++) {  //X
						// check for pixels out-of-bounds
						//cout<<j<<"  j  "<<k<<"  k  "<<"  iox  "<<vb[0]<<"  ioy  "<<vb[1]<<"  ioz "<<vb[2]<<endl;
						int iox = int(vb[0]);
						if ((iox >= 0) && (iox < nx-1)) {
							int ioy = int(vb[1]);
							if ((ioy >= 0) && (ioy < ny-1)) {
								int ioz = int(vb[2]);
								if ((ioz >= 0) && (ioz < nz-1)) {
									// real work for pixels in bounds
								//cout<<j<<"  j  "<<k<<"  k  "<<"  iox  "<<iox<<"  ioy  "<<ioy<<"  ioz "<<ioz<<endl;
								//cout<<"  TAKE"<<endl;
									float dx = vb[0] - iox;
									float dy = vb[1] - ioy;
									float dz = vb[2] - ioz;
									float a1 = (*image)(iox,ioy,ioz);
									float a2 = (*image)(iox+1,ioy,ioz) - a1;
									float a3 = (*image)(iox,ioy+1,ioz) - a1;
									float a4 = (*image)(iox,ioy,ioz+1) - a1;
									float a5 = -a2 -(*image)(iox,ioy+1,ioz)
												+ (*image)(iox+1,ioy+1,ioz);
									float a61 = -(*image)(iox,ioy,ioz+1)
												+ (*image)(iox+1,ioy,ioz+1);
									float a6 = -a2 + a61;
									float a7 = -a3 - (*image)(iox,ioy,ioz+1)
												+ (*image)(iox,ioy+1,ioz+1);
									float a8 = -a5 - a61 - (*image)(iox,ioy+1,ioz+1)
												+ (*image)(iox+1,ioy+1,ioz+1);
									(*ret)(j,k,ia) += a1 + dz*(a4 + a6*dx
												+ (a7 + a8*dx)*dy)
												+ a3*dy + dx*(a2 + a5*dy);
								} //else {cout<<"  iox  "<<iox<<"  ioy  "<<int(vb[1])<<"  ioz "<<int(vb[2])<<"  VIOLAATED Z "<<endl; }
							}//else {cout<<"  iox  "<<iox<<"  ioy  "<<int(vb[1])<<"  ioz "<<int(vb[2])<<"  VIOLATED Y "<<endl; }
						}//else {cout<<"  iox  "<<iox<<"  ioy  "<<int(vb[1])<<"  ioz "<<int(vb[2])<<"  VIOLATED X "<<endl; }
						vb += rotation->get_matrix3_row(0);
					}
				}
			}

		} else {
			// If a sensible origin isn't passed in, choose the middle of
			// the cube.
			if (params.has_key("origin_x")) {origin[0] = params["origin_x"];}
			else {origin[0] = nx/2;}
			if (params.has_key("origin_y")) {origin[1] = params["origin_y"];}
			else {origin[1] = ny/2;}
			if (params.has_key("origin_z")) {origin[2] = params["origin_z"];}
			else {origin[2] = nz/2;}
			// Determine the number of rows (x-lines) within the radius
			int nn = -1;
			prepcubes(nx, ny, nz, ri, origin, nn);
			// nn is now the number of rows-1 within the radius
			// so we can create and fill the ipcubes
			IPCube* ipcube = new IPCube[nn+1];
			prepcubes(nx, ny, nz, ri, origin, nn, ipcube);
			// initialize return object
			ret->set_size(nx, ny, nangles);
			ret->to_zero();
			// No need to check x and y boundaries
			for (int i = 0 ; i <= nn; i++) {
				int k = ipcube[i].loc[1] + origin[1];
				Vec3f vb = ipcube[i].loc*(*rotation) + origin;
				for (int j = ipcube[i].start; j <= ipcube[i].end; j++) {
					int iox = int(vb[0]);
					int ioy = int(vb[1]);
					int ioz = int(vb[2]);
					float dx = vb[0] - iox;
					float dy = vb[1] - ioy;
					float dz = vb[2] - ioz;
					float a1 = (*image)(iox,ioy,ioz);
					float a2 = (*image)(iox+1,ioy,ioz) - a1;
					float a3 = (*image)(iox,ioy+1,ioz) - a1;
					float a4 = (*image)(iox,ioy,ioz+1) - a1;
					float a5 = -a2 -(*image)(iox,ioy+1,ioz)
								+ (*image)(iox+1,ioy+1,ioz);
					float a61 = -(*image)(iox,ioy,ioz+1)
								+ (*image)(iox+1,ioy,ioz+1);
					float a6 = -a2 + a61;
					float a7 = -a3 - (*image)(iox,ioy,ioz+1)
								+ (*image)(iox,ioy+1,ioz+1);
					float a8 = -a5 - a61 - (*image)(iox,ioy+1,ioz+1)
								+ (*image)(iox+1,ioy+1,ioz+1);
					(*ret)(j,k,ia) += a1 + dz*(a4 + a6*dx
								+ (a7 + a8*dx)*dy)
								+ a3*dy + dx*(a2 + a5*dy);
					vb += rotation->get_matrix3_row(0);
				}
			}
			EMDeleteArray(ipcube);
		}
	//}
	ret->update();
	if(rotation) {delete rotation; rotation=0;}
	return ret;
}

EMData *StandardProjector::project3d(EMData * image) const
{
	Transform* t3d = params["transform"];
	if ( t3d == NULL ) throw NullPointerException("The transform object containing the angles(required for projection), was not specified");
// 	Dict p = t3d->get_rotation();
	if ( image->get_ndim() == 3 )
	{

#ifdef EMAN2_USING_CUDA
		if(EMData::usecuda == 1) {
			if(!image->isrodataongpu()) image->copy_to_cudaro();
			//cout << "CUDA PROJ" << endl;
			Transform* t3d = params["transform"];
			if ( t3d == NULL ) throw NullPointerException("The transform object containing the angles(required for projection), was not specified");
			float * m = new float[12];
			t3d->copy_matrix_into_array(m);
			image->bindcudaarrayA(true);
			//EMData* e = new EMData(0,0,image->get_xsize(),image->get_ysize(),1);
			EMData *e = new EMData();
			e->set_size_cuda(image->get_xsize(), image->get_ysize(), 1);
			e->rw_alloc();
			standard_project(m,e->getcudarwdata(), e->get_xsize(), e->get_ysize());
			image->unbindcudaarryA();
			delete [] m;
		
			e->update();
			e->set_attr("xform.projection",t3d);
			e->set_attr("apix_x",(float)image->get_attr("apix_x"));
			e->set_attr("apix_y",(float)image->get_attr("apix_y"));
			e->set_attr("apix_z",(float)image->get_attr("apix_z"));
			//e_>copy_from_device();
			if(t3d) {delete t3d; t3d=0;}
			return e;
		}
#endif
		int nx = image->get_xsize();
		int ny = image->get_ysize();
		int nz = image->get_zsize();

// 		Transform3D r(Transform3D::EMAN, az, alt, phi);
		Transform r = t3d->inverse(); // The inverse is taken here because we are rotating the coordinate system, not the image
		int xy = nx * ny;

		EMData *proj = new EMData();
		proj->set_size(nx, ny, 1);

		Vec3i offset(nx/2,ny/2,nz/2);

		float *sdata = image->get_data();
		float *ddata = proj->get_data();
		for (int k = -nz / 2; k < nz - nz / 2; k++) {
			int l = 0;
			for (int j = -ny / 2; j < ny - ny / 2; j++) {
				ddata[l]=0;
				for (int i = -nx / 2; i < nx - nx / 2; i++,l++) {

					Vec3f coord(i,j,k);
					Vec3f soln = r*coord;
					soln += offset;

					/**A "fix" for the segmentation fault when calling initmodel.py with
					 * standard projector. We'll look into this and make a real fix.
					 * -- Grant Tang*/
//					printf(" ");

					float x2 = soln[0];
					float y2 = soln[1];
					float z2 = soln[2];

					float x = (float)Util::fast_floor(x2);
					float y = (float)Util::fast_floor(y2);
					float z = (float)Util::fast_floor(z2);

					float t = x2 - x;
					float u = y2 - y;
					float v = z2 - z;

					size_t ii = (size_t) ((size_t)x + (size_t)y * nx + (size_t)z * xy);
// 
					if (x2 < 0 || y2 < 0 || z2 < 0 ) continue;
					if 	(x2 > (nx-1) || y2  > (ny-1) || z2 > (nz-1) ) continue;

					if (x2 < (nx - 1) && y2 < (ny - 1) && z2 < (nz - 1)) {
						ddata[l] +=
								Util::trilinear_interpolate(sdata[ii], sdata[ii + 1], sdata[ii + nx],
								sdata[ii + nx + 1], sdata[ii + xy],	sdata[ii + xy + 1], sdata[ii + xy + nx],
								sdata[ii + xy + nx + 1], t, u, v);
					}
					else if ( x2 == (nx - 1) && y2 == (ny - 1) && z2 == (nz - 1) ) {
						ddata[l] += sdata[ii];
					}
					else if ( x2 == (nx - 1) && y2 == (ny - 1) ) {
						ddata[l] +=	Util::linear_interpolate(sdata[ii], sdata[ii + xy],v);
					}
					else if ( x2 == (nx - 1) && z2 == (nz - 1) ) {
						ddata[l] += Util::linear_interpolate(sdata[ii], sdata[ii + nx],u);
					}
					else if ( y2 == (ny - 1) && z2 == (nz - 1) ) {
						ddata[l] += Util::linear_interpolate(sdata[ii], sdata[ii + 1],t);
					}
					else if ( x2 == (nx - 1) ) {
						ddata[l] += Util::bilinear_interpolate(sdata[ii], sdata[ii + nx], sdata[ii + xy], sdata[ii + xy + nx],u,v);
					}
					else if ( y2 == (ny - 1) ) {
						ddata[l] += Util::bilinear_interpolate(sdata[ii], sdata[ii + 1], sdata[ii + xy], sdata[ii + xy + 1],t,v);
					}
					else if ( z2 == (nz - 1) ) {
						ddata[l] += Util::bilinear_interpolate(sdata[ii], sdata[ii + 1], sdata[ii + nx], sdata[ii + nx + 1],t,u);
					}
				}
			}
		}
		proj->update();
		proj->set_attr("xform.projection",t3d);
		proj->set_attr("apix_x",(float)image->get_attr("apix_x"));
		proj->set_attr("apix_y",(float)image->get_attr("apix_y"));
		proj->set_attr("apix_z",(float)image->get_attr("apix_z"));
		
		if(t3d) {delete t3d; t3d=0;}
		return proj;
	}
	else if ( image->get_ndim() == 2 ) {

		Transform r = t3d->inverse(); // The inverse is taken here because we are rotating the coordinate system, not the image

		int nx = image->get_xsize();
		int ny = image->get_ysize();

		EMData *proj = new EMData();
		proj->set_size(nx, 1, 1);
		proj->to_zero();

		float *sdata = image->get_data();
		float *ddata = proj->get_data();

		Vec2f offset(nx/2,ny/2);
		for (int j = -ny / 2; j < ny - ny / 2; j++) { // j represents a column of pixels in the direction of the angle
			int l = 0;
			for (int i = -nx / 2; i < nx - nx / 2; i++,l++) {

				Vec2f coord(i,j);
				Vec2f soln = r*coord;
				soln += offset;

				float x2 = soln[0];
				float y2 = soln[1];

				float x = (float)Util::fast_floor(x2);
				float y = (float)Util::fast_floor(y2);

				int ii = (int) (x + y * nx);
				float u = x2 - x;
				float v = y2 - y;

				if (x2 < 0 || y2 < 0 ) continue;
				if 	(x2 > (nx-1) || y2  > (ny-1) ) continue;

				if (  x2 < (nx - 1) && y2 < (ny - 1) ) {
					ddata[l] += Util::bilinear_interpolate(sdata[ii], sdata[ii + 1], sdata[ii + nx],sdata[ii + nx + 1], u, v);
				}
				else if (x2 == (nx-1) && y2 == (ny-1) ) {
					ddata[l] += sdata[ii];
				}
				else if (x2 == (nx-1) ) {
					ddata[l] += Util::linear_interpolate(sdata[ii],sdata[ii + nx], v);
				}
				else if (y2 == (ny-1) ) {
					ddata[l] += Util::linear_interpolate(sdata[ii],sdata[ii + 1], u);
				}
			}
		}
		proj->set_attr("xform.projection",t3d);
		proj->update();
		if(t3d) {delete t3d; t3d=0;}
		return proj;
	}
	else throw ImageDimensionException("Standard projection works only for 2D and 3D images");
}

EMData *MaxValProjector::project3d(EMData * image) const
{
	Transform* t3d = params["transform"];
	if ( t3d == NULL ) throw NullPointerException("The transform object containing the angles(required for projection), was not specified");
// 	Dict p = t3d->get_rotation();
	if ( image->get_ndim() == 3 )
	{

		int nx = image->get_xsize();
		int ny = image->get_ysize();
		int nz = image->get_zsize();

// 		Transform3D r(Transform3D::EMAN, az, alt, phi);
		Transform r = t3d->inverse(); // The inverse is taken here because we are rotating the coordinate system, not the image
		int xy = nx * ny;

		EMData *proj = new EMData();
		proj->set_size(nx, ny, 1);

		Vec3i offset(nx/2,ny/2,nz/2);

		float *sdata = image->get_data();
		float *ddata = proj->get_data();
		for (int k = -nz / 2; k < nz - nz / 2; k++) {
			int l = 0;
			for (int j = -ny / 2; j < ny - ny / 2; j++) {
				ddata[l]=0;
				for (int i = -nx / 2; i < nx - nx / 2; i++,l++) {

					Vec3f coord(i,j,k);
					Vec3f soln = r*coord;
					soln += offset;

					/**A "fix" for the segmentation fault when calling initmodel.py with
					 * standard projector. We'll look into this and make a real fix.
					 * -- Grant Tang*/
//					printf(" ");

					float x2 = soln[0];
					float y2 = soln[1];
					float z2 = soln[2];

					float x = (float)Util::fast_floor(x2);
					float y = (float)Util::fast_floor(y2);
					float z = (float)Util::fast_floor(z2);

					float t = x2 - x;
					float u = y2 - y;
					float v = z2 - z;

					size_t ii = (size_t) ((size_t)x + (size_t)y * nx + (size_t)z * xy);
// 
					if (x2 < 0 || y2 < 0 || z2 < 0 ) continue;
					if 	(x2 > (nx-1) || y2  > (ny-1) || z2 > (nz-1) ) continue;

					if (x2 < (nx - 1) && y2 < (ny - 1) && z2 < (nz - 1)) {
						ddata[l] = Util::get_max(ddata[l],
								Util::trilinear_interpolate(sdata[ii], sdata[ii + 1], sdata[ii + nx],
								sdata[ii + nx + 1], sdata[ii + xy],	sdata[ii + xy + 1], sdata[ii + xy + nx],
								sdata[ii + xy + nx + 1], t, u, v));
					}
					else if ( x2 == (nx - 1) && y2 == (ny - 1) && z2 == (nz - 1) ) {
						ddata[l] = Util::get_max(ddata[l],sdata[ii]);
					}
					else if ( x2 == (nx - 1) && y2 == (ny - 1) ) {
						ddata[l] =	Util::get_max(ddata[l],Util::linear_interpolate(sdata[ii], sdata[ii + xy],v));
					}
					else if ( x2 == (nx - 1) && z2 == (nz - 1) ) {
						ddata[l] =	Util::get_max(ddata[l],Util::linear_interpolate(sdata[ii], sdata[ii + nx],u));
					}
					else if ( y2 == (ny - 1) && z2 == (nz - 1) ) {
						ddata[l] =	Util::get_max(ddata[l],Util::linear_interpolate(sdata[ii], sdata[ii + 1],t));
					}
					else if ( x2 == (nx - 1) ) {
						ddata[l] =	Util::get_max(ddata[l],Util::bilinear_interpolate(sdata[ii], sdata[ii + nx], sdata[ii + xy], sdata[ii + xy + nx],u,v));
					}
					else if ( y2 == (ny - 1) ) {
						ddata[l] =	Util::get_max(ddata[l],Util::bilinear_interpolate(sdata[ii], sdata[ii + 1], sdata[ii + xy], sdata[ii + xy + 1],t,v));
					}
					else if ( z2 == (nz - 1) ) {
						ddata[l] =	Util::get_max(ddata[l],Util::bilinear_interpolate(sdata[ii], sdata[ii + 1], sdata[ii + nx], sdata[ii + nx + 1],t,u));
					}
				}
			}
		}
		proj->update();
		proj->set_attr("xform.projection",t3d);
		proj->set_attr("apix_x",(float)image->get_attr("apix_x"));
		proj->set_attr("apix_y",(float)image->get_attr("apix_y"));
		proj->set_attr("apix_z",(float)image->get_attr("apix_z"));
		
		if(t3d) {delete t3d; t3d=0;}
		return proj;
	}
	else if ( image->get_ndim() == 2 ) {

		Transform r = t3d->inverse(); // The inverse is taken here because we are rotating the coordinate system, not the image

		int nx = image->get_xsize();
		int ny = image->get_ysize();

		EMData *proj = new EMData();
		proj->set_size(nx, 1, 1);
		proj->to_zero();

		float *sdata = image->get_data();
		float *ddata = proj->get_data();

		Vec2f offset(nx/2,ny/2);
		for (int j = -ny / 2; j < ny - ny / 2; j++) { // j represents a column of pixels in the direction of the angle
			int l = 0;
			for (int i = -nx / 2; i < nx - nx / 2; i++,l++) {

				Vec2f coord(i,j);
				Vec2f soln = r*coord;
				soln += offset;

				float x2 = soln[0];
				float y2 = soln[1];

				float x = (float)Util::fast_floor(x2);
				float y = (float)Util::fast_floor(y2);

				int ii = (int) (x + y * nx);
				float u = x2 - x;
				float v = y2 - y;

				if (x2 < 0 || y2 < 0 ) continue;
				if 	(x2 > (nx-1) || y2  > (ny-1) ) continue;

				if (  x2 < (nx - 1) && y2 < (ny - 1) ) {
					ddata[l] =	Util::get_max(ddata[l],Util::bilinear_interpolate(sdata[ii], sdata[ii + 1], sdata[ii + nx],sdata[ii + nx + 1], u, v));
				}
				else if (x2 == (nx-1) && y2 == (ny-1) ) {
					ddata[l] =	Util::get_max(ddata[l],sdata[ii]);
				}
				else if (x2 == (nx-1) ) {
					ddata[l] =	Util::get_max(ddata[l],Util::linear_interpolate(sdata[ii],sdata[ii + nx], v));
				}
				else if (y2 == (ny-1) ) {
					ddata[l] =	Util::get_max(ddata[l],Util::linear_interpolate(sdata[ii],sdata[ii + 1], u));
				}
			}
		}
		proj->set_attr("xform.projection",t3d);
		proj->update();
		if(t3d) {delete t3d; t3d=0;}
		return proj;
	}
	else throw ImageDimensionException("Standard projection works only for 2D and 3D images");
}


// EMData *FourierGriddingProjector::project3d(EMData * image) const
// {
// 	if (!image) {
// 		return 0;
// 	}
// 	if (3 != image->get_ndim())
// 		throw ImageDimensionException(
// 				"FourierGriddingProjector needs a 3-D volume");
// 	if (image->is_complex())
// 		throw ImageFormatException(
// 				"FourierGriddingProjector requires a real volume");
// 	const int npad = params.has_key("npad") ? int(params["npad"]) : 2;
// 	const int nx = image->get_xsize();
// 	const int ny = image->get_ysize();
// 	const int nz = image->get_zsize();
// 	if (nx != ny || nx != nz)
// 		throw ImageDimensionException(
// 				"FourierGriddingProjector requires nx==ny==nz");
// 	const int m = Util::get_min(nx,ny,nz);
// 	const int n = m*npad;
//
// 	int K = params["kb_K"];
// 	if ( K == 0 ) K = 6;
// 	float alpha = params["kb_alpha"];
// 	if ( alpha == 0 ) alpha = 1.25;
// 	Util::KaiserBessel kb(alpha, K, (float)(m/2), K/(2.0f*n), n);
//
// 	// divide out gridding weights
// 	EMData* tmpImage = image->copy();
// 	tmpImage->divkbsinh(kb);
// 	// pad and center volume, then FFT and multiply by (-1)**(i+j+k)
// 	//EMData* imgft = tmpImage->pad_fft(npad);
// 	//imgft->center_padded();
// 	EMData* imgft = tmpImage->norm_pad(false, npad);
// 	imgft->do_fft_inplace();
// 	imgft->center_origin_fft();
// 	imgft->fft_shuffle();
// 	delete tmpImage;
//
// 	// Do we have a list of angles?
// 	int nangles = 0;
// 	vector<float> anglelist;
// 	// Do we have a list of angles?
// 	if (params.has_key("anglelist")) {
// 		anglelist = params["anglelist"];
// 		nangles = anglelist.size() / 3;
// 	} else {
// 		// This part was modified by David Woolford -
// 		// Before this the code worked only for SPIDER and EMAN angles,
// 		// but the framework of the Transform3D allows for a generic implementation
// 		// as specified here.
// 		Transform3D* t3d = params["t3d"];
// 		if ( t3d == NULL ) throw NullPointerException("The transform3d object (required for projection), was not specified");
// 		Dict p = t3d->get_rotation(Transform3D::SPIDER);
//
// 		string angletype = "SPIDER";
// 		float phi = p["phi"];
// 		float theta = p["theta"];
// 		float psi = p["psi"];
// 		anglelist.push_back(phi);
// 		anglelist.push_back(theta);
// 		anglelist.push_back(psi);
// 		nangles = 1;
// 	}
//
// 	// End David Woolford modifications
//
// 	// initialize return object
// 	EMData* ret = new EMData();
// 	ret->set_size(nx, ny, nangles);
// 	ret->to_zero();
// 	// loop over sets of angles
// 	for (int ia = 0; ia < nangles; ia++) {
// 		int indx = 3*ia;
// 		Transform3D tf(Transform3D::SPIDER, anglelist[indx],anglelist[indx+1],anglelist[indx+2]);
// 		EMData* proj = imgft->extractplane(tf, kb);
// 		if (proj->is_shuffled()) proj->fft_shuffle();
// 		proj->center_origin_fft();
// 		proj->do_ift_inplace();
// 		EMData* winproj = proj->window_center(m);
// 		delete proj;
// 		for (int iy=0; iy < ny; iy++)
// 			for (int ix=0; ix < nx; ix++)
// 				(*ret)(ix,iy,ia) = (*winproj)(ix,iy);
// 		delete winproj;
// 	}
// 	delete imgft;
// 	ret->update();
//
// 	return ret;
// }


EMData *FourierGriddingProjector::project3d(EMData * image) const
{
	if (!image) {
		return 0;
	}
	if (3 != image->get_ndim())
		throw ImageDimensionException(
									  "FourierGriddingProjector needs a 3-D volume");
	if (image->is_complex())
		throw ImageFormatException(
								   "FourierGriddingProjector requires a real volume");
	const int npad = params.has_key("npad") ? int(params["npad"]) : 2;
	const int nx = image->get_xsize();
	const int ny = image->get_ysize();
	const int nz = image->get_zsize();
	if (nx != ny || nx != nz)
		throw ImageDimensionException(
									  "FourierGriddingProjector requires nx==ny==nz");
	const int m = Util::get_min(nx,ny,nz);
	const int n = m*npad;

	int K = params["kb_K"];
	if ( K == 0 ) K = 6;
	float alpha = params["kb_alpha"];
	if ( alpha == 0 ) alpha = 1.25;
	Util::KaiserBessel kb(alpha, K, (float)(m/2), K/(2.0f*n), n);

	// divide out gridding weights
	EMData* tmpImage = image->copy();
	tmpImage->divkbsinh(kb);
	// pad and center volume, then FFT and multiply by (-1)**(i+j+k)
	//EMData* imgft = tmpImage->pad_fft(npad);
	//imgft->center_padded();
	EMData* imgft = tmpImage->norm_pad(false, npad);
	imgft->do_fft_inplace();
	imgft->center_origin_fft();
	imgft->fft_shuffle();
	delete tmpImage;

	// Do we have a list of angles?
	int nangles = 0;
	vector<float> anglelist;
	// Do we have a list of angles?
	if (params.has_key("anglelist")) {
		anglelist = params["anglelist"];
		nangles = anglelist.size() / 3;
	} else {
		// This part was modified by David Woolford -
		// Before this the code worked only for SPIDER and EMAN angles,
		// but the framework of the Transform3D allows for a generic implementation
		// as specified here.
		Transform* t3d = params["transform"];
		if ( t3d == NULL ) throw NullPointerException("The transform object (required for projection), was not specified");
		Dict p = t3d->get_rotation("spider");

		string angletype = "SPIDER";
		float phi = p["phi"];
		float theta = p["theta"];
		float psi = p["psi"];
		anglelist.push_back(phi);
		anglelist.push_back(theta);
		anglelist.push_back(psi);
		nangles = 1;
		if(t3d) {delete t3d; t3d=0;}
	}

	// End David Woolford modifications

	// initialize return object
	EMData* ret = new EMData();
	ret->set_size(nx, ny, nangles);
	ret->to_zero();
	// loop over sets of angles
	for (int ia = 0; ia < nangles; ia++) {
		int indx = 3*ia;
		Dict d("type","spider","phi",anglelist[indx],"theta",anglelist[indx+1],"psi",anglelist[indx+2]);
		Transform tf(d);
		EMData* proj = imgft->extract_plane(tf, kb);
		if (proj->is_shuffled()) proj->fft_shuffle();
		proj->center_origin_fft();
		proj->do_ift_inplace();
		EMData* winproj = proj->window_center(m);
		delete proj;
		for (int iy=0; iy < ny; iy++)
			for (int ix=0; ix < nx; ix++)
				(*ret)(ix,iy,ia) = (*winproj)(ix,iy);
		delete winproj;
	}
	delete imgft;

	if (!params.has_key("anglelist")) {
		Transform* t3d = params["transform"];
		ret->set_attr("xform.projection",t3d);
		if(t3d) {delete t3d; t3d=0;}
	}
	ret->update();
	return ret;
}

// BEGIN Chao projectors and backprojector addition (04/25/06)
int ChaoProjector::getnnz(Vec3i volsize, int ri, Vec3i origin, int *nrays, int *nnz) const
/*
   purpose: count the number of voxels within a sphere centered
            at origin and with a radius ri.

     input:
     volsize contains the size information (nx,ny,nz) about the volume
     ri      radius of the object embedded in the cube.
     origin  coordinates for the center of the volume

     output:
     nnz    total number of voxels within the sphere (of radius ri)
     nrays  number of rays in z-direction.
*/
{
	int  ix, iy, iz, rs, r2, xs, ys, zs, xx, yy, zz;
	int  ftm=0, status = 0;

	r2    = ri*ri;
	*nnz  = 0;
	*nrays = 0;
	int nx = (int)volsize[0];
	int ny = (int)volsize[1];
	int nz = (int)volsize[2];

	int xcent = (int)origin[0];
	int ycent = (int)origin[1];
	int zcent = (int)origin[2];

	// need to add some error checking
	for (ix = 1; ix <=nx; ix++) {
	    xs  = ix-xcent;
	    xx  = xs*xs;
	    for (iy = 1; iy <= ny; iy++) {
		ys = iy-ycent;
		yy = ys*ys;
		ftm = 1;
		for (iz = 1; iz <= nz; iz++) {
	    	    zs = iz-zcent;
	    	    zz = zs*zs;
	    	    rs = xx + yy + zz;
	    	    if (rs <= r2) {
	    		(*nnz)++;
	    		if (ftm) {
			   (*nrays)++;
			   ftm = 0;
			}
		    }
		}
	    } // end for iy
	} // end for ix
	return status;
}

#define cube(i,j,k) cube[ ((k-1)*ny + j-1)*nx + i-1 ]
#define sphere(i)   sphere[(i)-1]
#define cord(i,j)   cord[((j)-1)*3 + (i) -1]
#define ptrs(i)     ptrs[(i)-1]
#define dm(i)       dm[(i)-1]

int ChaoProjector:: cb2sph(float *cube, Vec3i volsize, int    ri, Vec3i origin,
                           int    nnz0, int     *ptrs, int *cord, float *sphere) const
{
    int    xs, ys, zs, xx, yy, zz, rs, r2;
    int    ix, iy, iz, jnz, nnz, nrays;
    int    ftm = 0, status = 0;

    int xcent = (int)origin[0];
    int ycent = (int)origin[1];
    int zcent = (int)origin[2];

    int nx = (int)volsize[0];
    int ny = (int)volsize[1];
    int nz = (int)volsize[2];

    r2      = ri*ri;
    nnz     = 0;
    nrays    = 0;
    ptrs(1) = 1;

    for (ix = 1; ix <= nx; ix++) {
       xs  = ix-xcent;
       xx  = xs*xs;
       for ( iy = 1; iy <= ny; iy++ ) {
           ys = iy-ycent;
           yy = ys*ys;
           jnz = 0;

           ftm = 1;
           // not the most efficient implementation
           for (iz = 1; iz <= nz; iz++) {
               zs = iz-zcent;
               zz = zs*zs;
               rs = xx + yy + zz;
               if (rs <= r2) {
                  jnz++;
                  nnz++;
                  sphere(nnz) = cube(iz, iy, ix);

                  //  record the coordinates of the first nonzero ===
                  if (ftm) {
  		     nrays++;
                     cord(1,nrays) = iz;
                     cord(2,nrays) = iy;
                     cord(3,nrays) = ix;
                     ftm = 0;
                  }
               }
            } // end for (iz..)
            if (jnz > 0) {
		ptrs(nrays+1) = ptrs(nrays) + jnz;
	    }  // endif (jnz)
       } // end for iy
    } // end for ix
    if (nnz != nnz0) status = -1;
    return status;
}

// decompress sphere into a cube
int ChaoProjector::sph2cb(float *sphere, Vec3i volsize, int  nrays, int    ri,
                          int      nnz0, int     *ptrs, int  *cord, float *cube) const
{
    int       status=0;
    int       r2, i, j, ix, iy, iz,  nnz;

    int nx = (int)volsize[0];
    int ny = (int)volsize[1];
    // int nz = (int)volsize[2];

    r2      = ri*ri;
    nnz     = 0;
    ptrs(1) = 1;

    // no need to initialize
    // for (i = 0; i<nx*ny*nz; i++) cube[i]=0.0;

    nnz = 0;
    for (j = 1; j <= nrays; j++) {
       iz = cord(1,j);
       iy = cord(2,j);
       ix = cord(3,j);
       for (i = ptrs(j); i<=ptrs(j+1)-1; i++, iz++) {
           nnz++;
	   cube(iz,iy,ix) = sphere(nnz);
       }
    }
    if (nnz != nnz0) status = -1;
    return status;
}

#define x(i)        x[(i)-1]
#define y(i,j)      y[(j-1)*nx + i - 1]

// project from 3D to 2D (single image)
int ChaoProjector::fwdpj3(Vec3i volsize, int nrays, int      , float *dm,
                          Vec3i  origin, int    ri, int *ptrs, int *cord,
                          float      *x, float  *y) const
{
    /*
        purpose:  y <--- proj(x)
        input  :  volsize  the size (nx,ny,nz) of the volume
                  nrays    number of rays within the compact spherical
                           representation
                  nnz      number of voxels within the sphere
                  dm       an array of size 9 storing transformation
                           associated with the projection direction
                  origin   coordinates of the center of the volume
                  ri       radius of the sphere
                  ptrs     the beginning address of each ray
                  cord     the coordinates of the first point in each ray
                  x        3d input volume
                  y        2d output image
    */

    int    iqx, iqy, i, j, xc, yc, zc;
    float  ct, dipx, dipy, dipx1m, dipy1m, xb, yb, dm1, dm4;
    int    status = 0;

    int xcent = origin[0];
    int ycent = origin[1];
    int zcent = origin[2];

    int nx = volsize[0];

    dm1 = dm(1);
    dm4 = dm(4);

    if ( nx > 2*ri ) {
	for (i = 1; i <= nrays; i++) {
            zc = cord(1,i)-zcent;
            yc = cord(2,i)-ycent;
            xc = cord(3,i)-xcent;

            xb = zc*dm(1)+yc*dm(2)+xc*dm(3) + xcent;
            yb = zc*dm(4)+yc*dm(5)+xc*dm(6) + ycent;

            for (j = ptrs(i); j< ptrs(i+1); j++) {
               iqx = ifix(xb);
               iqy = ifix(yb);

  	       ct   = x(j);
               dipx =  xb - (float)(iqx);
               dipy = (yb - (float)(iqy)) * ct;

               dipy1m = ct - dipy;
               dipx1m = 1.0f - dipx;

               y(iqx  ,iqy)   = y(iqx  ,iqy)   + dipx1m*dipy1m;
               y(iqx+1,iqy)   = y(iqx+1,iqy)   + dipx*dipy1m;
               y(iqx+1,iqy+1) = y(iqx+1,iqy+1) + dipx*dipy;
               y(iqx  ,iqy+1) = y(iqx  ,iqy+1) + dipx1m*dipy;

               xb += dm1;
               yb += dm4;
	   }
	}
    }
    else {
	fprintf(stderr, " nx must be greater than 2*ri\n");
        exit(1);
    }
    return status;
}
#undef x
#undef y

#define y(i)        y[(i)-1]
#define x(i,j)      x[((j)-1)*nx + (i) - 1]

// backproject from 2D to 3D for a single image
int ChaoProjector::bckpj3(Vec3i volsize, int nrays, int      , float *dm,
                          Vec3i  origin, int    ri, int *ptrs, int *cord,
                          float      *x, float *y) const
{
    int       i, j, iqx,iqy, xc, yc, zc;
    float     xb, yb, dx, dy, dx1m, dy1m, dxdy;
    int       status = 0;

    int xcent = origin[0];
    int ycent = origin[1];
    int zcent = origin[2];

    int nx = volsize[0];

    if ( nx > 2*ri) {
	for (i = 1; i <= nrays; i++) {
	    zc = cord(1,i) - zcent;
	    yc = cord(2,i) - ycent;
            xc = cord(3,i) - xcent;

            xb = zc*dm(1)+yc*dm(2)+xc*dm(3) + xcent;
            yb = zc*dm(4)+yc*dm(5)+xc*dm(6) + ycent;

            for (j = ptrs(i); j <ptrs(i+1); j++) {
		iqx = ifix((float)(xb));
		iqy = ifix((float)(yb));

		dx = xb - (float)(iqx);
		dy = yb - (float)(iqy);
		dx1m = 1.0f - dx;
		dy1m = 1.0f - dy;
		dxdy = dx*dy;
/*
c               y(j) = y(j) + dx1m*dy1m*x(iqx  , iqy)
c     &                     + dx1m*dy  *x(iqx  , iqy+1)
c     &                     + dx  *dy1m*x(iqx+1, iqy)
c     &                     + dx  *dy  *x(iqx+1, iqy+1)
c
c              --- faster version of the above commented out
c                  code (derived by summing the following table
c                  of coefficients along  the colunms) ---
c
c                        1         dx        dy      dxdy
c                     ------   --------  --------  -------
c                      x(i,j)   -x(i,j)   -x(i,j)    x(i,j)
c                                        x(i,j+1) -x(i,j+1)
c                              x(i+1,j)           -x(i+1,j)
c                                                x(i+1,j+1)
c
*/
               y(j) += x(iqx,iqy)
                    +  dx*(-x(iqx,iqy)+x(iqx+1,iqy))
                    +  dy*(-x(iqx,iqy)+x(iqx,iqy+1))
                    +  dxdy*( x(iqx,iqy) - x(iqx,iqy+1)
                             -x(iqx+1,iqy) + x(iqx+1,iqy+1) );

               xb += dm(1);
               yb += dm(4);
	    } // end for j
	} // end for i
     }
    else {
	fprintf(stderr, "bckpj3: nx must be greater than 2*ri\n");
    }

    return status;
}

#undef x
#undef y
#undef dm

// funny F90 style strange rounding function
int ChaoProjector::ifix(float a) const
{
    int ia;

    if (a>=0) {
       ia = (int)floor(a);
    }
    else {
       ia = (int)ceil(a);
    }
    return ia;
}

#define dm(i,j)          dm[((j)-1)*9 + (i) -1]
#define anglelist(i,j)   anglelist[((j)-1)*3 + (i) - 1]

// SPIDER stype transformation
void ChaoProjector::setdm(vector<float> anglelist, string const , float *dm) const
{ // convert Euler angles to transformations, dm is an 9 by nangles array

	float  psi, theta, phi;
	double cthe, sthe, cpsi, spsi, cphi, sphi;
	int    j;

	int nangles = anglelist.size() / 3;

	// now convert all angles
	for (j = 1; j <= nangles; j++) {
		phi   = static_cast<float>(anglelist(1,j)*dgr_to_rad);
		theta = static_cast<float>(anglelist(2,j)*dgr_to_rad);
		psi   = static_cast<float>(anglelist(3,j)*dgr_to_rad);

		//		cout << phi << " " << theta << " " << psi << endl;
		cthe  = cos(theta);
		sthe  = sin(theta);
		cpsi  = cos(psi);
		spsi  = sin(psi);
		cphi  = cos(phi);
		sphi  = sin(phi);

		dm(1,j)=static_cast<float>(cphi*cthe*cpsi-sphi*spsi);
		dm(2,j)=static_cast<float>(sphi*cthe*cpsi+cphi*spsi);
		dm(3,j)=static_cast<float>(-sthe*cpsi);
		dm(4,j)=static_cast<float>(-cphi*cthe*spsi-sphi*cpsi);
		dm(5,j)=static_cast<float>(-sphi*cthe*spsi+cphi*cpsi);
		dm(6,j)=static_cast<float>(sthe*spsi);
		dm(7,j)=static_cast<float>(sthe*cphi);
		dm(8,j)=static_cast<float>(sthe*sphi);
		dm(9,j)=static_cast<float>(cthe);
	}
}
#undef anglelist

#define images(i,j,k) images[ ((k-1)*nyvol + j-1)*nxvol + i-1 ]

EMData *ChaoProjector::project3d(EMData * vol) const
{

	int nrays, nnz, status, j;
	float *dm;
	int   *ptrs, *cord;
	float *sphere, *images;

	int nxvol = vol->get_xsize();
	int nyvol = vol->get_ysize();
	int nzvol = vol->get_zsize();
	Vec3i volsize(nxvol,nyvol,nzvol);

	int dim = Util::get_min(nxvol,nyvol,nzvol);
	if (nzvol == 1) {
		LOGERR("The ChaoProjector needs a volume!");
		return 0;
	}
	Vec3i origin(0,0,0);
	// If a sensible origin isn't passed in, choose the middle of
	// the cube.
	if (params.has_key("origin_x")) {origin[0] = params["origin_x"];}
	else {origin[0] = nxvol/2+1;}
	if (params.has_key("origin_y")) {origin[1] = params["origin_y"];}
	else {origin[1] = nyvol/2+1;}
	if (params.has_key("origin_z")) {origin[2] = params["origin_z"];}
	else {origin[2] = nzvol/2+1;}

	int ri;
	if (params.has_key("radius")) {ri = params["radius"];}
	else {ri = dim/2 - 1;}

	// retrieve the voxel values
	float *cube = vol->get_data();

	// count the number of voxels within a sphere centered at icent,
	// with radius ri
	status = getnnz(volsize, ri, origin, &nrays, &nnz);
	// need to check status...

	// convert from cube to sphere
	sphere = new float[nnz];
	ptrs   = new int[nrays+1];
	cord   = new int[3*nrays];
	if (sphere == NULL || ptrs == NULL || cord == NULL) {
		fprintf(stderr,"ChaoProjector::project3d, failed to allocate!\n");
		exit(1);
	}
	for (int i = 0; i<nnz; i++) sphere[i] = 0.0;
	for (int i = 0; i<nrays+1; i++) ptrs[i] = 0;
	for (int i = 0; i<3*nrays; i++) cord[i] = 0;

	status = cb2sph(cube, volsize, ri, origin, nnz, ptrs, cord, sphere);
	// check status

	int nangles = 0;
	vector<float> anglelist;
	string angletype = "SPIDER";
	// Do we have a list of angles?
	if (params.has_key("anglelist")) {
		anglelist = params["anglelist"];
		nangles = anglelist.size() / 3;
	} else {
		Transform* t3d = params["transform"];
		if ( t3d == NULL ) throw NullPointerException("The transform object (required for projection), was not specified");
		// This part was modified by David Woolford -
		// Before this the code worked only for SPIDER and EMAN angles,
		// but the framework of the Transform3D allows for a generic implementation
		// as specified here.
		Dict p = t3d->get_rotation("spider");
		if(t3d) {delete t3d; t3d=0;}

		float phi   = p["phi"];
		float theta = p["theta"];
		float psi   = p["psi"];
		anglelist.push_back(phi);
		anglelist.push_back(theta);
		anglelist.push_back(psi);
		nangles = 1;
	}
	// End David Woolford modifications

	dm = new float[nangles*9];
	setdm(anglelist, angletype, dm);

		// return images
	EMData *ret = new EMData();
	ret->set_size(nxvol, nyvol, nangles);
	ret->set_complex(false);
	ret->set_ri(true);

	images = ret->get_data();

	for (j = 1; j <= nangles; j++) {
		status = fwdpj3(volsize, nrays, nnz   , &dm(1,j), origin, ri,
						ptrs   ,  cord, sphere, &images(1,1,j));
	// check status?
	}

	// deallocate all temporary work space
	EMDeleteArray(dm);
	EMDeleteArray(ptrs);
	EMDeleteArray(cord);
	EMDeleteArray(sphere);

	if (!params.has_key("anglelist")) {
		Transform* t3d = params["transform"];
		ret->set_attr("xform.projection",t3d);
		if(t3d) {delete t3d; t3d=0;}
	}
	ret->update();
	return ret;
}


#undef images

#define images(i,j,k) images[ ((k)-1)*nximg*nyimg + ((j)-1)*nximg + (i)-1 ]
// backproject from 2D to 3D (multiple images)
EMData *ChaoProjector::backproject3d(EMData * imagestack) const
{
	int nrays, nnz, status, j;
	float *dm;
	int   *ptrs, *cord;
	float *sphere, *images, *cube;

	int nximg   = imagestack->get_xsize();
	int nyimg   = imagestack->get_ysize();
	int nslices = imagestack->get_zsize();

	int dim = Util::get_min(nximg,nyimg);
	Vec3i volsize(nximg,nyimg,dim);

	Vec3i origin(0,0,0);
	// If a sensible origin isn't passed in, choose the middle of
	// the cube.
	if (params.has_key("origin_x")) {origin[0] = params["origin_x"];}
	else {origin[0] = nximg/2+1;}
	if (params.has_key("origin_y")) {origin[1] = params["origin_y"];}
	else {origin[1] = nyimg/2+1;}
	if (params.has_key("origin_z")) {origin[1] = params["origin_z"];}
	else {origin[2] = dim/2+1;}

	int ri;
	if (params.has_key("radius")) {ri = params["radius"];}
	else {ri = dim/2 - 1;}

	// retrieve the voxel values
	images = imagestack->get_data();

	// count the number of voxels within a sphere centered at icent,
	// with radius ri
	status = getnnz(volsize, ri, origin, &nrays, &nnz);
	// need to check status...

	// convert from cube to sphere
	sphere = new float[nnz];
	ptrs   = new int[nrays+1];
	cord   = new int[3*nrays];
	if (sphere == NULL || ptrs == NULL || cord == NULL) {
		fprintf(stderr,"ChaoProjector::backproject3d, failed to allocate!\n");
		exit(1);
	}
	for (int i = 0; i<nnz; i++) sphere[i] = 0.0;
	for (int i = 0; i<nrays+1; i++) ptrs[i] = 0;
	for (int i = 0; i<3*nrays; i++) cord[i] = 0;

	int nangles = 0;
	vector<float> anglelist;
	string angletype = "SPIDER";
	// Do we have a list of angles?
	if (params.has_key("anglelist")) {
		anglelist = params["anglelist"];
		nangles = anglelist.size() / 3;
	} else {
		Transform* t3d = params["transform"];
		if ( t3d == NULL ) throw NullPointerException("The transform object (required for projection), was not specified");
		// This part was modified by David Woolford -
		// Before this the code worked only for SPIDER and EMAN angles,
		// but the framework of the Transform3D allows for a generic implementation
		// as specified here.
		//  This was broken by david.  we need here a loop over all projections and put all angles on stack  PAP 06/28/09
		Dict p = t3d->get_rotation("spider");
		if(t3d) {delete t3d; t3d=0;}

		float phi = p["phi"];
		float theta = p["theta"];
		float psi = p["psi"];
		anglelist.push_back(phi);
		anglelist.push_back(theta);
		anglelist.push_back(psi);
		nangles = 1;
	}

	// End David Woolford modifications

	if (nslices != nangles) {
		LOGERR("the number of images does not match the number of angles");
		return 0;
	}

	dm = new float[nangles*9];
	setdm(anglelist, angletype, dm);

	// return volume
	EMData *ret = new EMData();
	ret->set_size(nximg, nyimg, dim);
	ret->set_complex(false);
	ret->set_ri(true);
	ret->to_zero();

	cube = ret->get_data();
	// cb2sph should be replaced by something that touches only ptrs and cord
	status = cb2sph(cube, volsize, ri, origin, nnz, ptrs, cord, sphere);
	// check status

	for (j = 1; j <= nangles; j++) {
		status = bckpj3(volsize, nrays, nnz, &dm(1,j), origin, ri,
			 ptrs   , cord , &images(1,1,j), sphere);
	// check status?
	}

	status = sph2cb(sphere, volsize, nrays, ri, nnz, ptrs, cord, cube);
	// check status?

	// deallocate all temporary work space
	EMDeleteArray(dm);
	EMDeleteArray(ptrs);
	EMDeleteArray(cord);
	EMDeleteArray(sphere);

	ret->update();
	return ret;
}

#undef images
#undef cube
#undef sphere
#undef cord
#undef ptrs
#undef dm

#define images(i,j,k) images[ (k)*nx*ny + ((j)-1)*nx + (i)-1 ]

// EMData *PawelProjector::backproject3d(EMData * imagestack) const
// {
//
//     float *images;
//
//     if (!imagestack) {
// 	return 0;
//     }
//     int ri;
//     int nx      = imagestack->get_xsize();
//     int ny      = imagestack->get_ysize();
// //     int nslices = imagestack->get_zsize();
//     int dim = Util::get_min(nx,ny);
//     images  = imagestack->get_data();
//
//     Vec3i origin(0,0,0);
//     // If a sensible origin isn't passed in, choose the middle of
//     // the cube.
//     if (params.has_key("origin_x")) {origin[0] = params["origin_x"];}
//     else {origin[0] = nx/2;}
//     if (params.has_key("origin_y")) {origin[1] = params["origin_y"];}
//     else {origin[1] = ny/2;}
//     if (params.has_key("origin_z")) {origin[1] = params["origin_z"];}
//     else {origin[2] = dim/2;}
//
//     if (params.has_key("radius")) {ri = params["radius"];}
//     else {ri = dim/2 - 1;}
//
//     // Determine the number of rows (x-lines) within the radius
//     int nn = -1;
//     prepcubes(nx, ny, dim, ri, origin, nn);
//     // nn is now the number of rows-1 within the radius
//     // so we can create and fill the ipcubes
//     IPCube* ipcube = new IPCube[nn+1];
//     prepcubes(nx, ny, dim, ri, origin, nn, ipcube);
//
// 	int nangles = 0;
// 	vector<float> anglelist;
// 	// Do we have a list of angles?
// 	if (params.has_key("anglelist")) {
// 		anglelist = params["anglelist"];
// 		nangles = anglelist.size() / 3;
// 	} else {
// 		Transform3D* t3d = params["t3d"];
// 		if ( t3d == NULL ) throw NullPointerException("The transform3d object (required for projection), was not specified");
// 		// This part was modified by David Woolford -
// 		// Before this the code worked only for SPIDER and EMAN angles,
// 		// but the framework of the Transform3D allows for a generic implementation
// 		// as specified here.
// 		Dict p = t3d->get_rotation(Transform3D::SPIDER);
//
// 		string angletype = "SPIDER";
// 		float phi = p["phi"];
// 		float theta = p["theta"];
// 		float psi = p["psi"];
// 		anglelist.push_back(phi);
// 		anglelist.push_back(theta);
// 		anglelist.push_back(psi);
// 		nangles = 1;
// 	}
//
// 	// End David Woolford modifications
//
//     // initialize return object
//     EMData* ret = new EMData();
//     ret->set_size(nx, ny, dim);
//     ret->to_zero();
//
//     // loop over sets of angles
//     for (int ia = 0; ia < nangles; ia++) {
//        int indx = 3*ia;
// 	   Transform3D rotation(Transform3D::SPIDER, float(anglelist[indx]),
//                             float(anglelist[indx+1]),
//                             float(anglelist[indx+2]));
//        float dm1 = rotation.at(0,0);
//        float dm4 = rotation.at(1,0);
//
//        if (2*(ri+1)+1 > dim) {
//           // Must check x and y boundaries
//           LOGERR("backproject3d, pawel, 2*(ri+1)+1 > dim\n");
//           return 0;
//        } else {
//           // No need to check x and y boundaries
//           for (int i = 0 ; i <= nn; i++) {
//              int iox = (int)ipcube[i].loc[0]+origin[0];
//              int ioy = (int)ipcube[i].loc[1]+origin[1];
//              int ioz = (int)ipcube[i].loc[2]+origin[2];
//
//              Vec3f vb = rotation*ipcube[i].loc + origin;
//              for (int j = ipcube[i].start; j <= ipcube[i].end; j++) {
//                 float xbb = (j-ipcube[i].start)*dm1 + vb[0];
//                 int   iqx = (int)floor(xbb);
//
//                 float ybb = (j-ipcube[i].start)*dm4 + vb[1];
//                 int   iqy = (int)floor(ybb);
//
//                 float dipx = xbb - iqx;
//                 float dipy = ybb - iqy;
//
//                 (*ret)(iox,ioy,ioz) += images(iqx,iqy,ia)
//                     + dipy*(images(iqx,iqy+1,ia)-images(iqx,iqy,ia))
//                     + dipx*(images(iqx+1,iqy,ia)-images(iqx,iqy,ia)
//                     + dipy*(images(iqx+1,iqy+1,ia)-images(iqx+1,iqy,ia)
//                     - images(iqx,iqy+1,ia)+images(iqx,iqy,ia)));
//                 iox++;
//              } // end for j
// 	  } // end for i
//        } // end if
//     } // end for ia
//
//     ret->update();
//     EMDeleteArray(ipcube);
//     return ret;
// }
EMData *PawelProjector::backproject3d(EMData * imagestack) const
{

	float *images;

	if (!imagestack) {
		return 0;
	}
	int ri;
	int nx      = imagestack->get_xsize();
	int ny      = imagestack->get_ysize();
//     int nslices = imagestack->get_zsize();
	int dim = Util::get_min(nx,ny);
	images  = imagestack->get_data();

	Vec3i origin(0,0,0);
    // If a sensible origin isn't passed in, choose the middle of
    // the cube.
	if (params.has_key("origin_x")) {origin[0] = params["origin_x"];}
	else {origin[0] = nx/2;}
	if (params.has_key("origin_y")) {origin[1] = params["origin_y"];}
	else {origin[1] = ny/2;}
	if (params.has_key("origin_z")) {origin[1] = params["origin_z"];}
	else {origin[2] = dim/2;}

	if (params.has_key("radius")) {ri = params["radius"];}
	else {ri = dim/2 - 1;}

    // Determine the number of rows (x-lines) within the radius
	int nn = -1;
	prepcubes(nx, ny, dim, ri, origin, nn);
    // nn is now the number of rows-1 within the radius
    // so we can create and fill the ipcubes
	IPCube* ipcube = new IPCube[nn+1];
	prepcubes(nx, ny, dim, ri, origin, nn, ipcube);

	int nangles = 0;
	vector<float> anglelist;
	// Do we have a list of angles?
	if (params.has_key("anglelist")) {
		anglelist = params["anglelist"];
		nangles = anglelist.size() / 3;
	} else {
		Transform* t3d = params["transform"];
		if ( t3d == NULL ) throw NullPointerException("The transform object (required for projection), was not specified");
		// This part was modified by David Woolford -
		// Before this the code worked only for SPIDER and EMAN angles,
		// but the framework of the Transform3D allows for a generic implementation
		// as specified here.
		Dict p = t3d->get_rotation("spider");
		if(t3d) {delete t3d; t3d=0;}

		string angletype = "SPIDER";
		float phi = p["phi"];
		float theta = p["theta"];
		float psi = p["psi"];
		anglelist.push_back(phi);
		anglelist.push_back(theta);
		anglelist.push_back(psi);
		nangles = 1;
	}

	// End David Woolford modifications

    // initialize return object
	EMData* ret = new EMData();
	ret->set_size(nx, ny, dim);
	ret->to_zero();

    // loop over sets of angles
	for (int ia = 0; ia < nangles; ia++) {
		int indx = 3*ia;
		Dict d("type","spider","phi",anglelist[indx],"theta",anglelist[indx+1],"psi",anglelist[indx+2]);
		Transform rotation(d);
		float dm1 = rotation.at(0,0);
		float dm4 = rotation.at(1,0);

		if (2*(ri+1)+1 > dim) {
          // Must check x and y boundaries
			LOGERR("backproject3d, pawel, 2*(ri+1)+1 > dim\n");
			return 0;
		} else {
          // No need to check x and y boundaries
			for (int i = 0 ; i <= nn; i++) {
				int iox = (int)ipcube[i].loc[0]+origin[0];
				int ioy = (int)ipcube[i].loc[1]+origin[1];
				int ioz = (int)ipcube[i].loc[2]+origin[2];

				Vec3f vb = rotation*ipcube[i].loc + origin;
				for (int j = ipcube[i].start; j <= ipcube[i].end; j++) {
					float xbb = (j-ipcube[i].start)*dm1 + vb[0];
					int   iqx = (int)floor(xbb);

					float ybb = (j-ipcube[i].start)*dm4 + vb[1];
					int   iqy = (int)floor(ybb);

					float dipx = xbb - iqx;
					float dipy = ybb - iqy;

					(*ret)(iox,ioy,ioz) += images(iqx,iqy,ia)
							+ dipy*(images(iqx,iqy+1,ia)-images(iqx,iqy,ia))
							+ dipx*(images(iqx+1,iqy,ia)-images(iqx,iqy,ia)
									+ dipy*(images(iqx+1,iqy+1,ia)-images(iqx+1,iqy,ia)
											- images(iqx,iqy+1,ia)+images(iqx,iqy,ia)));
					iox++;
				} // end for j
			} // end for i
		} // end if
	} // end for ia

	ret->update();
	EMDeleteArray(ipcube);
	return ret;
}
#undef images

EMData *StandardProjector::backproject3d(EMData * ) const
{
   // no implementation yet
   EMData *ret = new EMData();
   return ret;
}

EMData *MaxValProjector::backproject3d(EMData * ) const
{
   // no implementation yet
   EMData *ret = new EMData();
   return ret;
}


EMData *FourierGriddingProjector::backproject3d(EMData * ) const
{
   // no implementation yet
   EMData *ret = new EMData();
   return ret;
}

// End Chao's projector addition 4/25/06

void EMAN::dump_projectors()
{
	dump_factory < Projector > ();
}

map<string, vector<string> > EMAN::dump_projectors_list()
{
	return dump_factory_list < Projector > ();
}
