/*
 * Author: tunay.durmaz@bcm.edu, 08/15/2020
 * Copyright (c) 2020- Baylor College of Medicine
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

#include "eerio.h"

#include <tiffio.h>

using namespace EMAN;

//            cout<<"EerFrame: "<<count<<endl;
//            count++;
	cout<<"num_strips: "<<num_strips<<endl;
//                cout<<"Strip size: "<<i<<endl;
		cout<<"Strip size: "<<strip_sizes[i]<<" read..."<<endl;
//                auto strip_size = TIFFRawStripSize(tiff, i);
	EerStream<uint64_t> is(reinterpret_cast<uint64_t*>(data.data()));
//			cout<<"data.size(): "<<data.size()<<" "<<data.size()*sizeof(unsigned char )/sizeof(uint64_t)<<endl;
//			std::ofstream fdata("fdata.out");
//			for(auto &d : data)
//				fdata<<d<<endl;

	Pos pos(0, 0);
	unsigned count = 0;
	std::ofstream fout("eer.out");
	do {
		pos = is.real_pos();
		coords.push_back(pos);
		fout<<pos<<endl;
//			} while (pos.x <4095 && pos.y < 4095 && ++count<strip_sizes.back());
	} while (1 );
//			} while (pos.x * pos.y < 4095*4095);
std::vector<Pos> get_coords() const {
	return coords;
}

std::vector<Pos> EerIO::get_coords(int i) const {
	return frames[i].get_coords();
}
//int EerFrame::count = 0;
EerIO::EerIO(const string & fname, IOMode rw)
{
	cout<<"EerIO ctor"<<endl;

	tiff_file = TIFFOpen(fname.c_str(), "r");

	for(num_dirs=0; TIFFReadDirectory(tiff_file); num_dirs++)
		;
	
	init();
}

EerIO::~EerIO()
{
	cout<<"EerIO dtor"<<endl;

	TIFFClose(tiff_file);
}

void EerIO::init()
{
	ENTERFUNC;
	
	int count = 0;
	uint32* bc;
	std::vector<unsigned char> eer_data;
	TIFFGetField(tiff_file, TIFFTAG_STRIPBYTECOUNTS, &bc);
	cout<<"bc: "<<bc[0]<<endl;
	cout<<"sizeof(bc): "<<sizeof(bc)<<endl;
	auto nbc = sizeof(bc) / sizeof(bc[0]);
	cout << "num of bc: " << nbc << endl;
	for(size_t i=0; i<nbc; ++i)
		cout<<bc[i]<<"\t";
	cout<<endl;

	int count = 0;
	uint32* bc;
	std::vector<unsigned char> eer_data;
	TIFFGetField(tiff_file, TIFFTAG_STRIPBYTECOUNTS, &bc);
	cout<<"bc: "<<bc[0]<<endl;
	cout<<"sizeof(bc): "<<sizeof(bc)<<endl;
	auto nbc = sizeof(bc) / sizeof(bc[0]);
	cout << "num of bc: " << nbc << endl;
	for(size_t i=0; i<nbc; ++i)
		cout<<bc[i]<<"\t";
	cout<<endl;

	while(TIFFReadDirectory(tiff_file)) {
		uint16_t compression = 0;
		TIFFGetField(tiff_file, TIFFTAG_COMPRESSION, &compression);
		auto nStrips = TIFFNumberOfStrips(tiff_file);
//        auto strip_size = TIFFRawStripSize(tiff_file, count);
//        TIFFReadRawStrip(tiff_file, count, eer_data.data(), bc[0]);

		cout<<"IFD: "<<count
			<<"\t"<<TIFFCurrentDirectory(tiff_file)
			<<"\t"<<TIFFLastDirectory(tiff_file)
			<<"\t"<<nStrips
//            <<"\t"<<strip_size
			<<"\t";
//            <<endl;
//        unsigned char * eer_data;
		std::vector<unsigned char> eer_data;
		for(int i=0; i<nStrips; ++i) {
//            std::vector<unsigned char> eer_data;
			auto strip_size = TIFFRawStripSize(tiff_file, i);
			auto prev_size = eer_data.size();
			eer_data.resize(prev_size + strip_size);
			cout<<strip_size<<"\t";
			TIFFReadRawStrip(tiff_file, i, eer_data.data()+prev_size, strip_size);
//            TIFFReadRawStrip(tiff_file, i, eer_data, strip_size);
		}
		cout<<"eer_data.size: "<<eer_data.size();
		cout<<endl;
//        TIFFPrintDirectory(tiff_file, stdout);
		count++;
	}

	cout<<"Num of dirs: "<<count<<endl;
	cout<<"num_dirs: "<<num_dirs<<endl;
//    cout<<"bc: "<<bc[0]<<endl;

	EXITFUNC;
}

int EerIO::get_nimg()
{
	return 1;
}

bool EerIO::is_image_big_endian()
{
	return is_big_endian;
}


int EerIO::read_header(Dict & dict, int image_index, const Region * area, bool is_3d)
{
	cout<<"read_header"<<endl;

	TIFFSetDirectory(tiff_file, 0);
	TIFFPrintDirectory(tiff_file, stdout);
	TIFFGetField(tiff_file, TIFFTAG_COMPRESSION, &compression);

	char *metadata_c = nullptr;
	uint32_t count = 0;

	TIFFGetField(tiff_file, 65001, &count, &metadata_c);
	metadata = string(metadata_c, count);

	int nx = 0;
	int ny = 0;

	TIFFGetField(tiff_file, TIFFTAG_IMAGEWIDTH, &nx);
	TIFFGetField(tiff_file, TIFFTAG_IMAGELENGTH, &ny);

	dict["nx"] = nx;
	dict["ny"] = ny;
	dict["nz"] = 1;

	dict["nimg"] = int(get_nimg());

	cout<<"Final image:"<<endl;

	TIFFSetDirectory(tiff_file, 0);
	TIFFPrintDirectory(tiff_file, stdout);
	TIFFGetField(tiff_file, TIFFTAG_IMAGEWIDTH, &nx);
	TIFFGetField(tiff_file, TIFFTAG_IMAGELENGTH, &ny);
	TIFFGetField(tiff_file, TIFFTAG_COMPRESSION, &compression);
	cout<<endl;
	uint16_t count = 0;
	//    auto res = TIFFGetField(tiff_file, 65001, &meta);
	auto res = TIFFGetField(tiff_file, 65001, &count, &meta_c);

	cout<<"compres: "<<compression<<endl;
	cout << "meta: " << meta << endl;
	cout<<"Res= "<<res<<endl;
	cout<<endl;

	return 0;  // ???
}


int EerIO::write_header(const Dict & dict, int image_index, const Region* area,
						EMUtil::EMDataType filestoragetype, bool use_host_endian)
{
	ENTERFUNC;

	EXITFUNC;

	return 0;
}

int EerIO::read_data(float *rdata, int image_index, const Region * area, bool)
{
	ENTERFUNC;
//	rdata = new float[4095*4095];
	auto cc = get_coords(image_index);
//	cout<<"Coords #: "<<cc.size()<<endl;
	for(auto &c : cc) {
//		cout<<c<<endl;
		rdata[c.x + c.y*4096] += 1;
	}
//	for(int i=0;i<4095;i+=10){
//		for(int j=0;j<4095;j+=10){
//			rdata[i*4095 + j] = (4095/2 - i)+j;
//		}
//	}

	EXITFUNC;

	return 0;
}

int EerIO::write_data(float *data, int image_index, const Region* area,
					  EMUtil::EMDataType, bool use_host_endian)
{
	ENTERFUNC;

	EXITFUNC;
	return 0;
}


bool EerIO::is_complex_mode()
{
	return false;
}

void EerIO::flush()
{
}
