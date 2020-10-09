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

#ifndef eman__eerio_h__
#define eman__eerio_h__ 1

#include "imageio.h"

#include <tiffio.h>
#include <bitset>


namespace EMAN
{
	template <class T>
	class BitStream {
	public:
		BitStream(T *buf)
		: buffer(buf), cur(*buffer)
		{}

		T get_bits(int N) {
			auto result = cur & ((1 << N) - 1);

			if(N < bit_counter) {
				cur        >>= N;
				bit_counter -= N;
			}
			else {
				auto remaining_bits = N - bit_counter;

				cur = *(++buffer);
				result |= ((cur & ((1 << remaining_bits) - 1)) << bit_counter);

				cur >>= remaining_bits;
				bit_counter = max_num_bits - remaining_bits;
			}

			return result;
		}

	private:
		T *buffer;
		T cur;
		const size_t max_num_bits = 8*sizeof(T);
		size_t bit_counter        = max_num_bits;

		friend std::ostream &operator<<(std::ostream &out, const BitStream &obj) {
			return out<<"cur: "<<std::bitset<8*sizeof(T)>(obj.cur)
						<<endl
						<<"bit_counter: "<<obj.bit_counter<<endl
						<<"max_num_bits: "<<obj.max_num_bits<<endl;
		}
	};

	template<unsigned int T, bool BIT_OVERFLOW, class U>
	class BitReader {
	private:
		const decltype(T) num_bits = T;
		const decltype(T) max_val = (1 << num_bits) - 1;
		uintmax_t val = 0;

	public:
		operator decltype(val) const () {
			return val;
		}

		friend BitStream<U>& operator>>(BitStream<U> &in, BitReader<T, BIT_OVERFLOW, U> &obj) {
			decltype(val) count;
			obj.val = 0;
			do {
				count = in.get_bits(obj.num_bits);
				obj.val += count;
			} while(BIT_OVERFLOW && count == obj.max_val);

			return in;
		}
	};

	template<unsigned int T, class U>
	using Rle = BitReader<T, true, U>;

	template<unsigned int T, class U>
	using SubPix = BitReader<T, false, U>;

	using EerWord = uint64_t;
	using EerStream = BitStream<EerWord>;
	using EerRle    = Rle   <7, EerWord>;
	using EerSubPix = SubPix<4, EerWord>;

	
	class EerFrame {
	public:
		EerFrame() =default;
		EerFrame(TIFF *tiff);

		auto data_() const;

	private:
		size_t num_strips;
		std::vector<unsigned char> data;

		void _load_data(TIFF *tiff);
	};


	typedef pair<int, int> COORD;
	typedef vector<COORD> COORDS;

	class Decoder {
		const unsigned int EER_CAMERA_SIZE_BITS = 12;
		const unsigned int EER_CAMERA_SIZE      = 1 << EER_CAMERA_SIZE_BITS; // 2^12 = 4096

	protected:
		virtual unsigned int x(unsigned int count, unsigned int sub_pix) const =0;
		virtual unsigned int y(unsigned int count, unsigned int sub_pix) const =0;

	public:
		auto operator()(unsigned int count, unsigned int sub_pix) const;
	};

	
	struct Decoder4k : public Decoder {
		unsigned int x(unsigned int count, unsigned int sub_pix) const override;
		unsigned int y(unsigned int count, unsigned int sub_pix) const override;
	};
	
	auto decode_eer_data(EerWord *data, Decoder &decoder);

	static Decoder4k decoder4k;


	class EerIO : public ImageIO
	{
	public:
		EerIO(const string & fname, IOMode rw_mode = READ_ONLY, Decoder &dec=decoder4k);
		~EerIO();

		int get_nimg();
		bool is_single_image_format() const override;


		DEFINE_IMAGEIO_FUNC;

	private:
		void _read_meta_info();

		bool is_big_endian;
		TIFF *tiff_file;
		uint16_t compression = 0;
		string metadata;
		size_t num_dirs = 0;
		
		vector<EerFrame> frames;
		Decoder &decoder;
	};
}

#endif	//eman__eerio_h__
