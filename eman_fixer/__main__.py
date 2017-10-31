#!/usr/bin/env python

import sys, os
from lib2to3.main import main

sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
print sys.path
sys.exit(main("fix_eman_div"))
