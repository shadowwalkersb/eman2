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
EerIO::EerIO(const string & fname, IOMode rw)
{
	tiff_file = TIFFOpen(fname.c_str(), "r");

	for(num_dirs=0; TIFFReadDirectory(tiff_file); num_dirs++)
		;
}

EerIO::~EerIO()
{
	TIFFClose(tiff_file);
}

void EerIO::init()
{
	ENTERFUNC;

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

	return 0;
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
