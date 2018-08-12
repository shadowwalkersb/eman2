#!/bin/bash

set -xe

build_dir="${SRC_DIR}/../build_eman"

rm -rf $build_dir
mkdir -p $build_dir
cd $build_dir

LDFLAGS=${LDFLAGS/-Wl,-dead_strip_dylibs/}
LDFLAGS=${LDFLAGS/-Wl,-pie/}
CXXFLAGS=${CXXFLAGS/-std=c++17/-std=c++14}

cmake $SRC_DIR

make -j${CPU_COUNT}
make install

if [ "$JOB_NAME" != "Centos7" ];then
    if [ "${CONDA_BUILD_STATE}" == "BUILD" ];then
        rm -rfv ${SRC_DIR}/tests/gui/__pycache__
    fi
    make test-gui
fi
