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

	cout<<"EerFrame 0"<<endl;
	cout<<"EerFrame 1"<<endl;
	cout<<"EerFrame 2"<<endl;

	EerStream<uint64_t> is(reinterpret_cast<uint64_t*>(data.data()));
	cout<<"EerFrame 3"<<endl;
	Pos pos(0, 0);
	unsigned count = 0;
	do {
		cout<<pos
			<<" "<<coords.size()
			<<endl;
		pos = is.real_pos();
		coords.push_back(pos);
	} while (pos.x <4095 && pos.y < 4095 && ++count<100);
	cout<<"EerFrame 4"<<endl;
}

std::vector<Pos> get_coords() const {
	return coords;
EerIO::EerIO(const string & fname, IOMode rw)
{
	cout<<"ctor"<<endl;
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
	cout<<"init"<<endl;

	EXITFUNC;
}

int EerIO::get_nimg()
{
	cout<<"get_nimg"<<endl;
	return 1;
}

bool EerIO::is_image_big_endian()
{
	cout<<"is_image_big_endian"<<endl;
	return is_big_endian;
}


int EerIO::read_header(Dict & dict, int image_index, const Region * area, bool is_3d)
{
	cout<<"read_header"<<endl;
	TIFFSetDirectory(tiff_file, 0);
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

cout<<"read_data"<<endl;
	//	rdata = new float[4095*4095];
//	for(auto &c : get_coords(100)) {
//		rdata[c.x*4095 + c.y]= 2.f;
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
