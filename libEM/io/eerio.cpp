/*
 * Author: tunay.durmaz@bcm.edu, 08/20/2020
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


EerFrame::EerFrame(TIFF *tiff)
	: num_strips(TIFFNumberOfStrips(tiff))
{
	_load_data(tiff);
}

void EerFrame::_load_data(TIFF *tiff) {
	vector<unsigned int> strip_sizes(num_strips);
	for(size_t i=0; i<num_strips; ++i) {
		strip_sizes[i] = TIFFRawStripSize(tiff, i);
	}

	for(size_t i=0; i<num_strips; ++i) {
		auto prev_size = data.size();
		data.resize(prev_size + strip_sizes[i]);
		TIFFReadRawStrip(tiff, i, data.data()+prev_size, strip_sizes[i]);
	}
}

auto EerFrame::data_() const {
	return data.data();
}


unsigned int Decoder::x(unsigned int count, unsigned int sub_pix) const {
	return count & (EER_CAMERA_SIZE - 1);
}

unsigned int Decoder::y(unsigned int count, unsigned int sub_pix) const {
	return  count >> EER_CAMERA_SIZE_BITS;
}

unsigned int Decoder4k::x(unsigned int count, unsigned int sub_pix) const {
	cout<<"Decoder4k()::x"<<endl;
	return Decoder::x(count, sub_pix);
}

unsigned int Decoder4k::y(unsigned int count, unsigned int sub_pix) const {
	cout<<"Decoder4k()::y"<<endl;
	return Decoder::y(count, sub_pix);
}

unsigned int Decoder8k::x(unsigned int count, unsigned int sub_pix) const {
	cout<<"Decoder8k()::x"<<endl;
	return (Decoder::x(count, sub_pix) << 1) | (sub_pix & 1);
}

unsigned int Decoder8k::y(unsigned int count, unsigned int sub_pix) const {
	cout<<"Decoder8k()::y"<<endl;
	return (Decoder::y(count, sub_pix) << 1) | (sub_pix >> 1);
}

auto Decoder::operator()(unsigned int count, unsigned int sub_pix) const {
	return std::make_pair(x(count, sub_pix), y(count, sub_pix));
}

typedef vector<pair<int, int>> COORDS;

const unsigned int EER_CAMERA_SIZE_BITS = 12;
const unsigned int EER_CAMERA_SIZE      = 1 << EER_CAMERA_SIZE_BITS; // 2^12 = 4096

auto EMAN::decode_eer_data(EerWord *data, Decoder &decoder) {
	EerStream is((data));
	EerRle    rle;
	EerSubPix sub_pix;

	int count = 0;

	COORDS coords;

	while (count < EER_CAMERA_SIZE * EER_CAMERA_SIZE) {
		is>>rle>>sub_pix;
		
		coords.push_back(decoder(count, sub_pix));

		count += rle+1;
	}

	return coords;
}

EerIO::EerIO(const string & fname, IOMode rw, Decoder &dec)
:	ImageIO(fname, rw), decoder(dec)
{
	tiff_file = TIFFOpen(fname.c_str(), "r");

	for(num_dirs=0; TIFFReadDirectory(tiff_file); num_dirs++)
		;

	frames.resize(get_nimg());
	
	for(size_t i=0; i<get_nimg(); i++){
		TIFFSetDirectory(tiff_file, i);

		frames[i] = EerFrame(tiff_file);
	}
}

EerIO::~EerIO()
{
	TIFFClose(tiff_file);
}

void EerIO::init()
{
	ENTERFUNC;

	_read_meta_info();

	EXITFUNC;
}

void EerIO::_read_meta_info() {
	TIFFSetDirectory(tiff_file, 0);
	TIFFGetField(tiff_file, TIFFTAG_COMPRESSION, &compression);

	char *metadata_c = nullptr;
	uint32_t count = 0;

	TIFFGetField(tiff_file, 65001, &count, &metadata_c);
	metadata = string(metadata_c, count);
}

int EerIO::get_nimg()
{
	return 10;
}

bool EerIO::is_image_big_endian()
{
	return is_big_endian;
}


int EerIO::read_header(Dict & dict, int image_index, const Region * area, bool is_3d)
{
	TIFFSetDirectory(tiff_file, image_index);

	int nx = 0;
	int ny = 0;

	TIFFGetField(tiff_file, TIFFTAG_IMAGEWIDTH, &nx);
	TIFFGetField(tiff_file, TIFFTAG_IMAGELENGTH, &ny);

	dict["nx"] = EER_CAMERA_SIZE;
	dict["ny"] = EER_CAMERA_SIZE;
	dict["nz"] = 1;

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

	auto coords = decode_eer_data((EerWord *) frames[image_index].data_(), decoder);
	for(auto &c : coords)
		rdata[c.first + c.second * EER_CAMERA_SIZE] += 1;

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

bool EerIO::is_single_image_format() const
{
	return false;
}
