#!/usr/bin/env bash

set -xe

# Download and install Miniconda
export MINICONDA_URL="https://repo.continuum.io/miniconda"
export MINICONDA_FILE="Miniconda3-4.6.14-Linux-x86_64.sh"

curl -L -O "${MINICONDA_URL}/${MINICONDA_FILE}"
bash $MINICONDA_FILE -b

# Configure conda
source ${HOME}/miniconda3/bin/activate root
conda config --set show_channel_urls true

conda config --set auto_update_conda False

conda install ${CIRCLE_JOB} eman-deps=18.0 conda=4.6.14 conda-build=3.17.8 cmake=3.14 -c cryoem -c defaults -c conda-forge --yes
conda clean --all --yes
