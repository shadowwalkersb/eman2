/**
 * $Id$
 */
#ifndef eman__imageio_h__
#define eman__imageio_h__ 1

#include "emobject.h"
#include "byteorder.h"

#include <vector>
#include <string>
#include <stdio.h>

using std::vector;
using std::string;

namespace EMAN
{
	class Region;
	class IntSize;
	class Ctf;

	/** ImageIO classes are designed for reading/writing various
	 * electron micrography image formats, including MRC, IMAGIC,
	 * SPIDER, PIF, etc. 
	 * 
	 * ImageIO class is the base class for all image io classes.
	 * Each subclass defines the IO routines for reading/writing a
	 * type of image format. For example, MrcIO is for reading/writing
	 * MRC images.
	 * 
	 * A subclass should implement functions declared in
	 * DEFINE_IMAGEIO_FUNC macro.
	 *
	 * Image header I/O is separated from image data I/O.
	 *
	 * Some image formats (e.g., MRC, DM3, Gatan2, TIFF, PNG, EM, ICOS) only store a
	 * single 2D or 3D images. For them, image_index should always be
	 * 0. To read/write part of the image, use a region.
	 *
	 * Some image formats (e.g., Imagic) can store either a
	 * stack of 2D images or a single 3D image. From the physical
	 * image file itself, there is no difference between them. Only at
	 * reading time, they may be treated as either a stack of 2D
	 * images, or a single 3D image. A boolean hint should be given for these
	 * formats at reading time.
	 *
	 * Some image formats (e.g. HDF) can store a stack of images. Each
	 * image can be 2D or 3D.
	 * 
	 * For image formats storing multiple images, valid image_index = [0, n].
	 *
	 * For image formats storing multiple images, the image append and
	 * insertion policy is:
	 *
	 *   - it should support appending image to existing file.
	 *
	 *   - it should support appending image to new file.
	 *
	 *   - it should support insert image in existing file with gap
	 *     between EOF and the new image. The gap should be zeroed.
	 * 
	 *   - it should support insert image in new file with image index != 0.
	 *
	 *   - insert image in existing file overwriting existing image.
	 *
	 *   - The gap from insertion or appending should be filled with zero.
	 *
	 * Image region writing follows the following princeples:
	 *
	 *   - The file must exist before writing a region to it.
	 *
	 *   - The image header usually won't be changed except the
	 *     statistics fields and timestamp.
	 *
	 *   - The region must be inside the original image.
	 *
	 *   - If the new data are in different endian from the endian of 
	 *     the original image, swap the new data.
	 *
	 *   - If the new data are of different data type from the data
     *     type of the original image, convert the new data. This may
     *     lose information when converting from longer data type to
     *     shorter data type.
	 *
	 *   
	 *
	 * The typical way to use an ImageIO instance is:
	 * a) To read:
	 *    ImageIO *imageio = EMUtil::get_imageio(filename, ImageIO::READ_ONLY);
	 *    int err = imageio->read_header(dict, img_index, region, is_3d);
	 *    err = imageio->read_ctf(ctf, img_index);
	 *    err = imageio->read_data(data, img_index, region, is_3d);
	 *
	 * b) To write:
	 *    similar to read.
	 */
	class ImageIO
	{
	  public:
		enum IOMode
		{ READ_ONLY = 1, READ_WRITE = 2, WRITE_ONLY = 3 };
	  public:
		virtual ~ ImageIO();

		/** Read the header from an image.
		 *
		 * @param dict A keyed-dictionary to store the header information.
		 * @param image_index The index of the image to read.
		 * @param area Define an image-region to read.
		 * @param is_3d Whether to treat the image as a single 3D or a
		 *   set of 2Ds. This is a hint for certain image formats which
		 *   has no difference between 3D image and set of 2Ds.
		 * @return 0 if OK; 1 if error.
		 */
		virtual int read_header(Dict & dict, int image_index = 0,
								const Region * area = 0, bool is_3d = false) = 0;

		/** Write a header to an image.
		 *
		 * @param dict A keyed-dictionary storing the header information.
		 * @param image_index The index of the image to write.
		 * @param area The region to write data to.
		 * @param use_host_endian Whether to use the host machine
		 *        endian to write out or not. If false, use the
		 *        endian opposite to the host machine's endian.
		 * @return 0 if OK; 1 if error.
		 */
		virtual int write_header(const Dict & dict, int image_index = 0,
								 const Region * area = 0, bool use_host_endian = true) = 0;

		/** Read the data from an image.
		 *
		 * @param data An array to store the data. It should be
		 *        created outside of this function.
		 * @param image_index The index of the image to read.
		 * @param area Define an image-region to read.
		 * @param is_3d Whether to treat the image as a single 3D or a
		 *        set of 2Ds. This is a hint for certain image formats which
		 *        has no difference between 3D image and set of 2Ds.
		 * @return 0 if OK; 1 if error.
		 */
		virtual int read_data(float *data, int image_index = 0,
							  const Region * area = 0, bool is_3d = false) = 0;

		/** Write data to an image.
		 *
		 * @param data An array storing the data.
		 * @param image_index The index of the image to write.
		 * @param area The region to write data to.
		 * @param use_host_endian Whether to use the host machine
		 *        endian to write out or not. If false, use the
		 *        endian opposite to the host machine's endian.
		 * @return 0 if OK; 1 if error.
		 */
		virtual int write_data(float *data, int image_index = 0,
							   const Region * area = 0, bool use_host_endian = true) = 0;

		/** Read CTF data from this image.
		 *
		 * @param ctf Used to store the CTF data. 
		 * @param image_index The index of the image to read.
		 * @return 0 if OK; 1 if error.
		 */
		virtual int read_ctf(Ctf & ctf, int image_index = 0);

		/** Write CTF data to this image.
		 *
		 * @param ctf Ctf instance storing the CTF data.
		 * @param image_index The index of the image to write.
		 * @return 0 if OK; 1 if error.
		 */
		virtual int write_ctf(const Ctf & ctf, int image_index = 0);

		virtual void flush() = 0;
		
		/** Return the number of images in this image file. */
		virtual int get_nimg();

		/** Is this an complex image or not. */
		virtual bool is_complex_mode() = 0;

		/** Is this image in big endian or not. */
		virtual bool is_image_big_endian() = 0;

		/** Is this image format only storing 1 image or not.*/
		virtual bool is_single_image_format() const
		{
			return true;
		}
		
		/** Convert data of this image into host endian format.
		 *
		 * @param data An array of data. It can be any type, short,
		 *        int, float, double, etc.
		 * @param n Array size.
		 */
		template < class T > void become_host_endian(T * data, size_t n = 1)
		{
			if (is_image_big_endian() != ByteOrder::is_host_big_endian()) {
				ByteOrder::swap_bytes(data, n);
			}
		}

	protected:
		virtual void init() = 0;
		void check_read_access(int image_index);
		void check_read_access(int image_index, float *data);
		void check_write_access(IOMode rw_mode, int image_index, int max_nimg = 0);
		void check_write_access(IOMode rw_mode, int image_index, int max_nimg, float *data);
		void check_region(const Region * area, const IntSize & max_size);

		FILE *sfopen(const string & filename, IOMode mode,
					 bool * is_new = 0, bool overwrite = false);
	};

	/** DEFINE_IMAGEIO_FUNC declares the functions that needs to
	 * be implemented by any subclass of ImageIO.
	 */
#define DEFINE_IMAGEIO_FUNC \
		int read_header(Dict & dict, int image_index = 0, const Region* area = 0, bool is_3d = false); \
		int write_header(const Dict & dict, int image_index = 0, const Region * area = 0, bool use_host_endian = true); \
		int read_data(float* data, int image_index = 0, const Region* area = 0, bool is_3d = false); \
		int write_data(float* data, int image_index = 0, const Region * area = 0, bool use_host_endian = true); \
		void flush(); \
		bool is_complex_mode(); \
		bool is_image_big_endian(); \
		void init()

}


#endif
