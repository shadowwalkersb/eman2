conda list

:: 1. Run e2version.py and e2speedtest.py
e2version.py
e2speedtest.py
python -c "from EMAN2 import *; Util.version()"

:: 2. Existence tests for data files like images, font files, JSON
python tests\test_EMAN2DIR.py
