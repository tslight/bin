#!/usr/bin/env bash

[ -z "$1" ] && msg="Hello $USER, my name is $(hostname)!" || msg="$1"

title="${msg%% *}"
osascript -e 'display notification "'"$msg"'" with title "'"$title"'"'
osascript -e "set Volume 10"
say "$msg"
