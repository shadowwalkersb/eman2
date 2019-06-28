#!/usr/bin/env bash

set -xe

# Download and install Miniconda
export MINICONDA_URL="https://repo.continuum.io/miniconda"
export MINICONDA_FILE="Miniconda2-latest-Linux-x86_64.sh"

curl -L -O "${MINICONDA_URL}/${MINICONDA_FILE}"
bash $MINICONDA_FILE -b

# Configure conda
source ${HOME}/miniconda2/bin/activate root
conda config --set show_channel_urls true

conda install conda=4.6.14 conda-build=3.17.8 cmake=${CMAKE_VERSION} -c defaults --yes
conda install eman-deps=14.2 cmake=3.9 conda=4.6.14 conda-build=3.17.8 -c cryoem/label/dev -c cryoem -c defaults -c conda-forge --yes

conda clean --all --yes
rm $MINICONDA_FILE
