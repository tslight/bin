#!/usr/bin/env bash
THIS_DIR="$( cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
LIB="$THIS_DIR/lib/bash"
source "$LIB/colors"

usage() {
    echo "
$(basename $0) [TARGET DIRECTORY] [FILE TYPE]

[FILE TYPE] is one of the following:

- archive
- audio
- doc
- ebook
- img
- video

Example:

$(basename $0) /path/to/target/dir img

Would print files image files stored in /path/to/target/dir
"
}

find_file_type() {
    local dir="$1" type="$2" regex="$3"
    printf "${YEL}Checking $dir for $type files... ${NC}"
    readarray -d '' found_files < <(find -L "$dir" -iregex "$regex" -print0)
    if [ "${#found_files[@]}" == 0 ]; then
        printf "${CYN}Nothing to see here :-)${NC}\n"
    else
        printf "${MAG}Found ${#found_files[@]}:${NC}\n"
        for f in "${found_files[@]}"; do
            echo "$f"
        done
    fi
}

if [ -z "$1" ]; then
    usage
    exit 1
else
    if [ -d "$1" ]; then
        TARGET_DIR="$1"
    else
        printf "\n${RED}$1 is not a valid directory! Aborting!${NC}\n"
        usage
        exit 1
    fi
fi

if [ -z "$2" ]; then
    usage
    exit 1
else
    TYPE="$2"
    EXTENSIONS_FILE="$THIS_DIR/share/$TYPE.extensions.list"
    [ -f "$EXTENSIONS_FILE" ] || {
        printf "\n${RED}$EXTENSIONS_FILE doesn't exist. Aborting!${NC}\n"
        usage
        exit 1
    }
fi

readarray -t EXTENSIONS < "$EXTENSIONS_FILE"

for ext in "${EXTENSIONS[@]}"; do
    if [ "$ext" == "${EXTENSIONS[-1]}" ]; then
        REGEX+=".*\.$ext"
    else
        REGEX+=".*\.$ext\|"
    fi
done

find_file_type "$TARGET_DIR" "$TYPE" "$REGEX"
