#!/usr/bin/env bash

for f in "${@}";do
    export FILENAME=${f}
    2to3 -w -n --no-diff -f eman_div "${f}"
done
