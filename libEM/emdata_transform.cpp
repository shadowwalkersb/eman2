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

#include "emdata.h"
#include "emfft.h"

#include <cstring>
#include <cstdio>

#include  "gsl/gsl_sf_result.h"
#include  "gsl/gsl_sf_bessel.h"
#include <iostream>
#include <algorithm>
#include <vector>
#include <utility>
#include <cmath>
#include "util.h"

//#ifdef EMAN2_USING_CUDA
//#include "cuda/cuda_processor.h"
//#endif

using namespace EMAN;
using namespace std;
typedef vector< pair<float,int> > vp;

EMData *EMData::do_fft() const
{
	ENTERFUNC;
#ifdef FFT_CACHING
	if (fftcache!=0) {
		return fftcache->copy();
	}
#endif //FFT_CACHING

	if (is_complex() ) { // ming add 08/17/2010
#ifdef NATIVE_FFT
		LOGERR(" NATIVE_FFT does not support complex to complex.");  // PAP
		throw ImageFormatException("real image expected. Input image is complex image.");
#else
		EMData *temp_in=copy();
		EMData *dat= copy_head();
		int offset;
		if(is_fftpadded()) {
			offset = is_fftodd() ? 1 : 2;
		}
		else offset=0;
		//printf("offset=%d\n",offset);
		EMfft::complex_to_complex_nd(temp_in->get_data(),dat->get_data(),nx-offset,ny,nz);

		if(dat->get_ysize()==1 && dat->get_zsize()==1) dat->set_complex_x(true);

		dat->update();
		delete temp_in;
		EXITFUNC;
		return dat;
#endif // NATIVE_FFT
	} else {
		int nxreal = nx;
		int offset = 2 - nx%2;
		int nx2 = nx + offset;
		EMData* dat = copy_head();
		dat->set_size(nx2, ny, nz);
		//dat->to_zero();  // do not need it, real_to_complex will do it right anyway
		if (offset == 1) dat->set_fftodd(true);
		else             dat->set_fftodd(false);

		float *d = dat->get_data();
		//std::cout<<" do_fft "<<rdata[5]<<"  "<<d[5]<<std::endl;
		EMfft::real_to_complex_nd(get_data(), d, nxreal, ny, nz);

		dat->update();
		dat->set_fftpad(true);
		dat->set_complex(true);
		dat->set_attr("is_intensity",false);
		if(dat->get_ysize()==1 && dat->get_zsize()==1) dat->set_complex_x(true);
		dat->set_ri(true);

		EXITFUNC;
#ifdef FFT_CACHING
//		printf("%p %d\n",this,nxyz);
		if (nxyz<80000000) {
			fftcache=dat->copy();
		}
#endif //FFT_CACHING
		return dat;
	}
}

void EMData::do_fft_inplace()
{
	ENTERFUNC;

	if ( is_complex() ) {
		LOGERR("real image expected. Input image is complex image.");
		throw ImageFormatException("real image expected. Input image is complex image.");
	}

	size_t offset;
	int nxreal;
	get_data(); // Required call if GPU caching is being used. Otherwise harmless
	if (!is_fftpadded()) {
		// need to extend the matrix along x
		// meaning nx is the un-fftpadded size
		nxreal = nx;
		offset = 2 - nx%2;
		if (1 == offset) set_fftodd(true);
		else             set_fftodd(false);
		int nxnew = nx + offset;
		set_size(nxnew, ny, nz);
		for (int iz = nz-1; iz >= 0; iz--) {
			for (int iy = ny-1; iy >= 0; iy--) {
				for (int ix = nxreal-1; ix >= 0; ix--) {
					size_t oldxpos = ix + (iy + iz*ny)*(size_t)nxreal;
					size_t newxpos = ix + (iy + iz*ny)*(size_t)nxnew;
					(*this)(newxpos) = (*this)(oldxpos);
				}
			}
		}
		set_fftpad(true);
	} else {
		offset = is_fftodd() ? 1 : 2;
		nxreal = nx - offset;
	}
	EMfft::real_to_complex_nd(rdata, rdata, nxreal, ny, nz);

	set_complex(true);
	if(ny==1 && nz==1)  set_complex_x(true);
	set_ri(true);

	update();

	EXITFUNC;
	//return this;
}

#ifdef EMAN2_USING_CUDA

#include "cuda/cuda_emfft.h"

EMData *EMData::do_fft_cuda()
{
	ENTERFUNC;

	if ( is_complex() ) {
		LOGERR("real image expected. Input image is complex image.");
		throw ImageFormatException("real image expected. Input image is complex image.");
	}

	int offset = 2 - nx%2;
	EMData* dat = new EMData(0,0,nx+offset,ny,nz,attr_dict);
	if(!dat->rw_alloc()) throw UnexpectedBehaviorException("Bad alloc");
	//cout << "Doing CUDA FFT " << cudarwdata << endl;
	if(cudarwdata == 0){copy_to_cuda();}
	cuda_dd_fft_real_to_complex_nd(cudarwdata, dat->cudarwdata, nx, ny,nz, 1);

	if (offset == 1) dat->set_fftodd(true);
	else             dat->set_fftodd(false);

	dat->set_fftpad(true);
	dat->set_complex(true);
	if(dat->get_ysize()==1 && dat->get_zsize()==1) dat->set_complex_x(true);
	dat->set_ri(true);
	dat->update();

	EXITFUNC;
	return dat;
}

void EMData::do_fft_inplace_cuda()
{
	ENTERFUNC;

	if ( is_complex() ) {
		LOGERR("real image expected. Input image is complex image.");
		throw ImageFormatException("real image expected. Input image is complex image.");
	}

	int offset = 2 - nx%2;
	float* tempcudadata = 0;
	cudaError_t error = cudaMalloc((void**)&tempcudadata,(nx + offset)*ny*nz*sizeof(float));
	if( error != cudaSuccess) throw ImageFormatException("Couldn't allocate memory.");
	
	//cout << "Doing CUDA FFT inplace" << cudarwdata << endl;
	if(cudarwdata == 0){copy_to_cuda();}
	cuda_dd_fft_real_to_complex_nd(cudarwdata, tempcudadata, nx, ny,nz, 1);
	// this section is a bit slight of hand it actually does the FFT out of place but this avoids and EMData object creation and detruction...
	cudaError_t ferror = cudaFree(cudarwdata);
	if ( ferror != cudaSuccess) throw UnexpectedBehaviorException( "CudaFree failed:" + string(cudaGetErrorString(error)));
	cudarwdata = tempcudadata;
	num_bytes = (nx + offset)*ny*nz*sizeof(float);

	if (offset == 1) set_fftodd(true);
	else             set_fftodd(false);

	nx = nx + offset; // don't want to call set_size b/c that will delete my cudadata, remember what I am doing is a bit slignt of hand....
	set_fftpad(true);
	set_complex(true);
	if(get_ysize()==1 && get_zsize()==1) set_complex_x(true);
	set_ri(true);
	update();

	EXITFUNC;
//	return this;
}

EMData *EMData::do_ift_cuda()
{
	ENTERFUNC;

	if (!is_complex()) {
		LOGERR("complex image expected. Input image is real image.");
		throw ImageFormatException("complex image expected. Input image is real image.");
	}

	if (!is_ri()) {
		throw ImageFormatException("complex ri expected. Got amplitude/phase.");
	}

	int offset = is_fftodd() ? 1 : 2;
	EMData* dat = new EMData(0,0,nx-offset,ny,nz,attr_dict);
	if(!dat->rw_alloc()) throw UnexpectedBehaviorException("Bad alloc");
	
	if(cudarwdata == 0){copy_to_cuda();}

	
	int ndim = get_ndim();
	if ( ndim == 1 ) {
		cuda_dd_fft_complex_to_real_nd(cudarwdata,dat->cudarwdata, nx-offset,1,1,1);
	} else if (ndim == 2) {
		cuda_dd_fft_complex_to_real_nd(cudarwdata,dat->cudarwdata, ny,nx-offset,1,1);
	} else if (ndim == 3) {
		cuda_dd_fft_complex_to_real_nd(cudarwdata,dat->cudarwdata, nz,ny,nx-offset,1);
	} else throw ImageDimensionException("No cuda FFT support of images with dimensions exceeding 3");
	
	// SCALE the inverse FFT
	float scale = 1.0f/static_cast<float>((dat->get_size()));
	dat->mult(scale); 

	dat->set_fftpad(false);
	dat->set_fftodd(false);
	dat->set_complex(false);
	if(dat->get_ysize()==1 && dat->get_zsize()==1)  dat->set_complex_x(false);
	dat->set_ri(false);
//	dat->gpu_update();
	dat->update(); 
	
	EXITFUNC;
	return dat;
}

/*
   FFT in place does not depad, hence this routine is of limited use b/c mem operations on the device are quite SLOW, JFF
   use
*/

void EMData::do_ift_inplace_cuda()
{
	ENTERFUNC;

	if (!is_complex()) {
		LOGERR("complex image expected. Input image is real image.");
		throw ImageFormatException("complex image expected. Input image is real image.");
	}

	if (!is_ri()) {
		LOGWARN("run IFT on AP data, only RI should be used. ");
	}

	int offset = is_fftodd() ? 1 : 2;
	
	if(cudarwdata == 0){copy_to_cuda();}
	
	int ndim = get_ndim();
	if ( ndim == 1 ) {
		cuda_dd_fft_complex_to_real_nd(cudarwdata,cudarwdata, nx-offset,1,1,1);
	} else if (ndim == 2) {
		cuda_dd_fft_complex_to_real_nd(cudarwdata,cudarwdata, ny,nx-offset,1,1);
	} else if (ndim == 3) {
		cuda_dd_fft_complex_to_real_nd(cudarwdata,cudarwdata, nz,ny,nx-offset,1);
	} else throw ImageDimensionException("No cuda FFT support of images with dimensions exceeding 3");
#if defined USE_FFTW3 //native fft and ACML already done normalization
	// SCALE the inverse FFT
	int nxo = nx - offset;
	float scale = 1.0f / (nxo * ny * nz);
	mult(scale); //if we are just doing a CCF, this is a waste!
#endif //USE_FFTW3

	set_fftpad(true);
	set_complex(false);

	if(ny==1 && nz==1) set_complex_x(false);
	set_ri(false);
	update();
	
	EXITFUNC;
//	return this;
}

#endif //EMAN2_USING_CUDA

EMData *EMData::do_ift()
{
	ENTERFUNC;

	if (!is_complex()) {
		LOGERR("complex image expected. Input image is real image.");
		throw ImageFormatException("complex image expected. Input image is real image.");
	}

	if (!is_ri()) {
		LOGWARN("run IFT on AP data, only RI should be used. Converting.");
	}

	get_data(); // Required call if GPU caching is being used. Otherwise harmless
	EMData* dat = copy_head();
	dat->set_size(nx, ny, nz);
	ap2ri();

	float *d = dat->get_data();
	int ndim = get_ndim();

	/* Do inplace IFT on a image copy, because the complex to real transform of
	 * nd will destroy its input array even for out-of-place transforms.
	 */
	memcpy((char *) d, (char *) rdata, (size_t)nx * ny * nz * sizeof(float));

	int offset = is_fftodd() ? 1 : 2;
	//cout << "Sending offset " << offset << " " << nx-offset << endl;
	if (ndim == 1) {
		EMfft::complex_to_real_nd(d, d, nx - offset, ny, nz);
	} else {
		EMfft::complex_to_real_nd(d, d, nx - offset, ny, nz);

		size_t row_size = (nx - offset) * sizeof(float);
		for (size_t i = 1; i < (size_t)ny * nz; i++) {
			memmove((char *) &d[i * (nx - offset)], (char *) &d[i * nx], row_size);
		}
	}

	dat->set_size(nx - offset, ny, nz);	//remove the padding
#if defined USE_FFTW3 //native fft and ACML already done normalization
	// SCALE the inverse FFT
	float scale = 1.0f / ((nx - offset) * ny * nz);
	dat->mult(scale);
#endif	//USE_FFTW3
	dat->set_fftodd(false);
	dat->set_fftpad(false);
	dat->set_complex(false);
	if(dat->get_ysize()==1 && dat->get_zsize()==1)  dat->set_complex_x(false);
	dat->set_ri(false);
	dat->set_attr("is_intensity",false);
	dat->update();


	EXITFUNC;
	return dat;
}

/*
   FFT in place does not depad, return real x-extended image (needs to be depadded before use as PAP does in CCF routines)
   use
*/
void EMData::do_ift_inplace()
{
	ENTERFUNC;

	if (!is_complex()) {
		LOGERR("complex image expected. Input image is real image.");
		throw ImageFormatException("complex image expected. Input image is real image.");
	}

	if (!is_ri()) {
		LOGWARN("run IFT on AP data, only RI should be used. ");
	}
	ap2ri();

	int offset = is_fftodd() ? 1 : 2;
	float* data = get_data();
	EMfft::complex_to_real_nd(data, data, nx - offset, ny, nz);

#if defined USE_FFTW3 	//native fft and ACML already done normalization
	// SCALE the inverse FFT
	int nxo = nx - offset;
	float scale = 1.0f / ((size_t)nxo * ny * nz);
	mult(scale);
#endif //USE_FFTW3

	set_fftpad(true);
	set_complex(false);
	if(ny==1 && nz==1) set_complex_x(false);
	set_ri(false);
	update();

	EXITFUNC;
//	return this;
}
#undef rdata


EMBytes EMData::render_ap24(int x0, int y0, int ixsize, int iysize,
						 int bpl, float scale, int mingray, int maxgray,
						 float render_min, float render_max,float gamma,int flags)
{
	ENTERFUNC;

	int asrgb;
	int hist=(flags&2)/2;
	int invy=(flags&4)?1:0;

	if (!is_complex()) throw ImageDimensionException("complex only");

	if (get_ndim() != 2) {
		throw ImageDimensionException("2D only");
	}

	if (is_complex()) ri2ap();

	if (render_max <= render_min) {
		render_max = render_min + 0.01f;
	}

	if (gamma<=0) gamma=1.0;

	// Calculating a full floating point gamma for
	// each pixel in the image slows rendering unacceptably
	// however, applying a gamma-mapping to an 8 bit colorspace
	// has unaccepable accuracy. So, we oversample the 8 bit colorspace
	// as a 12 bit colorspace and apply the gamma mapping to that
	// This should produce good accuracy for gamma values
	// larger than 0.5 (and a high upper limit)
	static int smg0=0,smg1=0;	// while this destroys threadsafety in the rendering process
	static float sgam=0;		// it is necessary for speed when rendering large numbers of small images
	static unsigned char gammamap[4096];
	if (gamma!=1.0 && (smg0!=mingray || smg1!=maxgray || sgam!=gamma)) {
		for (int i=0; i<4096; i++) {
			if (mingray<maxgray) gammamap[i]=(unsigned char)(mingray+(maxgray-mingray+0.999)*pow(((float)i/4096.0f),gamma));
			else gammamap[4095-i]=(unsigned char)(mingray+(maxgray-mingray+0.999)*pow(((float)i/4096.0f),gamma));
		}
	}
	smg0=mingray;	// so we don't recompute the map unless something changes
	smg1=maxgray;
	sgam=gamma;

	if (flags&8) asrgb=4;
	else if (flags&1) asrgb=3;
	else throw ImageDimensionException("must set flag 1 or 8");

	EMBytes ret=EMBytes();
//	ret.resize(iysize*bpl);
	ret.assign(iysize*bpl+hist*1024,char(mingray));
	unsigned char *data=(unsigned char *)ret.data();
	unsigned int *histd=(unsigned int *)(data+iysize*bpl);
	if (hist) {
		for (int i=0; i<256; i++) histd[i]=0;
	}

	float rm = render_min;
	float inv_scale = 1.0f / scale;
	int ysize = iysize;
	int xsize = ixsize;

	int ymin = 0;
	if (iysize * inv_scale > ny) {
		ymin = (int) (iysize - ny / inv_scale);
	}

	float gs = (maxgray - mingray) / (render_max - render_min);
	float gs2 = 4095.999f / (render_max - render_min);
//	float gs2 = 1.0 / (render_max - render_min);
	if (render_max < render_min) {
		gs = 0;
		rm = FLT_MAX;
	}

	int dsx = -1;
	int dsy = 0;
	int remx = 0;
	int remy = 0;
	const int scale_n = 100000;

	int addi = 0;
	int addr = 0;
	if (inv_scale == floor(inv_scale)) {
		dsx = (int) inv_scale;
		dsy = (int) (inv_scale * nx);
	}
	else {
		addi = (int) floor(inv_scale);
		addr = (int) (scale_n * (inv_scale - floor(inv_scale)));
	}

	int xmin = 0;
	if (x0 < 0) {
		xmin = (int) (-x0 / inv_scale);
		xsize -= (int) floor(x0 / inv_scale);
		x0 = 0;
	}

	if ((xsize - xmin) * inv_scale > (nx - x0)) {
		xsize = (int) ((nx - x0) / inv_scale + xmin);
	}
	int ymax = ysize - 1;
	if (y0 < 0) {
		ymax = (int) (ysize + y0 / inv_scale - 1);
		ymin += (int) floor(y0 / inv_scale);
		y0 = 0;
	}

	if (xmin < 0) xmin = 0;
	if (ymin < 0) ymin = 0;
	if (xsize > ixsize) xsize = ixsize;
	if (ymax > iysize) ymax = iysize;

	int lmax = nx * ny - 1;

	int mid=nx*ny/2;
	float* image_data = get_data();
	if (dsx != -1) {
		int l = y0 * nx;
		for (int j = ymax; j >= ymin; j--) {
			int ll = x0;
			for (int i = xmin; i < xsize; i++) {
				if (l + ll > lmax || ll >= nx - 2) break;

				int k = 0;
				unsigned char p;
				int ph;
				if (ll >= nx / 2) {
					if (l >= (ny - inv_scale) * nx) k = 2 * (ll - nx / 2) + 2;
					else k = 2 * (ll - nx / 2) + l + 2 + nx;
					if (k>=mid) k-=mid;		// These 2 lines handle the Fourier origin being in the corner, not the middle
					else k+=mid;
					ph = (int)(image_data[k+1]*768/(2.0*M_PI))+384;	// complex phase as integer 0-767
				}
				else {
					k = nx * ny - (l + 2 * ll) - 2;
					ph = (int)(-image_data[k+1]*768/(2.0*M_PI))+384;	// complex phase as integer 0-767
					if (k>=mid) k-=mid;		// These 2 lines handle the Fourier origin being in the corner, not the middle
					else k+=mid;
				}
				float t = image_data[k];
				if (t <= rm)  p = mingray;
				else if (t >= render_max) p = maxgray;
				else if (gamma!=1.0) {
					k=(int)(gs2 * (t-render_min));		// map float value to 0-4096 range
					p = gammamap[k];					// apply gamma using precomputed gamma map
				}
				else {
					p = (unsigned char) (gs * (t - render_min));
					p += mingray;
				}
				if (ph<256) {
					data[i * asrgb + j * bpl] = p*(255-ph)/256;
					data[i * asrgb + j * bpl+1] = p*ph/256;
					data[i * asrgb + j * bpl+2] = 0;
				}
				else if (ph<512) {
					data[i * asrgb + j * bpl+1] = p*(511-ph)/256;
					data[i * asrgb + j * bpl+2] = p*(ph-256)/256;
					data[i * asrgb + j * bpl] = 0;
				}
				else {
					data[i * asrgb + j * bpl+2] = p*(767-ph)/256;
					data[i * asrgb + j * bpl] = p*(ph-512)/256;
					data[i * asrgb + j * bpl+1] = 0;
				}
				if (hist) histd[p]++;
				ll += dsx;
			}
			l += dsy;
		}
	}
	else {
		remy = 10;
		int l = y0 * nx;
		for (int j = ymax; j >= ymin; j--) {
			int br = l;
			remx = 10;
			int ll = x0;
			for (int i = xmin; i < xsize - 1; i++) {
				if (l + ll > lmax || ll >= nx - 2) {
					break;
				}
				int k = 0;
				unsigned char p;
				int ph;
				if (ll >= nx / 2) {
					if (l >= (ny * nx - nx)) k = 2 * (ll - nx / 2) + 2;
					else k = 2 * (ll - nx / 2) + l + 2 + nx;
					if (k>=mid) k-=mid;		// These 2 lines handle the Fourier origin being in the corner, not the middle
					else k+=mid;
					ph = (int)(image_data[k+1]*768/(2.0*M_PI))+384;	// complex phase as integer 0-767
				}
				else {
					k = nx * ny - (l + 2 * ll) - 2;
					if (k>=mid) k-=mid;		// These 2 lines handle the Fourier origin being in the corner, not the middle
					else k+=mid;
					ph = (int)(-image_data[k+1]*768/(2.0*M_PI))+384;	// complex phase as integer 0-767
				}

				float t = image_data[k];
				if (t <= rm)
					p = mingray;
				else if (t >= render_max) {
					p = maxgray;
				}
				else if (gamma!=1.0) {
					k=(int)(gs2 * (t-render_min));		// map float value to 0-4096 range
					p = gammamap[k];					// apply gamma using precomputed gamma map
				}
				else {
					p = (unsigned char) (gs * (t - render_min));
					p += mingray;
				}
				if (ph<256) {
					data[i * asrgb + j * bpl] = p*(255-ph)/256;
					data[i * asrgb + j * bpl+1] = p*ph/256;
					data[i * asrgb + j * bpl+2] = 0;
				}
				else if (ph<512) {
					data[i * asrgb + j * bpl+1] = p*(511-ph)/256;
					data[i * asrgb + j * bpl+2] = p*(ph-256)/256;
					data[i * asrgb + j * bpl] = 0;
				}
				else {
					data[i * asrgb + j * bpl+2] = p*(767-ph)/256;
					data[i * asrgb + j * bpl] = p*(ph-512)/256;
					data[i * asrgb + j * bpl+1] = 0;
				}
				if (hist) histd[p]++;
				ll += addi;
				remx += addr;
				if (remx > scale_n) {
					remx -= scale_n;
					ll++;
				}
			}
			l = br + addi * nx;
			remy += addr;
			if (remy > scale_n) {
				remy -= scale_n;
				l += nx;
			}
		}
	}

	// this replicates r -> g,b
	if (asrgb==4) {
		for (int j=ymin*bpl; j<=ymax*bpl; j+=bpl) {
			for (int i=xmin; i<xsize*4; i+=4) {
				data[i+j+3]=255;
			}
		}
	}

	EXITFUNC;

	// ok, ok, not the most efficient place to do this, but it works
	if (invy) {
		int x,y;
		char swp;
		for (y=0; y<iysize/2; y++) {
			for (x=0; x<ixsize; x++) {
				swp=ret[y*bpl+x];
				ret[y*bpl+x]=ret[(iysize-y-1)*bpl+x];
				ret[(iysize-y-1)*bpl+x]=swp;
			}
		}
	}

    //	return PyString_FromStringAndSize((const char*) data,iysize*bpl);
	return ret;
}


void EMData::render_amp24( int x0, int y0, int ixsize, int iysize,
						  int bpl, float scale, int mingray, int maxgray,
						  float render_min, float render_max, void *ref,
						  void cmap(void *, int coord, unsigned char *tri))
{
	ENTERFUNC;

	if (get_ndim() != 2) {
		throw ImageDimensionException("2D only");
	}

	if (is_complex()) {
		ri2ap();
	}

	if (render_max <= render_min) {
		render_max = render_min + 0.01f;
	}

	std::string ret=std::string();
	ret.resize(iysize*bpl);
	unsigned char *data=(unsigned char *)ret.data();

	float rm = render_min;
	float inv_scale = 1.0f / scale;
	int ysize = iysize;
	int xsize = ixsize;
	const int scale_n = 100000;

	int ymin = 0;
	if ( iysize * inv_scale > ny) {
		ymin = (int) (iysize - ny / inv_scale);
	}
	float gs = (maxgray - mingray) / (render_max - render_min);
	if (render_max < render_min) {
		gs = 0;
		rm = FLT_MAX;
	}
	int dsx = -1;
	int dsy = 0;
	if (inv_scale == floor(inv_scale)) {
		dsx = (int) inv_scale;
		dsy = (int) (inv_scale * nx);
	}
	int addi = 0;
	int addr = 0;

	if (dsx == -1) {
		addi = (int) floor(inv_scale);
		addr = (int) (scale_n * (inv_scale - floor(inv_scale)));
	}

	int remx = 0;
	int remy = 0;
	int xmin = 0;
	if (x0 < 0) {
		xmin = (int) (-x0 / inv_scale);
		xsize -= (int) floor(x0 / inv_scale);
		x0 = 0;
	}

	if ((xsize - xmin) * inv_scale > (nx - x0)) {
		xsize = (int) ((nx - x0) / inv_scale + xmin);
	}
	int ymax = ysize - 1;
	if (y0 < 0) {
		ymax = (int) (ysize + y0 / inv_scale - 1);
		ymin += (int) floor(y0 / inv_scale);
		y0 = 0;
	}


	if (xmin < 0) {
		xmin = 0;
	}

	if (ymin < 0) {
		ymin = 0;
	}
	if (xsize > ixsize) {
		xsize = ixsize;
	}
	if (ymax > iysize) {
		ymax = iysize;
	}

	int lmax = nx * ny - 1;
	unsigned char tri[3];
	float* image_data = get_data();
	if (is_complex()) {
		if (dsx != -1) {
			int l = y0 * nx;
			for (int j = ymax; j >= ymin; j--) {
				int ll = x0;
				for (int i = xmin; i < xsize; i++, ll += dsx) {
					if (l + ll > lmax || ll >= nx - 2) {
						break;
					}
					int kk = 0;
					if (ll >= nx / 2) {
						if (l >= (ny - inv_scale) * nx) {
							kk = 2 * (ll - nx / 2) + 2;
						}
						else {
							kk = 2 * (ll - nx / 2) + l + 2 + nx;
						}
					}
					else {
						kk = nx * ny - (l + 2 * ll) - 2;
					}
					int k = 0;
					float t = image_data[kk];
					if (t <= rm) {
						k = mingray;
					}
					else if (t >= render_max) {
						k = maxgray;
					}
					else {
						k = (int) (gs * (t - render_min));
						k += mingray;
					}
					tri[0] = static_cast < unsigned char >(k);
					cmap(ref, kk, tri);
					data[i * 3 + j * bpl] = tri[0];
					data[i * 3 + 1 + j * bpl] = tri[1];
					data[i * 3 + 2 + j * bpl] = tri[2];
				}
				l += dsy;
			}
		}
		else {
			remy = 10;
			for (int j = ymax, l = y0 * nx; j >= ymin; j--) {
				int br = l;
				remx = 10;
				for (int i = xmin, ll = x0; i < xsize - 1; i++) {
					if (l + ll > lmax || ll >= nx - 2) {
						break;
					}
					int kk = 0;
					if (ll >= nx / 2) {
						if (l >= (ny * nx - nx)) {
							kk = 2 * (ll - nx / 2) + 2;
						}
						else {
							kk = 2 * (ll - nx / 2) + l + 2 + nx;
						}
					}
					else {
						kk = nx * ny - (l + 2 * ll) - 2;
					}
					int k = 0;
					float t = image_data[kk];
					if (t <= rm) {
						k = mingray;
					}
					else if (t >= render_max) {
						k = maxgray;
					}
					else {
						k = (int) (gs * (t - render_min));
						k += mingray;
					}
					tri[0] = static_cast < unsigned char >(k);
					cmap(ref, kk, tri);
					data[i * 3 + j * bpl] = tri[0];
					data[i * 3 + 1 + j * bpl] = tri[1];
					data[i * 3 + 2 + j * bpl] = tri[2];
					ll += addi;
					remx += addr;
					if (remx > scale_n) {
						remx -= scale_n;
						ll++;
					}
				}
				l = br + addi * nx;
				remy += addr;
				if (remy > scale_n) {
					remy -= scale_n;
					l += nx;
				}
			}
		}
	}
	else {
		if (dsx != -1) {
			for (int j = ymax, l = x0 + y0 * nx; j >= ymin; j--) {
				int br = l;
				for (int i = xmin; i < xsize; i++, l += dsx) {
					if (l > lmax) {
						break;
					}
					float t = image_data[l];
					int k = 0;
					if (t <= rm) {
						k = mingray;
					}
					else if (t >= render_max) {
						k = maxgray;
					}
					else {
						k = (int) (gs * (t - render_min));
						k += mingray;
					}
					tri[0] = static_cast < unsigned char >(k);
					cmap(ref, l, tri);
					data[i * 3 + j * bpl] = tri[0];
					data[i * 3 + 1 + j * bpl] = tri[1];
					data[i * 3 + 2 + j * bpl] = tri[2];
				}
				l = br + dsy;
			}
		}
		else {
			remy = 10;
			for (int j = ymax, l = x0 + y0 * nx; j >= ymin; j--) {
				int br = l;
				remx = 10;
				for (int i = xmin; i < xsize; i++) {
					if (l > lmax) {
						break;
					}
					float t = image_data[l];
					int k = 0;
					if (t <= rm) {
						k = mingray;
					}
					else if (t >= render_max) {
						k = maxgray;
					}
					else {
						k = (int) (gs * (t - render_min));
						k += mingray;
					}
					tri[0] = static_cast < unsigned char >(k);
					cmap(ref, l, tri);
					data[i * 3 + j * bpl] = tri[0];
					data[i * 3 + 1 + j * bpl] = tri[1];
					data[i * 3 + 2 + j * bpl] = tri[2];
					l += addi;
					remx += addr;
					if (remx > scale_n) {
						remx -= scale_n;
						l++;
					}
				}
				l = br + addi * nx;
				remy += addr;
				if (remy > scale_n) {
					remy -= scale_n;
					l += nx;
				}
			}
		}
	}

	EXITFUNC;
}

void EMData::ap2ri()
{
	ENTERFUNC;

	if (!is_complex() || is_ri()) {
		return;
	}
	
	Util::ap2ri(get_data(), (size_t)nx * ny * nz);
	set_ri(true);
	update();
	EXITFUNC;
}

void EMData::ri2inten()
{
	ENTERFUNC;

	if (!is_complex()) return;
	if (!is_ri()) ap2ri();

	float * data = get_data();
	size_t size = (size_t)nx * ny * nz;
	for (size_t i = 0; i < size; i += 2) {
		data[i]=data[i]*data[i]+data[i+1]*data[i+1];
		data[i+1]=0;
	}

	set_attr("is_intensity", int(1));
	update();
	EXITFUNC;
}


void EMData::ri2ap()
{
	ENTERFUNC;

	if (!is_complex() || !is_ri()) {
		return;
	}

	float * data = get_data();

	size_t size = (size_t)nx * ny * nz;
	for (size_t i = 0; i < size; i += 2) {
		float f = (float)hypot(data[i], data[i + 1]);
		if (data[i] == 0 && data[i + 1] == 0) {
			data[i + 1] = 0;
		}
		else {
			data[i + 1] = atan2(data[i + 1], data[i]);
		}
		data[i] = f;
	}

	set_ri(false);
	update();
	EXITFUNC;
}


float calc_bessel(const int n, const float& x) {
	gsl_sf_result result;
//	int success =
	gsl_sf_bessel_Jn_e(n,(double)x, &result);
	return (float)result.val;
}

void EMData::insert_clip(const EMData * const block, const IntPoint &origin) {
	int nx1 = block->get_xsize();
	int ny1 = block->get_ysize();
	int nz1 = block->get_zsize();

	Region area(origin[0], origin[1], origin[2],nx1, ny1, nz1);

	//make sure the block fits in EMData 
	int x0 = (int) area.origin[0];
	x0 = x0 < 0 ? 0 : x0;

	int y0 = (int) area.origin[1];
	y0 = y0 < 0 ? 0 : y0;

	int z0 = (int) area.origin[2];
	z0 = z0 < 0 ? 0 : z0;

	int x1 = (int) (area.origin[0] + area.size[0]);
	x1 = x1 > nx ? nx : x1;

	int y1 = (int) (area.origin[1] + area.size[1]);
	y1 = y1 > ny ? ny : y1;

	int z1 = (int) (area.origin[2] + area.size[2]);
	z1 = z1 > nz ? nz : z1;
	if (z1 <= 0) {
		z1 = 1;
	}

	int xd0 = (int) (area.origin[0] < 0 ? -area.origin[0] : 0);
	int yd0 = (int) (area.origin[1] < 0 ? -area.origin[1] : 0);
	int zd0 = (int) (area.origin[2] < 0 ? -area.origin[2] : 0);

	if (x1 < x0 || y1 < y0 || z1 < z0) return; // out of bounds, this is fine, nothing happens

	size_t clipped_row_size = (x1-x0) * sizeof(float);
	size_t src_secsize =  (size_t)(nx1 * ny1);
	size_t dst_secsize = (size_t)(nx * ny);

/*
#ifdef EMAN2_USING_CUDA
	if(block->cudarwdata){
		// this is VERY slow.....
		float *cudasrc = block->cudarwdata + zd0 * src_secsize + yd0 * nx1 + xd0;
		if(!cudarwdata) rw_alloc();
		float *cudadst = cudarwdata + z0 * dst_secsize + y0 * nx + x0;
		for (int i = z0; i < z1; i++) {
			for (int j = y0; j < y1; j++) {
				//printf("%x %x %d\n", cudadst, cudasrc, clipped_row_size);
				cudaMemcpy(cudadst,cudasrc,clipped_row_size,cudaMemcpyDeviceToDevice);
				cudasrc += nx1;
				cudadst += nx;
			}
			cudasrc += src_gap;
			cudadst += dst_gap;
		}
		return;
	}
#endif
*/
	float *src = block->get_data() + (size_t)zd0 * (size_t)src_secsize + (size_t)yd0 * (size_t)nx1 + (size_t)xd0;
	float *dst = get_data() + (size_t)z0 * (size_t)dst_secsize + (size_t)y0 * (size_t)nx + (size_t)x0;
	
	size_t src_gap = src_secsize - (y1-y0) * nx1;
	size_t dst_gap = dst_secsize - (y1-y0) * nx;
	
	for (int i = z0; i < z1; i++) {
		for (int j = y0; j < y1; j++) {
			EMUtil::em_memcpy(dst, src, clipped_row_size);
			src += nx1;
			dst += nx;
		}
		src += src_gap;
		dst += dst_gap;
	}
	
#ifdef EMAN2_USING_CUDA	
	if(block->cudarwdata){
		copy_to_cuda(); // copy back to device as padding is faster on the host
	}
#endif

	update();
	EXITFUNC;
}


void EMData::insert_scaled_sum(EMData *block, const FloatPoint &center,
						   float scale, float mult_factor)
{
	ENTERFUNC;
	float * data = get_data();
	if (get_ndim()==3) {
		// Start by determining the region to operate on
		int xs=(int)floor(block->get_xsize()*scale/2.0);
		int ys=(int)floor(block->get_ysize()*scale/2.0);
		int zs=(int)floor(block->get_zsize()*scale/2.0);
		int x0=(int)center[0]-xs;
		int x1=(int)center[0]+xs;
		int y0=(int)center[1]-ys;
		int y1=(int)center[1]+ys;
		int z0=(int)center[2]-zs;
		int z1=(int)center[2]+zs;

		if (x1<0||y1<0||z1<0||x0>get_xsize()||y0>get_ysize()||z0>get_zsize()) return;	// object is completely outside the target volume

		// make sure we stay inside the volume
		if (x0<0) x0=0;
		if (y0<0) y0=0;
		if (z0<0) z0=0;
		if (x1>=get_xsize()) x1=get_xsize()-1;
		if (y1>=get_ysize()) y1=get_ysize()-1;
		if (z1>=get_zsize()) z1=get_zsize()-1;

		float bx=block->get_xsize()/2.0f;
		float by=block->get_ysize()/2.0f;
		float bz=block->get_zsize()/2.0f;

		size_t idx;
		for (int x=x0; x<=x1; x++) {
			for (int y=y0; y<=y1; y++) {
				for (int z=z0; z<=z1; z++) {
					idx = x + y * nx + (size_t)z * nx * ny;
					if (scale==1) // skip interpolation so it is much faster
						data[idx] +=
						mult_factor*block->sget_value_at((x-center[0])+bx,(y-center[1])+by,(z-center[2])+bz);
					else
						data[idx] +=
						mult_factor*block->sget_value_at_interp((x-center[0])/scale+bx,(y-center[1])/scale+by,(z-center[2])/scale+bz);
					
				}
			}
		}
		update();
	}
	else if (get_ndim()==2) {
		// Start by determining the region to operate on
		int xs=(int)floor(block->get_xsize()*scale/2.0);
		int ys=(int)floor(block->get_ysize()*scale/2.0);
		int x0=(int)center[0]-xs;
		int x1=(int)center[0]+xs;
		int y0=(int)center[1]-ys;
		int y1=(int)center[1]+ys;

		if (x1<0||y1<0||x0>get_xsize()||y0>get_ysize()) return;	// object is completely outside the target volume

		// make sure we stay inside the volume
		if (x0<0) x0=0;
		if (y0<0) y0=0;
		if (x1>=get_xsize()) x1=get_xsize()-1;
		if (y1>=get_ysize()) y1=get_ysize()-1;

		float bx=block->get_xsize()/2.0f;
		float by=block->get_ysize()/2.0f;

		for (int x=x0; x<=x1; x++) {
			for (int y=y0; y<=y1; y++) {
				data[x + y * nx] +=
					mult_factor*block->sget_value_at_interp((x-center[0])/scale+bx,(y-center[1])/scale+by);
			}
		}
		update();
	}
	else {
		LOGERR("insert_scaled_sum supports only 2D and 3D data");
		throw ImageDimensionException("2D/3D only");
	}

	EXITFUNC;
}
// 			else if ( m == 0 )
// 			{
// 				if ( n_f == -ny/2 )
// 				{
// 					t2++;
// // 					continue;
// 					for (int y = 0; y < return_slice->get_ysize(); ++y) {
// 						for (int x = 0; x < return_slice->get_xsize(); ++x) {
// 							double cur_val = return_slice->get_value_at(x,y);
// 							return_slice->set_value_at(x,y,cur_val+dat[idx]*std::pow(-1.0f,y));
// 						}
// 					}
// 					if (phase > 0.01 ) cout << "foo 2 " << phase << " " << amp << " " << dat[idx] << endl;
// 				}
// 				else
// 				{
// 					if ( n_f < 1 ) continue;
// 					t3++;
// 					for (int y = 0; y < return_slice->get_ysize(); ++y) {
// 						for (int x = 0; x < return_slice->get_xsize(); ++x) {
// 							double cur_val = return_slice->get_value_at(x,y);
// 							return_slice->set_value_at(x,y,cur_val+2*amp*cos(ndash*y+phase));
// 						}
// 					}
// 				}
// 			}
// 			else if ( n_f == -ny/2 )
// 			{
// 				if ( m == ((nx-2)/2) )
// 				{
// 					t4++;
// 					for (int y = 0; y < return_slice->get_ysize(); ++y) {
// 						for (int x = 0; x < return_slice->get_xsize(); ++x) {
// 							double cur_val = return_slice->get_value_at(x,y);
// 							return_slice->set_value_at(x,y,cur_val+dat[idx]*std::pow(-1.0f,x+y));
// 						}
// 					}
// 					if (phase > 0.01 ) cout << "foo 4 " << phase << " " << amp << " " << dat[idx] << endl;
// 				}
// 				else
// 				{
// 					t5++;
// 					for (int y = 0; y < return_slice->get_ysize(); ++y) {
// 						for (int x = 0; x < return_slice->get_xsize(); ++x) {
// 							double cur_val = return_slice->get_value_at(x,y);
// 							return_slice->set_value_at(x,y,cur_val+2*amp*cos(mdash*x+phase));
// 						}
// 					}
// 				}
// 			}
// 			else if ( n_f == 0 )
// 			{
// 				if ( m == ((nx-2)/2) )
// 				{
// 					t6++;
// 					for (int y = 0; y < return_slice->get_ysize(); ++y) {
// 						for (int x = 0; x < return_slice->get_xsize(); ++x) {
// 							double cur_val = return_slice->get_value_at(x,y);
// 							return_slice->set_value_at(x,y,cur_val+dat[idx]*std::pow(-1.0f,x));
// 						}
// 					}
// 					if (phase > 0.01 ) cout << "foo 3 " << phase << " " << amp << " " << dat[idx] << endl;
// 				}
// 				else
// 				{
// 					t7++;
// 					for (int y = 0; y < return_slice->get_ysize(); ++y) {
// 						for (int x = 0; x < return_slice->get_xsize(); ++x) {
// 							double cur_val = return_slice->get_value_at(x,y);
// 							return_slice->set_value_at(x,y,cur_val+2*amp*cos(mdash*x+M_PI*y + phase));
// 						}
// 					}
// 				}
// 			}
// 			else if ( m == ((nx-2)/2) )
// 			{
// 				if ( n_f < 1 ) continue;
// 				t8++;
// 				for (int y = 0; y < return_slice->get_ysize(); ++y) {
// 					for (int x = 0; x < return_slice->get_xsize(); ++x) {
// 						double cur_val = return_slice->get_value_at(x,y);
// 						return_slice->set_value_at(x,y,cur_val+2*amp*cos(ndash*y+M_PI*x+phase));
// 					}
// 				}
// 			}
// }
