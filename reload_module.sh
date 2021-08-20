#!/usr/bin/env bash
# shellcheck disable=SC2039

# I use this to reload the touchpad driver on my HP ProBook that does funny
# things after suspend. Hence the default the module value. However it could be
# used to reload any module passed in as an argument.

NC="$(tput sgr0)"
RED="$(tput setaf 1)"
GRN="$(tput setaf 2)"
YEL="$(tput setaf 3)"

modcmd() {
    local command="$1" module="$2"

    printf "%sRunning %s %s... " "$YEL" "$command" "$module"
    if output=$(sudo "$command" "$module" 2>&1); then
        printf "%sDONE :-)%s\n" "$GRN" "$NC"
    else
        printf "%sFAIL :-(%s\n%s\n" "$RED" "$NC" "$output"
    fi
}

[ -z "$1" ] && MODULE="i2c_hid" || MODULE="$1"

RMMOD=$(command -v rmmod)
MODPROBE=$(command -v modprobe)

modcmd "$RMMOD" "$MODULE"
modcmd "$MODPROBE" "$MODULE"
