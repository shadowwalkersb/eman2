#!/usr/bin/env bash

set -xe

# Download and install Miniconda
export MINICONDA_URL="https://repo.continuum.io/miniconda"
export MINICONDA_FILE="Miniconda2-4.4.10-Linux-x86_64.sh"

curl -L -O "${MINICONDA_URL}/${MINICONDA_FILE}"
bash $MINICONDA_FILE -b

# Configure conda
source ${HOME}/miniconda2/bin/activate root
conda config --set show_channel_urls true

conda install conda=4.6.14 conda-build=3.17.8 cmake=3.9 -c defaults --yes
