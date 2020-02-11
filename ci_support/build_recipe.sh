#!/usr/bin/env bash

set -xe

MYDIR="$(cd "$(dirname "$0")"; pwd -P)"

source ${MYDIR}/set_env_vars.sh

if [ -n "${TRAVIS}" ];then
    source ci_support/setup_conda.sh
fi

source "${MYDIR}/circleci.sh"

python -m compileall -q .

source "${MYDIR}/jenkinsci.sh"

conda info -a
conda list
conda list --explicit
conda render recipes/eman
conda build purge-all

conda build ${recipe_dir} -c cryoem -c defaults -c conda-forge
