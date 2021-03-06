#!/usr/bin/env bash

set -xe

function print_usage(){
    printf "\e\033[35m\n  Usage: $(basename ${0}) %s %s\n\n\033[0m" "[installer's path]" "[installation directory]" >&2
    exit 64
}

case $# in
    2) installer_file="$1"
       installation_loc="$2"
       ;;

    *) echo $#
    print_usage
       ;;
esac

MYDIR="$(cd "$(dirname "$0")" && pwd -P)"

rm -rf ${installation_loc}
bash "${installer_file}" -bp ${installation_loc}
source ${installation_loc}/bin/activate root
conda info -a
conda list
conda list --explicit
bash "${MYDIR}/run_tests_from_binary.sh"
