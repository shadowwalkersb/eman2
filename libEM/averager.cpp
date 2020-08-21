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

#include "averager.h"
#include "emdata.h"
#include "xydata.h"
#include "ctf.h"
#include <cstring>
#include "plugins/averager_template.h"

using namespace EMAN;

const string ImageAverager::NAME = "mean";
const string SigmaAverager::NAME = "sigma";
const string TomoAverager::NAME = "mean.tomo";
const string MinMaxAverager::NAME = "minmax";
const string MedianAverager::NAME = "median";
const string IterAverager::NAME = "iterative";
const string CtfCWautoAverager::NAME = "ctfw.auto";
const string CtfCAutoAverager::NAME = "ctf.auto";
const string CtfWtAverager::NAME = "ctf.weight";
const string CtfWtFiltAverager::NAME = "ctf.weight.autofilt";
const string FourierWeightAverager::NAME = "weightedfourier";
const string LocalWeightAverager::NAME = "localweight";

template <> Factory < Averager >::Factory()
{
	force_add<ImageAverager>();
	force_add<SigmaAverager>();
	force_add<MinMaxAverager>();
	force_add<MedianAverager>();
	force_add<LocalWeightAverager>();
	force_add<IterAverager>();
	force_add<CtfCWautoAverager>();
	force_add<CtfCAutoAverager>();
	force_add<CtfWtAverager>();
	force_add<CtfWtFiltAverager>();
	force_add<TomoAverager>();
	force_add<FourierWeightAverager>();
//	force_add<XYZAverager>();
}

void Averager::mult(const float& s)
{
	if ( result != 0 )
	{
		result->mult(s);
	}
	else throw NullPointerException("Error, attempted to multiply the result image, which is NULL");
}

// pure virtual causing boost issues here, so this is just a dummy method
void Averager::add_image(EMData* image)
{
return;
}

void Averager::add_image_list(const vector<EMData*> & image_list)
{
	for (size_t i = 0; i < image_list.size(); i++) {
		add_image(image_list[i]);
	}
}

TomoAverager::TomoAverager()
	: norm_image(0),nimg(0),overlap(0)
{

}

void TomoAverager::add_image(EMData * image)
{
	if (!image) {
		return;
	}

	if (!image->is_complex()) {
		image=image->do_fft();
		image->set_attr("free_me",(int)1);
	}
		
	if (result!=0 && !EMUtil::is_same_size(image, result)) {
		LOGERR("%s Averager can only process same-size Images",
			   get_name().c_str());
		return;
	}

	int nx = image->get_xsize();
	int ny = image->get_ysize();
	int nz = image->get_zsize();
//	size_t image_size = (size_t)nx * ny * nz;

	if (norm_image == 0) {
//		printf("init average %d %d %d",nx,ny,nz);
		result = image->copy_head();
		result->to_zero();
		
		norm_image = image->copy_head();
		norm_image->to_zero();
		
		thresh_sigma = (float)params.set_default("thresh_sigma", 0.5);
		overlap=0.0f;
		nimg=0;
	}

	float *result_data = result->get_data();
	float *norm_data = norm_image->get_data();
	float *data = image->get_data();
	
	vector<float> threshv;
	threshv=image->calc_radial_dist(nx/2,0,1,4);
	for (int i=0; i<nx/2; i++) threshv[i]*=threshv[i]*thresh_sigma;  // The value here is amplitude, we square to make comparison less expensive
	
	size_t j=0;
	// Add any values above threshold to the result image, and add 1 to the corresponding pixels in the norm image
	int k=0;
	for (int z=0; z<nz; z++) {
		for (int y=0; y<ny; y++) {
			for (int x=0; x<nx; x+=2, j+=2) {
				float rf=Util::hypot3(x/2,y<ny/2?y:ny-y,z<nz/2?z:nz-z);	// origin at 0,0; periodic
				int r=int(rf);
				if (r>ny/2) continue;
				float f=data[j];	// real
				float g=data[j+1];	// imag
				float inten=f*f+g*g;
				
				if (inten<threshv[r]) continue;
				
				k+=1;
				result_data[j]  +=f;
				result_data[j+1]+=g;
				
				norm_data[j]  +=1.0;
				norm_data[j+1]+=1.0;
			}
		}
	}
//	printf("%d %d\n",k,nx*ny*nz);
	overlap+=(float)k/(nx*ny*nz);
	nimg++;
	
	if (image->has_attr("free_me")) delete image;
}

EMData * TomoAverager::finish()
{
	if (norm_image==0 || result==0 || nimg==0) return NULL;
	
	int nx = result->get_xsize();
	int ny = result->get_ysize();
	int nz = result->get_zsize();
	size_t image_size = (size_t)nx * ny * nz;
	
	float *result_data = result->get_data();
	float *norm_data = norm_image->get_data();
	
//	printf("finish average %d %d %d",nx,ny,nz);
	// normalize the average
	for (size_t j = 0; j < image_size; j++) {
		if (norm_data[j]==0.0) result_data[j]=0.0;
		else result_data[j]/=norm_data[j];
	}
	
	norm_image->update();
	result->update();
	
	EMData *ret;
	if ((int)params.set_default("doift", 1))
		ret = result->do_ift();
	else
		ret = result->copy();
	
	ret->set_attr("ptcl_repr",norm_image->get_attr("maximum"));
	ret->set_attr("mean_coverage",(float)(overlap/nimg));
	if ((int)params.set_default("save_norm", 0)) 
		norm_image->write_image("norm.hdf");
	
	if (params.has_key("normout")) {
		EMData *normout=(EMData*) params["normout"];
		normout->set_data(norm_image->copy()->get_data());
		normout->update();
	}
	
	delete result;
	delete norm_image;
	result=0;
	norm_image=0;
	
	return ret;
}


ImageAverager::ImageAverager()
	: sigma_image(0), ignore0(0), normimage(0), freenorm(0), nimg(0)
{

}

void ImageAverager::add_image(EMData * image)
{
	if (!image) {
		return;
	}

	if (nimg >= 1 && !EMUtil::is_same_size(image, result)) {
		LOGERR("%sAverager can only process same-size Image",
			   get_name().c_str());
		return;
	}

	nimg++;

	int nx = image->get_xsize();
	int ny = image->get_ysize();
	int nz = image->get_zsize();
	size_t image_size = (size_t)nx * ny * nz;

	if (nimg == 1) {
		result = image->copy_head();
		result->set_size(nx, ny, nz);
		sigma_image = params.set_default("sigma", (EMData*)0);
		ignore0 = params["ignore0"];

		normimage = params.set_default("normimage", (EMData*)0);
		if (ignore0 && normimage==0) { normimage=new EMData(nx,ny,nz); freenorm=1; }
		if (normimage) normimage->to_zero();
	}

	float *result_data = result->get_data();
	float *sigma_image_data = 0;
	if (sigma_image) {
		sigma_image->set_size(nx, ny, nz);
		sigma_image_data = sigma_image->get_data();
	}

	float * image_data = image->get_data();

	if (!ignore0) {
		for (size_t j = 0; j < image_size; ++j) {
			float f = image_data[j];
			result_data[j] += f;
			if (sigma_image_data) {
				sigma_image_data[j] += f * f;
			}
		}
	}
	else {
		for (size_t j = 0; j < image_size; ++j) {
			float f = image_data[j];
			if (f) {
				result_data[j] += f;
				if (sigma_image_data) {
					sigma_image_data[j] += f * f;
				}
				normimage->set_value_at_fast(j,normimage->get_value_at(j)+1.0);
			}
		}
	}
}

EMData * ImageAverager::finish()
{
	if (result && nimg > 1) {
		size_t image_size = (size_t)result->get_xsize() * result->get_ysize() * result->get_zsize();
		float * result_data = result->get_data();

		if (!ignore0) {
			for (size_t j = 0; j < image_size; ++j) {
				result_data[j] /= nimg;
			}

			if (sigma_image) {
				float * sigma_image_data = sigma_image->get_data();

				for (size_t j = 0; j < image_size; ++j) {
					float f1 = sigma_image_data[j] / nimg;
					float f2 = result_data[j];
					sigma_image_data[j] = sqrt(f1 - f2 * f2);
				}

				sigma_image->update();
			}
		}
		else {
			for (size_t j = 0; j < image_size; ++j) {
				if (normimage->get_value_at(j)>0) result_data[j] /= normimage->get_value_at(j);
			}
			if (sigma_image) {
				float * sigma_image_data = sigma_image->get_data();

				for (size_t j = 0; j < image_size; ++j) {
					float f1 = 0;
					if (normimage->get_value_at(j)>0) f1=sigma_image_data[j] / normimage->get_value_at(j);
					float f2 = result_data[j];
					sigma_image_data[j] = sqrt(f1 - f2 * f2);
				}

				sigma_image->update();
			}
		}

		result->update();

	}		
	result->set_attr("ptcl_repr",nimg);

	if (freenorm) { delete normimage; normimage=(EMData*)0; }

	return result;
}




SigmaAverager::SigmaAverager()
	: mean_image(0), ignore0(0), normimage(0), freenorm(0), nimg(0)
{

}

void SigmaAverager::add_image(EMData * image)
{
	if (!image) {
		return;
	}

	if (nimg >= 1 && !EMUtil::is_same_size(image, mean_image)) {
		LOGERR("%sAverager can only process same-size Image",
			   get_name().c_str());
		return;
	}

	nimg++;

	int nx = image->get_xsize();
	int ny = image->get_ysize();
	int nz = image->get_zsize();
	size_t image_size = (size_t)nx * ny * nz;

	if (nimg == 1) {
		mean_image = image->copy_head();
		mean_image->set_size(nx, ny, nz);

		result = image->copy_head();
		result->set_size(nx, ny, nz);

		ignore0 = params["ignore0"];
		normimage = params.set_default("normimage", (EMData*)0);
		if (ignore0 && normimage==0) { normimage=new EMData(nx,ny,nz); freenorm=1; }
		if (normimage) normimage->to_zero();
	}

	float *mean_image_data = mean_image->get_data();
	float *result_data = result->get_data();
	float * image_data = image->get_data();

	if (!ignore0) {
		for (size_t j = 0; j < image_size; ++j) {
			float f = image_data[j];
			mean_image_data[j] += f;
			if (result_data) {
				result_data[j] += f * f;
			}
		}
	}
	else {
		for (size_t j = 0; j < image_size; ++j) {
			float f = image_data[j];
			if (f) {
				mean_image_data[j] += f;
				if (result_data) {
					result_data[j] += f * f;
				}
				normimage->set_value_at_fast(j,normimage->get_value_at(j)+1.0);
			}
		}
	}
}

EMData * SigmaAverager::finish()
{
	if (mean_image && nimg > 1) {
		size_t image_size = (size_t)mean_image->get_xsize() * mean_image->get_ysize() * mean_image->get_zsize();
		float * mean_image_data = mean_image->get_data();
		if (!ignore0) {
			for (size_t j = 0; j < image_size; ++j) {
				mean_image_data[j] /= nimg;
			}

			float * result_data = result->get_data();
			
			for (size_t j = 0; j < image_size; ++j) {
				float f1 = result_data[j] / nimg;
				float f2 = mean_image_data[j];
				result_data[j] = sqrt(f1 - f2 * f2);
			}

			result->update();
		}
		else {
			for (size_t j = 0; j < image_size; ++j) {
				if (normimage->get_value_at(j)>0) mean_image_data[j] /= normimage->get_value_at(j);
			}

			float * result_data = result->get_data();

			for (size_t j = 0; j < image_size; ++j) {
				float f1 = 0;
				if (normimage->get_value_at(j)>0) f1=result_data[j] / normimage->get_value_at(j);
				float f2 = mean_image_data[j];
				result_data[j] = sqrt(f1 - f2 * f2);
			
				result->update();
			}
		}

		mean_image->update();
		mean_image->set_attr("ptcl_repr",nimg);

		result->set_attr("ptcl_repr",nimg);

		if (freenorm) { delete normimage; normimage=(EMData*)0; }

		return result;
	}
	else {
		LOGERR("%sAverager requires >=2 images", get_name().c_str());
	}
}

FourierWeightAverager::FourierWeightAverager()
	: normimage(0), freenorm(0), nimg(0)
{

}

void FourierWeightAverager::add_image(EMData * image)
{
	if (!image) {
		return;
	}



	EMData *img=image->do_fft();
	if (nimg >= 1 && !EMUtil::is_same_size(img, result)) {
		LOGERR("%sAverager can only process same-size Image",
			   get_name().c_str());
		return;
	}
	
	nimg++;

	int nx = img->get_xsize();
	int ny = img->get_ysize();
	int nz = 1;
//	size_t image_size = (size_t)nx * ny * nz;

	XYData *weight=(XYData *)image->get_attr("avg_weight");
	
	if (nimg == 1) {
		result = new EMData(nx,ny,nz);
		result->set_complex(true);
		result->to_zero();

		normimage = params.set_default("normimage", (EMData*)0);
		if (normimage==0) { normimage=new EMData(nx/2,ny,nz); freenorm=1; }
		normimage->to_zero();
	}

	// We're using routines that handle complex image wraparound for us, so we iterate over the half-plane
	for (int y=-ny/2; y<ny/2; y++) {
		for (int x=0; x<nx/2; x++) {
			std::complex<float> v=img->get_complex_at(x,y);
			float r=Util::hypot2(y/(float)ny,x/(float)nx);
			float wt=weight->get_yatx(r);
			result->set_complex_at(x,y,result->get_complex_at(x,y)+v*wt);
			normimage->set_value_at(x,y+ny/2,normimage->get_value_at(x,y+ny/2)+wt);
		}
	}

	delete img;
}

EMData * FourierWeightAverager::finish()
{
	EMData *ret = (EMData *)0;
	
	if (result && nimg >= 1) {
	// We're using routines that handle complex image wraparound for us, so we iterate over the half-plane
		int nx = result->get_xsize();
		int ny = result->get_ysize();
		
		for (int y=-ny/2; y<ny/2; y++) {
			for (int x=0; x<nx/2; x++) {
				float norm=normimage->get_value_at(x,y+ny/2);
				if (norm<=0) result->set_complex_at(x,y,0.0f);
				else result->set_complex_at(x,y,result->get_complex_at(x,y)/norm);
			}
		}

		result->update();
//		result->mult(1.0f/(float)result->get_attr("sigma"));
//		result->write_image("tmp.hdf",0);
//		printf("%g %g %g\n",(float)result->get_attr("sigma"),(float)result->get_attr("minimum"),(float)result->get_attr("maximum"));
		ret=result->do_ift();
		delete result;
		result=(EMData*) 0;
	}
	ret->set_attr("ptcl_repr",nimg);

	if (freenorm) { delete normimage; normimage=(EMData*)0; }
	nimg=0;

	return ret;
}

LocalWeightAverager::LocalWeightAverager()
	: normimage(0), freenorm(0), nimg(0),fourier(0)
{

}

void LocalWeightAverager::add_image(EMData * image)
{
	if (!image) {
		return;
	}
	
	nimg++;

	int nx = image->get_xsize();
	int ny = image->get_ysize();
	int nz = image->get_zsize();

	fourier = params.set_default("fourier", (int)0);
	if (nimg == 1) {
		result = image->copy_head();
		result->set_size(nx, ny, nz);
		result->to_zero();

		
		normimage = params.set_default("normimage", (EMData*)0);
		if (normimage==0) { normimage=new EMData(nx,ny,nz); freenorm=1; }
		normimage->to_zero();
		normimage->add(0.0000001f);
	}

	images.push_back(image->copy());
}

EMData * LocalWeightAverager::finish()
{
	if (nimg==0) return nullptr;
	
	int nx = images.front()->get_xsize();
	int ny = images.front()->get_ysize();
	int nz = images.front()->get_zsize();
	
	float dampnoise = params.set_default("dampnoise", (float)0.5);
	
	// This is the standard mode where local real-space correlation with the average is used to define a local weight (like a mask)
	// applied to each image. If fourier>=2 then the same is done, but in "gaussian bands" in Fourier space
	if (fourier<=1) {
		auto stg1 = std::make_unique<EMData>(nx,ny,nz);
		
		for (auto & image : images) stg1->add(*image);
		stg1->process_inplace("normalize");
		
	//	std::vector<EMData*> weights;
		for (auto & image : images) {
			EMData *imc=image->copy();
			imc->mult(*stg1);
			imc->process_inplace("filter.lowpass.gauss",Dict("cutoff_freq",0.02f));
			imc->process_inplace("threshold.belowtozero",Dict("minval",0.0f));
	//		imc->process_inplace("math.sqrt");
	//		imc->process_inplace("math.pow",Dict("pow",0.25));
			image->mult(*imc);
			result->add(*image);
			normimage->add(*imc);
			delete imc;
			delete image;
		}
		
		if (dampnoise>0) {
			float mean=normimage->get_attr("mean");
			float max=normimage->get_attr("maximum");
			normimage->process_inplace("threshold.clampminmax",Dict("minval",mean*dampnoise,"maxval",max));
		}
		
		result->div(*normimage);
		
		result->set_attr("ptcl_repr",nimg);
		
		if (freenorm) { delete normimage; normimage=(EMData*)0; }
		nimg=0;

		return result;
	}
	else if (fourier<=ny/2) {
		// we do pretty much the same thing as above, but one Fourier "band" at a time
		
		for (int r=0;  r<fourier; r++) {
			float cen=r/((float)fourier-1.0)*0.5;
			float sig=(0.5/fourier)/(2.0*sqrt(log(2.0)));
			std::vector<EMData*> filt;

			EMData *stg1 = new EMData(nx,ny,nz);
			for (auto & image : images) {
				EMData *f=image->process("filter.bandpass.gauss",Dict("center",(float)cen,"sigma",sig));
				filt.push_back(f);
				stg1->add(*f);
				if (r==fourier-1) delete image;		// we don't actually need the unfiltered images again
			}
			stg1->process_inplace("normalize");
			stg1->process("filter.bandpass.gauss",Dict("center",(float)cen,"sigma",sig));
//			stg1->write_image("cmp.hdf",r);
			
		//	std::vector<EMData*> weights;
			int imn=1;
			for (auto & im : filt) {
				EMData *imc=im->copy();
				imc->mult(*stg1);
				imc->process_inplace("filter.lowpass.gauss",Dict("cutoff_freq",0.02f));
				imc->process_inplace("threshold.belowtozero",Dict("minval",0.0f));
//				imc->write_image("cmp.hdf",imn*fourier+r);
		//		imc->process_inplace("math.sqrt");
		//		imc->process_inplace("math.pow",Dict("pow",0.25));
				im->mult(*imc);
				result->add(*im);
				normimage->add(*imc);
				delete im;
				delete imc;
				imn++;
			}
			
			if (dampnoise>0) {
				float mean=normimage->get_attr("mean");
				float max=normimage->get_attr("maximum");
				normimage->process_inplace("threshold.clampminmax",Dict("minval",mean*dampnoise,"maxval",max));
			}
			
		}
		result->div(*normimage);
		result->set_attr("ptcl_repr",nimg);
		
		if (freenorm) { delete normimage; normimage=(EMData*)0; }
		nimg=0;
		return result;
	}
	
}

void IterAverager::add_image(EMData * image)
{
	if (!image) return;
	
	images.push_back(image->do_fft());
}

EMData *IterAverager::finish()
{
	if (images.empty()) return nullptr;
	
	int nx = images.front()->get_xsize();
	int ny = images.front()->get_ysize();
	int nz = images.front()->get_zsize();
	
	if (nz!=1) throw ImageDimensionException("IterAverager is for 2-D images only");
	
	delete result;
	result=new EMData(nx-2,ny,nz,0);
	result -> to_zero();
	
	auto tmp = std::make_unique<EMData>(nx-2,ny,nz,0);
	tmp -> to_zero();

	for (int it=0; it<4; it++) {
		for (int y=-ny/2+1; y<ny/2-1; y++) {
			for (int x=0; x<nx-2; x++) {
				std::complex<double> nv=0;
				// put the vector on the inside, then we can accumulate into a double easily
				for (auto im=images.begin(); im<images.end(); im++)
					for (int yy=y-1; yy<=y+1; yy++)
						for (int xx=x-1; xx<=x+1; xx++)
							nv+=(*im)->get_complex_at(xx,yy)+tmp->get_complex_at(x,y)-tmp->get_complex_at(xx,yy);
				result->set_complex_at(x,y,std::complex<float>(nv/(9.0*images.size())));
			}
		}
		// Swap the pointers
		result->write_image("dbug.hdf",-1);
		auto swp=tmp.get();
		tmp.reset(result);
		result=swp;
	}
	
	delete result;
	result=nullptr;
	for (auto im=images.begin(); im<images.end(); ++im) delete (*im);
	images.clear();
	result=tmp->do_ift();
	return result;
}


#if 0
EMData *ImageAverager::average(const vector < EMData * >&image_list) const
{
	if (image_list.size() == 0) {
		return 0;
	}

	EMData *sigma_image = params["sigma"];
	int ignore0 = params["ignore0"];

	EMData *image0 = image_list[0];

	int nx = image0->get_xsize();
	int ny = image0->get_ysize();
	int nz = image0->get_zsize();
	size_t image_size = (size_t)nx * ny * nz;

	EMData *result = new EMData();
	result->set_size(nx, ny, nz);

	float *result_data = result->get_data();
	float *sigma_image_data = 0;

	if (sigma_image) {
		sigma_image->set_size(nx, ny, nz);
		sigma_image_data = sigma_image->get_data();
	}

	int c = 1;
	if (ignore0) {
		for (size_t j = 0; j < image_size; ++j) {
			int g = 0;
			for (size_t i = 0; i < image_list.size(); i++) {
				float f = image_list[i]->get_value_at(j);
				if (f) {
					g++;
					result_data[j] += f;
					if (sigma_image_data) {
						sigma_image_data[j] += f * f;
					}
				}
			}
			if (g) {
				result_data[j] /= g;
			}
		}
	}
	else {
		float *image0_data = image0->get_data();
		if (sigma_image_data) {
			memcpy(sigma_image_data, image0_data, image_size * sizeof(float));

			for (size_t j = 0; j < image_size; ++j) {
				sigma_image_data[j] *= sigma_image_data[j];
			}
		}

		image0->update();
		memcpy(result_data, image0_data, image_size * sizeof(float));

		for (size_t i = 1; i < image_list.size(); i++) {
			EMData *image = image_list[i];

			if (EMUtil::is_same_size(image, result)) {
				float *image_data = image->get_data();

				for (size_t j = 0; j < image_size; ++j) {
					result_data[j] += image_data[j];
				}

				if (sigma_image_data) {
					for (size_t j = 0; j < image_size; ++j) {
						sigma_image_data[j] += image_data[j] * image_data[j];
					}
				}

				image->update();
				c++;
			}
		}

		for (size_t j = 0; j < image_size; ++j) {
			result_data[j] /= static_cast < float >(c);
		}
	}

	if (sigma_image_data) {
		for (size_t j = 0; j < image_size; ++j) {
			float f1 = sigma_image_data[j] / c;
			float f2 = result_data[j];
			sigma_image_data[j] = sqrt(f1 - f2 * f2);
		}
	}

	if (sigma_image_data) {
		sigma_image->update();
	}

	result->update();
	return result;
}
#endif

MinMaxAverager::MinMaxAverager()
	: nimg(0),ismax(0),isabs(0)
{
	
}

void MinMaxAverager::add_image(EMData * image)
{
	if (!image) {
		return;
	}

	if (nimg >= 1 && !EMUtil::is_same_size(image, result)) {
		LOGERR("%sAverager can only process same-size Image",
			   get_name().c_str());
		return;
	}
	EMData *owner = params.set_default("owner", (EMData*)0);

	float thisown = image->get_attr_default("ortid",(float)nimg);
	nimg++;

	size_t nxyz = image->get_size();
	
	if (nimg == 1) {
		result = image->copy();
		if (owner) owner->to_value(thisown);
		return;
	}

	float *rdata = result->get_data();
	float *data = image->get_data();
	float *owndata = 0;
	if (owner) owndata=owner->get_data();

	ismax=(int)params.set_default("max",0);
	isabs=(int)params.set_default("abs",0);
	
	
	for (size_t i=0; i<nxyz; i++) {
		float v = isabs?fabs(data[i]):data[i];
		float rv = isabs?fabs(rdata[i]):rdata[i];
		if ((ismax && v>rv) || (!ismax && v<rv)) {
			rdata[i]=data[i];
			if (owndata) owndata[i]=thisown;
		}
	}

}

EMData *MinMaxAverager::finish()
{
	result->update();
	result->set_attr("ptcl_repr",nimg);
	
	if (result && nimg >= 1) return result;

	return nullptr;
}

MedianAverager::MedianAverager()
= default;

void MedianAverager::add_image(EMData * image)
{
	if (!image) {
		return;
	}

	if (!imgs.empty() && !EMUtil::is_same_size(image, imgs[0])) {
		LOGERR("MedianAverager can only process images of the same size");
		return;
	}

	imgs.push_back(image->copy());
}

EMData *MedianAverager::finish()
{
	if (imgs.empty()) return 0;
	EMData *ret=nullptr;
	
	if (imgs.size()==1) {
		ret=imgs[0];
		imgs.clear();
		return ret;
	}
	
	// special case for n==2
	if (imgs.size()==2) {
		imgs[0]->add(*imgs[1]);
		imgs[0]->mult(0.5f);
		delete imgs[1];
		ret=imgs[0];
		imgs.clear();
		return ret;
	}

	int nx=imgs[0]->get_xsize();
	int ny=imgs[0]->get_ysize();
	int nz=imgs[0]->get_zsize();
	
	// special case for n==3
	if (imgs.size()==3) {
		for (int z=0; z<nz; z++) {
			for (int y=0; y<ny; y++) {
				for (int x=0; x<nx; x++) {
					float v0=imgs[0]->get_value_at(x,y,z);
					float v1=imgs[1]->get_value_at(x,y,z);
					float v2=imgs[2]->get_value_at(x,y,z);
					
					if (v0<=v1) {
						if (v0>=v2) continue;
						if (v1<=v2) imgs[0]->set_value_at(x,y,z,v1);
						else imgs[0]->set_value_at(x,y,z,v2);
					}
					else {
						if (v0<=v2) continue;
						if (v2<=v1) imgs[0]->set_value_at(x,y,z,v1);
						else imgs[0]->set_value_at(x,y,z,v2);
					}
				}
			}
		}
		
		delete imgs[1];
		delete imgs[2];
		ret=imgs[0];
		imgs.clear();
		return ret;
	}

	ret=imgs[0]->copy();
	std::vector<float> vals(imgs.size(),0.0f);
	
	
	for (int z=0; z<nz; z++) {
		for (int y=0; y<ny; y++) {
			for (int x=0; x<nx; x++) {
				int i=0;
				for (auto it = imgs.begin() ; it != imgs.end(); ++it,++i) {
					vals[i]=(*it)->get_value_at(x,y,z);
				}
					
				std::sort(vals.begin(),vals.end());
				//printf("%d %d %d    %d\n",x,y,z,vals.size());
				if (vals.size()&1) ret->set_value_at(x,y,z,vals[vals.size()/2]);		// for even sizes, not quite right, and should include possibility of local average
				else ret->set_value_at(x,y,z,(vals[vals.size()/2]+vals[vals.size()/2-1])/2.0f);
			}
		}
	}

	if (!imgs.empty()) {
		for (auto & img : imgs) if (img) delete img;
		imgs.clear();
	}


	return ret;
}

CtfCWautoAverager::CtfCWautoAverager()
	: nimg(0)
{

}


void CtfCWautoAverager::add_image(EMData * image)
{
	if (!image)
		return;

	EMData *fft=image->do_fft();

	if (nimg >= 1 && !EMUtil::is_same_size(fft, result)) {
		LOGERR("%s Averager can only process images of the same size", get_name().c_str());
		return;
	}

	nimg++;
	if (nimg == 1) {
		result = fft->copy_head();
		result->to_zero();
	}

	Ctf *ctf = (Ctf *)image->get_attr("ctf");
//string cc=ctf->to_string();
//FILE *out=fopen("ctf.txt","a");
//fprintf(out,"%s\n",cc.c_str());
//fclose(out);
	float b=ctf->bfactor;
	ctf->bfactor=100.0;			// FIXME - this is a temporary fixed B-factor which does a (very) little sharpening

//	if (nimg==1) unlink("snr.hdf");

	EMData *snr = result -> copy();
	ctf->compute_2d_complex(snr,Ctf::CTF_SNR);
//	snr->write_image("snr.hdf",-1);
	EMData *ctfi = result-> copy();
	ctf->compute_2d_complex(ctfi,Ctf::CTF_AMP);

	ctf->bfactor=b;	// return to its original value

	float *outd = result->get_data();
	float *ind = fft->get_data();
	float *snrd = snr->get_data();
	float *ctfd = ctfi->get_data();

	size_t sz=snr->get_xsize()*snr->get_ysize();
	for (size_t i = 0; i < sz; i+=2) {
		if (snrd[i]<0) snrd[i]=0.001;	// Used to be 0. See ctfcauto averager
		ctfd[i]=fabs(ctfd[i]);
		if (ctfd[i]<.05) ctfd[i]=0.05f;
//		{
//			if (snrd[i]<=0) ctfd[i]=.05f;
//			else ctfd[i]=snrd[i]*10.0f;
//		}
		outd[i]+=ind[i]*snrd[i]/ctfd[i];
		outd[i+1]+=ind[i+1]*snrd[i]/ctfd[i];
	}

	if (nimg==1) {
		snrsum=snr->copy_head();
		float *ssnrd=snrsum->get_data();
		// we're only using the real component, and we need to start with 1.0
		for (size_t i = 0; i < sz; i+=2) { ssnrd[i]=1.0; ssnrd[i+1]=0.0; }
	}
//	snr->write_image("snr.hdf",-1);
	snr->process_inplace("math.absvalue");
	snrsum->add(*snr);

	delete ctf;
	delete fft;
	delete snr;
	delete ctfi;
}

EMData * CtfCWautoAverager::finish()
{
/*	EMData *tmp=result->do_ift();
	tmp->write_image("ctfcw.hdf",0);
	delete tmp;

	tmp=snrsum->do_ift();
	tmp->write_image("ctfcw.hdf",1);
	delete tmp;*/

//snrsum->write_image("snrsum.hdf",-1);
	//size_t sz=result->get_xsize()*result->get_ysize();
	int nx=result->get_xsize();
	int ny=result->get_ysize();	
	float *snrsd=snrsum->get_data();
	float *outd=result->get_data();

	int rm=(ny-2)*(ny-2)/4;
	for (int j=0; j<ny; j++) {
		for (int i=0; i<nx; i+=2) {
			size_t ii=i+j*nx;
			if ((j<ny/2 && i*i/4+j*j>rm) ||(j>=ny/2 && i*i/4+(ny-j)*(ny-j)>rm) || snrsd[ii]==0) { outd[ii]=outd[ii+1]=0; continue; }
			outd[ii]/=snrsd[ii];		// snrsd contains total SNR
			outd[ii+1]/=snrsd[ii];
		}
	}

	result->update();
	result->set_attr("ptcl_repr",nimg);
	result->set_attr("ctf_snr_total",snrsum->calc_radial_dist(snrsum->get_ysize()/2,0,1,false));
	result->set_attr("ctf_wiener_filtered",1);
	
	delete snrsum;
	EMData *ret=result->do_ift();
	delete result;
	result=nullptr;
	return ret;
}

CtfCAutoAverager::CtfCAutoAverager()
	: nimg(0)
{

}


void CtfCAutoAverager::add_image(EMData * image)
{
	if (!image)
		return;

	EMData *fft=image->do_fft();

	if (nimg >= 1 && !EMUtil::is_same_size(fft, result)) {
		LOGERR("%s Averager can only process images of the same size", get_name().c_str());
		return;
	}

	nimg++;
	if (nimg == 1) {
		result = fft->copy_head();
		result->to_zero();
	}

	Ctf *ctf = (Ctf *)image->get_attr("ctf");
	float b=ctf->bfactor;
	ctf->bfactor=0;			// NO B-FACTOR CORRECTION !

	EMData *snr = result -> copy();
	ctf->compute_2d_complex(snr,Ctf::CTF_SNR);
	EMData *ctfi = result-> copy();
	ctf->compute_2d_complex(ctfi,Ctf::CTF_AMP);

	ctf->bfactor=b;	// return to its original value

	float *outd = result->get_data();
	float *ind = fft->get_data();
	float *snrd = snr->get_data();
	float *ctfd = ctfi->get_data();

	size_t sz=snr->get_xsize()*snr->get_ysize();
	for (size_t i = 0; i < sz; i+=2) {
		if (snrd[i]<=0) snrd[i]=0.001;		// used to be 0. Trying to insure that there is always at least a little signal used. In cases with dense particles, SNR may be dramatically underestimated
		ctfd[i]=fabs(ctfd[i]);
		
		// This limits the maximum possible amplification in CTF correction to 10x
		if (ctfd[i]<.05)  ctfd[i]=0.05f;
//		{
//			if (snrd[i]<=0) ctfd[i]=.05f;
//			else ctfd[i]=snrd[i]*10.0f;
//		}
		
		// SNR weight and CTF correction
		outd[i]+=ind[i]*snrd[i]/ctfd[i];
		outd[i+1]+=ind[i+1]*snrd[i]/ctfd[i];
	}

	if (nimg==1) {
		snrsum=snr->copy_head();
		float *ssnrd=snrsum->get_data();
		// we're only using the real component, for Wiener filter we put 1.0 in R, but for just SNR weight we use 0
		for (size_t i = 0; i < sz; i+=2) { ssnrd[i]=0.0; ssnrd[i+1]=0.0; }
	}
	snr->process_inplace("math.absvalue");
	snrsum->add(*snr);

	delete ctf;
	delete fft;
	delete snr;
	delete ctfi;
}

EMData * CtfCAutoAverager::finish()
{
/*	EMData *tmp=result->do_ift();
	tmp->write_image("ctfcw.hdf",0);
	delete tmp;

	tmp=snrsum->do_ift();
	tmp->write_image("ctfcw.hdf",1);
	delete tmp;*/

//	snrsum->write_image("snrsum.hdf",-1);
	//size_t sz=result->get_xsize()*result->get_ysize();
	int nx=result->get_xsize();
	int ny=result->get_ysize();	
	float *snrsd=snrsum->get_data();
	float *outd=result->get_data();

	int rm=(ny-2)*(ny-2)/4;
	for (int j=0; j<ny; j++) {
		for (int i=0; i<nx; i+=2) {
			size_t ii=i+j*nx;
			if ((j<ny/2 && i*i/4+j*j>rm) ||(j>=ny/2 && i*i/4+(ny-j)*(ny-j)>rm) || snrsd[ii]==0) { outd[ii]=outd[ii+1]=0; continue; }
			// we aren't wiener filtering, but if the total SNR is too low, we don't want TOO much exaggeration of noise
			if (snrsd[ii]<.05) {		
				outd[ii]*=20.0;		// 1/0.05
				outd[ii+1]*=20.0;
			}
			else {
				outd[ii]/=snrsd[ii];		// snrsd contains total SNR
				outd[ii+1]/=snrsd[ii];
			}
		}
	}
	result->update();
	result->set_attr("ptcl_repr",nimg);
	result->set_attr("ctf_snr_total",snrsum->calc_radial_dist(snrsum->get_ysize()/2,0,1,false));
	result->set_attr("ctf_wiener_filtered",0);
	
/*	snrsum->write_image("snr.hdf",-1);
	result->write_image("avg.hdf",-1);*/
	
	delete snrsum;
	EMData *ret=result->do_ift();
	delete result;
	result=NULL;
	return ret;
}

CtfWtAverager::CtfWtAverager()
	: nimg(0)
{

}


void CtfWtAverager::add_image(EMData * image)
{
	if (!image) {
		return;
	}



	EMData *fft=image->do_fft();

	if (nimg >= 1 && !EMUtil::is_same_size(fft, result)) {
		LOGERR("%s Averager can only process images of the same size", get_name().c_str());
		return;
	}

	nimg++;
	if (nimg == 1) {
		result = fft->copy_head();
		result->to_zero();
	}

	Ctf *ctf = (Ctf *)image->get_attr("ctf");

	EMData *ctfi = result-> copy();
	float b=ctf->bfactor;
	ctf->bfactor=0;		// no B-factor used in weight
	ctf->compute_2d_complex(ctfi,Ctf::CTF_INTEN);
	ctf->bfactor=b;	// return to its original value

	float *outd = result->get_data();
	float *ind = fft->get_data();
	float *ctfd = ctfi->get_data();

	size_t sz=ctfi->get_xsize()*ctfi->get_ysize();
	for (size_t i = 0; i < sz; i+=2) {
		
		// CTF weight
		outd[i]+=ind[i]*ctfd[i];
		outd[i+1]+=ind[i+1]*ctfd[i];
	}

	if (nimg==1) {
		ctfsum=ctfi->copy_head();
		ctfsum->to_zero();
	}
	ctfsum->add(*ctfi);

	delete ctf;
	delete fft;
	delete ctfi;
}

EMData * CtfWtAverager::finish()
{
	int nx=result->get_xsize();
	int ny=result->get_ysize();	
	float *ctfsd=ctfsum->get_data();
	float *outd=result->get_data();

	for (int j=0; j<ny; j++) {
		for (int i=0; i<nx; i+=2) {
			size_t ii=i+j*nx;
			outd[ii]/=ctfsd[ii];		// snrsd contains total SNR
			outd[ii+1]/=ctfsd[ii];
		}
	}
	result->update();
	result->set_attr("ptcl_repr",nimg);
//	result->set_attr("ctf_total",ctfsum->calc_radial_dist(ctfsum->get_ysize()/2,0,1,false));
	result->set_attr("ctf_wiener_filtered",0);
	
/*	snrsum->write_image("snr.hdf",-1);
	result->write_image("avg.hdf",-1);*/
	
	delete ctfsum;
	EMData *ret=result->do_ift();
	delete result;
	result=NULL;
	return ret;
}

CtfWtFiltAverager::CtfWtFiltAverager()
{
	nimg[0]=0;
	nimg[1]=0;
	eo=-1;
}


void CtfWtFiltAverager::add_image(EMData * image)
{
	if (!image) {
		return;
	}



	EMData *fft=image->do_fft();

	if (nimg[0] >= 1 && !EMUtil::is_same_size(fft, results[0])) {
		LOGERR("%s Averager can only process images of the same size", get_name().c_str());
		return;
	}

	if (eo==-1) {
		results[0] = fft->copy_head();
		results[0]->to_zero();
		results[1] = fft->copy_head();
		results[1]->to_zero();
		eo=1;
	}

	eo^=1;
	nimg[eo]++;

	
	EMData *ctfi = results[0]-> copy();
	if (image->has_attr("ctf")) {
		Ctf *ctf = (Ctf *)image->get_attr("ctf");

		float b=ctf->bfactor;
		ctf->bfactor=0;		// no B-factor used in weight, not strictly threadsafe, but shouldn't be a problem
		ctf->compute_2d_complex(ctfi,Ctf::CTF_INTEN);
		ctf->bfactor=b;	// return to its original value
		delete ctf;
	}
	else {
		ctfi->to_one();
	}
		
	float *outd = results[eo]->get_data();
	float *ind = fft->get_data();
	float *ctfd = ctfi->get_data();

	size_t sz=ctfi->get_xsize()*ctfi->get_ysize();
	for (size_t i = 0; i < sz; i+=2) {
		
		// CTF weight
		outd[i]+=ind[i]*ctfd[i];
		outd[i+1]+=ind[i+1]*ctfd[i];
	}

	if (nimg[eo]==1) {
		ctfsum[eo]=ctfi->copy_head();
		ctfsum[eo]->to_zero();
		ctfsum[eo]->add(0.1);		// we start with a value of 0.1 rather than zero to empirically help with situations where the data is incomplete
	}
	ctfsum[eo]->add(*ctfi);

	delete fft;
	delete ctfi;
}

EMData * CtfWtFiltAverager::finish()
{
	if (nimg[0]==0 && nimg[1]==0) return NULL;	// no images
	// Only a single image, so we just return it. No way to filter
	if (nimg[1]==0) {
		EMData *ret=results[0]->do_ift();
		delete results[0];
		delete results[1];
		delete ctfsum[0];
		return ret;
	}

	int nx=results[0]->get_xsize();
	int ny=results[0]->get_ysize();

	for (int k=0; k<2; k++) {
		float *outd=results[k]->get_data();
		float *ctfsd=ctfsum[k]->get_data();
		for (int j=0; j<ny; j++) {
			for (int i=0; i<nx; i+=2) {
				size_t ii=i+j*nx;
				outd[ii]/=ctfsd[ii];
				outd[ii+1]/=ctfsd[ii];
			}
		}
		results[k]->update();
	//	result->set_attr("ctf_total",ctfsum->calc_radial_dist(ctfsum->get_ysize()/2,0,1,false));
		results[0]->set_attr("ctf_wiener_filtered",1);
	}
	
	// compute the Wiener filter from the FSC
	std::vector<float> fsc=results[0]->calc_fourier_shell_correlation(results[1]);
	int third=fsc.size()/3;
	for (int i=third; i<third*2; i++) {
		if (fsc[i]>=.9999) fsc[i]=.9999;
		if (fsc[i]<.001) fsc[i]=.001;
		float snr=2.0*fsc[i]/(1.0-fsc[i]);		// convert the FSC to SNR and multiply by 2
		fsc[i]=snr/(snr+1.0);					// to give us the FSC of the combined average, which is also a Wiener filter (depending on whether SNR is squared)
	}
	
	
	results[0]->add(*results[1]);
	
	float c;
	for (int j=-ny/2; j<ny/2; j++) {
		for (int i=0; i<nx/2; i++) {
			int r=(int)Util::hypot_fast(i,j);
			if (r>=third) c=0.0;
			else c=fsc[third+r];
			results[0]->set_complex_at(i,j,results[0]->get_complex_at(i,j)*c);
		}
	}
	
	EMData *ret=results[0]->do_ift();
	ret->set_attr("ptcl_repr",nimg[0]+nimg[1]);
	
/*	snrsum->write_image("snr.hdf",-1);
	result->write_image("avg.hdf",-1);*/
	
	delete ctfsum[0];
	delete ctfsum[1];
	delete results[0];
	delete results[1];
	results[0]=results[1]=NULL;
	return ret;
}


#if 0
EMData *IterationAverager::average(const vector < EMData * >&image_list) const
{
	if (image_list.size() == 0) {
		return 0;
	}

	EMData *image0 = image_list[0];

	int nx = image0->get_xsize();
	int ny = image0->get_ysize();
	int nz = image0->get_zsize();
	size_t image_size = (size_t)nx * ny * nz;

	EMData *result = new EMData();
	result->set_size(nx, ny, nz);

	EMData *sigma_image = new EMData();
	sigma_image->set_size(nx, ny, nz);

	float *image0_data = image0->get_data();
	float *result_data = result->get_data();
	float *sigma_image_data = sigma_image->get_data();

	memcpy(result_data, image0_data, image_size * sizeof(float));
	memcpy(sigma_image_data, image0_data, image_size * sizeof(float));

	for (size_t j = 0; j < image_size; ++j) {
		sigma_image_data[j] *= sigma_image_data[j];
	}

	image0->update();

	int nc = 1;
	for (size_t i = 1; i < image_list.size(); i++) {
		EMData *image = image_list[i];

		if (EMUtil::is_same_size(image, result)) {
			float *image_data = image->get_data();

			for (size_t j = 0; j < image_size; j++) {
				result_data[j] += image_data[j];
				sigma_image_data[j] += image_data[j] * image_data[j];
			}

			image->update();
			nc++;
		}
	}

	float c = static_cast < float >(nc);
	for (size_t j = 0; j < image_size; ++j) {
		float f1 = sigma_image_data[j] / c;
		float f2 = result_data[j] / c;
		sigma_image_data[j] = sqrt(f1 - f2 * f2) / sqrt(c);
	}


	for (size_t j = 0; j < image_size; ++j) {
		result_data[j] /= c;
	}

	result->update();
	sigma_image->update();

	result->append_image("iter.hed");

	float sigma = sigma_image->get_attr("sigma");
	float *sigma_image_data2 = sigma_image->get_data();
	float *result_data2 = result->get_data();
	float *d2 = new float[nx * ny];
	size_t sec_size = nx * ny * sizeof(float);

	memcpy(d2, result_data2, sec_size);
	memcpy(sigma_image_data2, result_data2, sec_size);

	printf("Iter sigma=%f\n", sigma);

	for (int k = 0; k < 1000; k++) {
		for (int i = 1; i < nx - 1; i++) {
			for (int j = 1; j < ny - 1; j++) {
				int l = i + j * nx;
				float c1 = (d2[l - 1] + d2[l + 1] + d2[l - nx] + d2[l + nx]) / 4.0f - d2[l];
				float c2 = fabs(result_data2[l] - sigma_image_data2[l]) / sigma;
				result_data2[l] += c1 * Util::eman_erfc(c2) / 100.0f;
			}
		}

		memcpy(d2, result_data2, sec_size);
	}

	if( d2 )
	{
		delete[]d2;
		d2 = 0;
	}

	sigma_image->update();
	if( sigma_image )
	{
		delete sigma_image;
		sigma_image = 0;
	}

	result->update();
	result->append_image("iter.hed");

	return result;
}
#endif




void EMAN::dump_averagers()
{
	dump_factory < Averager > ();
}

map<string, vector<string> > EMAN::dump_averagers_list()
{
	return dump_factory_list < Averager > ();
}
