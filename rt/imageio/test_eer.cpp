/*
 *
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

#include "io/eerio.h"

using namespace EMAN;


#undef NDEBUG
#include <cassert>


#include "io/eerio.h"

uint64_t mm = ~0;
uint64_t nn = ~0 - 1;
uint64_t bb = 1 << 1 | 1 << 3 | 1 << 5 | 1 << 7;
//    WORD bb = 0b10101010;
//	WORD b[] = {mm, nn, bb};

uint8_t a = 0b10101010;
uint8_t b = 0b10011001;
uint8_t ab[] = {a, b};

uint64_t AB[] = {a, b};
EerStream<uint64_t> is3(AB);

void test_eer_get_bits() {
	EerStream<uint64_t> is(&mm);
	assert(is.get_bits(3) == 7);
	assert(is.get_bits(9) == (1 << 9) - 1);
	assert(is.get_bits(1) == 1);

	EerStream<uint64_t> is1(&bb);
	assert(is1.get_bits(2) == 2);
	assert(is1.get_bits(3) == 2);
	assert(is1.get_bits(3) == 5);

//	cout<<is1<<endl;

	EerStream<uint64_t> is2(reinterpret_cast<uint64_t *>(ab));
	assert(is2.get_bits(2) == 2);
//	cout<<is2<<endl;
	assert(is2.get_bits(6) == 42);

	EerStream<uint8_t> is22(ab);
	assert(is22.get_bits(2) == 2);
//	cout<<is2<<endl;
	assert(is22.get_bits(6) == 42);
	assert(is22.get_bits(3) == 1);

	uint64_t AB[] = {a, b};
	EerStream<uint64_t> is3(AB);

	is5 >> rle;
	assert(rle == 42);

	is5 >> rle;
	assert(rle == 0b110011);

	is5 >> rle;
	assert(rle == 0b1001100 + (1<<7) - 1);
}

void test_eer_sub_pix() {
	EerStream is6(reinterpret_cast<EerWord *>(ab5));
	EerSubPix sub_pix;
	EerRleCounter rle6;

	is6 >> sub_pix;
	assert(sub_pix == 10);

	is6 >> rle6 >> sub_pix;
	assert(sub_pix == 11);
}

void test_eer_rle() {
	typedef uint8_t BuffWord;
	auto num_bits = sizeof(BuffWord) * 8;
	
	BuffWord a = 0b11111111;
	
	BitStream<BuffWord> is1(&a);
	BitReader<1, false, BuffWord> rle1;
	
	for(int i=0; i<num_bits; i++) {
		is1 >> rle1;
		assert(rle1 == 1);
	}

	BitStream<BuffWord> is2(&a);
	BitReader<2, false, BuffWord> rle2;

	for(int i=0; i<num_bits/2; i++) {
		is2 >> rle2;
		assert(rle2 == 0b11);
	}

	BitStream<BuffWord> is4(&a);
	BitReader<4, false, BuffWord> rle4;

	for(int i=0; i<num_bits/4; i++) {
		is4 >> rle4;
		assert(rle4 == 0b1111);
	}

	BitStream<BuffWord> is3(&a);
	BitReader<3, false, BuffWord> rle3;

	is3>>rle3;
	assert(rle3 == 0b111);
	is3>>rle3;
	assert(rle3 == 0b111);
	is3>>rle3;
	assert(rle3 == 0b11);
}

void test_eer_rle_counter() {
	typedef uint8_t BuffWord;
	auto num_bits = sizeof(BuffWord) * 8;

	BuffWord a = 0b11001101;

	BitStream<BuffWord> is1(&a);
	BitReaderCounter<1, false, BuffWord> rle1;

	is1 >> rle1;
	assert(rle1 == 1);

	is1 >> rle1;
	cout<<rle1<<endl;
	assert(rle1 == 2);

	is1 >> rle1;
	assert(rle1 == 4);

	assert(rle1 == 4.);
	assert(rle1 == 4.f);
	assert(rle1 == (int)4);
	assert(rle1 == (short)4);

	is1 >> rle1;
	assert(rle1 == 6);

	is1 >> rle1;
	assert(rle1 == 7);

	is1 >> rle1;
	assert(rle1 == 8);

	is1 >> rle1;
	assert(rle1 == 10);

	is1 >> rle1;
	assert(rle1 == 12);
}

void test_eer_real_pos() {
	BitStream<uint8_t> is66(ab5);
	SubPix<4, uint8_t> sub_pix;
	RleCounter<7, uint8_t> rle66;
	cout<<"\n\nis66"<<endl;
	cout<<is66;
	is66>>sub_pix;
	cout<<sub_pix<<endl;
	cout<<decode(sub_pix)<<endl;
	assert(decode(sub_pix) == Pos(0,0));
	is66>>rle66>>sub_pix;
	cout<<is66<<endl;
	cout<<rle66<<endl;
	cout<<sub_pix<<endl;
	cout<<decode(sub_pix)<<endl;
	assert(decode(sub_pix) == Pos(0,0));
	is66>>rle66>>sub_pix;
	assert(decode(sub_pix) == Pos(1,0));

	BitStream<uint8_t> is7(ab5);
//	auto pos = is7.real_pos();
//	cout<<pos<<endl;
//	assert(pos == Pos(169, 2));
	assert(is7.real_pos() == Pos(169, 2));
//	pos = is7.real_pos();
//	cout<<pos<<endl;
	assert(is7.real_pos() == Pos(661, 3));
}

uint8_t a5 = 0b10101010;
uint8_t b5 = 0b11011001;
uint8_t c5 = 0b10011111;
uint8_t d5 = 0b10011001;
uint8_t ab5[] = {a5,b5,c5,d5};

void test_eer_rle() {
	EerStream<uint64_t> is4(AB);

	assert(is4.read_rle() == 42);

	EerStream<uint8_t> is5(ab5);
	EerStream<uint8_t> is55(ab5);
	RLE<uint8_t> rle;

	is55>>rle;
	assert(rle.count == 42);

	is55>>rle;
	assert(rle.count == 0b110011 + 42);

	is55>>rle;
	assert(rle.count == 0b1001100 + (1<<7) - 1 + 0b110011 + 42);

	assert(is5.read_rle() == 42);
	assert(is5.read_rle() == 0b110011 + 42);
	assert(is5.read_rle() == 0b1001100 + (1<<7) - 1 + 0b110011 + 42);
}

void test_eer_sub_pos() {
	EerStream<uint8_t> is6(ab5);
	assert(is6.read_sub_pos() == Pos(0,0));
	is6.read_rle();
	assert(is6.read_sub_pos() == Pos(1,0));
}

void test_eer_real_pos() {
	EerStream<uint8_t> is7(ab5);
//	auto pos = is7.real_pos();
//	cout<<pos<<endl;
//	assert(pos == Pos(169, 2));
	assert(is7.real_pos() == Pos(169, 2));
//	pos = is7.real_pos();
//	cout<<pos<<endl;
	assert(is7.real_pos() == Pos(661, 3));
}

int main()
{
	test_bit_stream();
	test_bit_reader();
	test_eer_sub_pix();
	test_eer_rle();
	test_eer_rle_counter();
	test_eer_real_pos();

	test_eer_get_bits();
	test_eer_rle();
	test_eer_sub_pos();
	test_eer_real_pos();

	return 0;
}
