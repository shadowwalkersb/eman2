d3 = {"--apix", "--average", "--averager", "--calcfsc", "--calcsf", "--clip", "--process", "--add", "--addfile",
      "--mult", "--multfile", "--first", "--fouriershrink", "--last", "--medianshrink", "--meanshrink", "--align",
      "--alignctod", "--alignref", "--append", "--avg_byxf", "--calcradial", "--compressbits", "--nooutliers",
      "--diffmap", "--fftclip", "--filtertable", "--fragmentize", "--icos2to5", "--icos5fhalfmap", "--icos5to2",
      "--inputto1", "--matchto", "--meanshrinkbig", "--origin", "--outmode", "--outnorescale", "--outtype", "--ppid",
      "--resetxf", "--ralignzphi", "--rot", "--scale", "--setsf", "--setisosf", "--step", "--swap", "--sym",
      "--tomoprep", "--tophalf", "--trans", "--unstacking"}

d2 = {"--apix", "--average", "--avgseq", "--averager", "--calcsf", "--calccont", "--clip", "--exclude", "--fftavg",
      "--process", "--mult", "--add", "--addfile", "--first", "--last", "--list", "--select", "--randomn", "--inplace",
      "--interlv", "--extractboxes", "--meanshrink", "--medianshrink", "--fouriershrink", "--mraprep", "--compressbits",
      "--outmode", "--outnorescale", "--fixintscaling", "--multfile", "--norefs", "--outtype", "--radon", "--randomize",
      "--rotavg", "--rotate", "--rfp", "--fp", "--scale", "--anisotropic", "--selfcl", "--setsfpairs", "--split",
      "--translate", "--headertransform", "--verbose", "--plane", "--writejunk", "--swap", "--threed2threed",
      "--threed2twod", "--twod2threed", "--unstacking", "--ppid", "--step", "--eer2x", "--eer4x", "--parallel"}

print(sorted(d2 & d3))
