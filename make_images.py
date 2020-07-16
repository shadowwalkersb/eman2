from EMAN2 import *

im = EMData()

num=100000
input_file = "test_images_{}.mrcs".format(num)

#for i in range(num):
#    test_image(i%10).write_image(input_file, -1)

im.read_images(input_file)

print(im.get_ndim())
print(EMUtil.get_image_count(input_file))

'''
(eman-deps-22) firefly:test-eman shadow_walker$ time python make_images.py
elapsed time: 8.606s
1
10000

real	0m9.002s
user	0m5.876s
sys	0m1.748s
(eman-deps-22) firefly:test-eman shadow_walker$ time python make_images.py
elapsed time: 4.22278s
1
10000

real	0m4.638s
user	0m2.798s
sys	0m0.789s
(eman-deps-22) firefly:test-eman shadow_walker$ time python make_images.py
elapsed time: 45.1925s
1
100000

real	0m46.834s
user	0m26.605s
sys	0m8.270s
(eman-deps-22) firefly:test-eman shadow_walker$ time python make_images.py
elapsed time: 85.3389s
1
100000

real	1m26.778s
user	0m58.540s
sys	0m20.678s
'''
