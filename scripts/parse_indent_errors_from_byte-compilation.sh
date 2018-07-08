#!/usr/bin/env bash

python -m compileall -qf . |

awk '
    /Error compiling/{
        fname=$0
        sub(/.*\.\//,"", fname)
        sub(/'\''\.*/,"", fname)
        next
    }
    /Sorry: TabError:/{
        sub(/.* line /,"")
        sub(/\)/,"")
        printf("%s:%d\n", fname, $0 )
        next
    }
'
