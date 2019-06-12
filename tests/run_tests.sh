#!/usr/bin/env bash

set -xe

conda list

MYDIR="$(cd "$(dirname "$0")"; pwd -P)"

# 1. Run e2version.py and e2speedtest.py
e2version.py
e2speedtest.py
time python -c "from EMAN2 import *; Util.version()"

# 2. Test git-hash consistency
if [ ${CONDA_BUILD:-0} -ne 1 ];then
    bash "${MYDIR}/test_git_hash.sh"
fi

# 3. Existence tests for data files like images, font files, JSON
python "${MYDIR}/test_EMAN2DIR.py"
