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
        
        description = "TabError: inconsistent use of tabs and spaces in indentation"
        gh_link = "../tree/master/" fname "#L" $0

        printf("- [ ] %s: [%s:%d](%s)\n", description, fname, $0, gh_link)

        next
    }
'
