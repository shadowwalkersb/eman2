#!/usr/bin/env bash

set -xe

MYDIR="$(cd "$(dirname "$0")"; pwd -P)"

source ${MYDIR}/set_env_vars.sh

if [ -n "${TRAVIS}" ];then
    source ci_support/setup_conda.sh
fi

if [ -n "${CIRCLECI}" ];then
    . $HOME/miniconda/etc/profile.d/conda.sh
    conda activate eman
fi

if [ -n "$JENKINS_HOME" ];then
    CPU_COUNT=4
else
    CPU_COUNT=2
fi

conda info -a
conda list
conda list --explicit

python -m compileall -q .

conda render recipes/eman
conda build purge-all

conda build ${recipe_dir} -c cryoem -c defaults -c conda-forge
