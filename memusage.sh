#!/usr/bin/env bash

usage() {
    echo "
$(basename "$0") [PROGRAM]
"
}

[ -n "$1" ] && PROG="$1" || { usage; exit 1; }

# You'd think you could just use the pipeline below, however, whilst that works
# as expected in an interactive shell, it does not work as expected when called
# from a script. Because... bash gremlins I guess!

# sudo pmap $(pgrep -f firefox) | tail -n 1 | awk 'gsub(/K/, '' $0) {print $2}'

PIDS=();

while IFS= read -r -d $'\n'; do
    PIDS+=("$REPLY");
done < <(pgrep -f "$PROG")

total=0

for p in "${PIDS[@]}"; do
    # echo "$p"
    KB=$(pmap "$p" | tail -n 1 | awk '{print $2}')
    KB=${KB%K}
    total=$((total+KB))
done

if ((total>1048576)); then
    total=$((total/1024/1024))
    echo "$total GB"
elif ((total>1024)); then
    total=$((total/1024))
    echo "$total MB"
else
    echo "$total KB"
fi
