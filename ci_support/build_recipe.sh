#!/usr/bin/env bash

set -xe

MYDIR="$(cd "$(dirname "$0")"; pwd -P)"

if [ ! -z ${TRAVIS} ];then
    source ci_support/setup_conda.sh

    conda install conda-build=3 -c defaults --yes
fi

if [ ! -z ${CIRCLECI} ];then
    source ${HOME}/miniconda3/bin/activate root
fi

python -m compileall -q .

export CPU_COUNT=2

conda info -a
conda list
conda render recipes/eman
conda build purge-all

conda build recipes/eman -c cryoem/label/dev -c cryoem -c defaults -c conda-forge -m $1
