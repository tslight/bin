#!/usr/bin/env bash

countdown() {
    local -i start="$1"
    local msg="$2" local spin='-\|/'

    for i in $(seq -w "$start" -1 0); do
        for k in {1..10}; do
            local -i j=$(( (j+1) %4 ))
            printf "\rWaiting $i seconds for $msg... ${spin:$j:1} "
            sleep .1
        done
    done

    printf "\rFinished waiting for $msg.\033[K\n"
}

countdown "$1" "$2"
