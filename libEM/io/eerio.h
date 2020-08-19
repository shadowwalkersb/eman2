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

#ifndef eman__eerio_h__
#define eman__eerio_h__ 1

#include "imageio.h"

#include <tiffio.h>


namespace EMAN
{
	const unsigned int num_rle_bits = 7;
	const unsigned int num_sub_pix_bits = 2;

	struct Pos {
		Pos(int xx, int yy) : x(xx), y(yy) {}
		int x, y;

		bool operator==(const Pos &p) {
			return x == p.x && y == p.y;
		}

		friend std::ostream& operator<<(std::ostream &out, const Pos &obj) {
			return out<<obj.x
					<<" "<<obj.y;
		}
	};

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

		unsigned int read_rle() {
			static const unsigned int max_val = (1<<num_rle_bits) - 1;
			unsigned int count = 0;
			unsigned int val;
			do {
				val = get_bits(num_rle_bits);
				count += val;
			} while(val == max_val);

			return count;
		}

		Pos read_sub_pos() {
			int sub_pix = get_bits(2*num_sub_pix_bits);

			return Pos((sub_pix  & 3) ^ 2, (sub_pix >> 2) ^ 2);
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
	protected:
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


	template<unsigned int T, bool BIT_OVERFLOW, class U>
	class BitReaderCounter : public BitReader<T, BIT_OVERFLOW, U> {
	private:
		uintmax_t count = 0;

	public:
		operator decltype(count) const () {
			return count;
		}

		friend BitStream<U>& operator>>(BitStream<U> &in, BitReaderCounter<T, BIT_OVERFLOW, U> &obj) {
			in>>static_cast<BitReader<T, BIT_OVERFLOW, U>& >(obj);

			obj.count += (static_cast<BitReader<T, BIT_OVERFLOW, U>>(obj) + (obj.count>0?1:0));

			return in;
		}
	};

	template<unsigned int T, class U>
	using Rle = BitReader<T, true, U>;

	template<unsigned int T, class U>
	using SubPix = BitReader<T, false, U>;

	using EerWord = uint64_t;
	using EerStream     = BitStream    <EerWord>;
	using EerRleCounter = Rle       <7, EerWord>;
	using EerSubPix     = SubPix    <4, EerWord>;


	class EerIO : public ImageIO
	{
	public:
		EerIO(const string & fname, IOMode rw_mode = READ_ONLY);
		~EerIO();

		int get_nimg();

		DEFINE_IMAGEIO_FUNC;

	private:
		bool is_big_endian;
		TIFF *tiff_file;
		uint16_t compression = 0;
		string metadata;
		size_t num_dirs = 0;
	};
}

#endif	//eman__eerio_h__
