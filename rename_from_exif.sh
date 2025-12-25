#!/usr/bin/env bash
THIS_DIR="$( cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
LIB="$THIS_DIR/lib/bash"
source "$LIB/colors"

usage() {
    echo "
$(basename "$0") [-s [SOURCE]] [-i [IMG_DESTINATION]] [-v [VID_DESTINATION]] [-a [AUDIO_DESTINATION]] [-t [TAGS]]
"
}

while getopts "a:s:i:v:t:h" opt; do
    case $opt in
	h) usage
	   exit 0
	   ;;
	s) SOURCE="$OPTARG"
	   ;;
	i) IMG_DESTINATION="$OPTARG"
	   ;;
	v) VID_DESTINATION="$OPTARG"
	   ;;
	a) AUDIO_DESTINATION="$OPTARG"
	   ;;
	t) TAGS="$OPTARG"
	   ;;
	\?) echo "${RED}INVALID OPTION -$OPTARG${NC}" >&2
	    usage
	    exit 1
	    ;;
    esac
done

[ -z "$SOURCE" ] && SOURCE="$HOME/Dropbox/Camera Uploads"
[ -d "$SOURCE" ] || { echo "${RED}$SOURCE doesn't exist. Aborting!${NC}"; exit 1; }
[ -z "$IMG_DESTINATION" ] && IMG_DESTINATION="$HOME/Dropbox/Pictures"
[ -d "$IMG_DESTINATION" ] || { echo "${RED}$IMG_DESTINATION doesn't exist. Aborting!${NC}"; exit 1; }
[ -z "$VID_DESTINATION" ] && VID_DESTINATION="$HOME/Dropbox/Videos"
[ -d "$VID_DESTINATION" ] || { echo "${RED}$VID_DESTINATION doesn't exist. Aborting!${NC}"; exit 1; }
[ -z "$AUDIO_DESTINATION" ] && AUDIO_DESTINATION="$HOME/Dropbox/audio/talk/vn"
[ -d "$AUDIO_DESTINATION" ] || { echo "${RED}$AUDIO_DESTINATION doesn't exist. Aborting!${NC}"; exit 1; }
[ -z "$TAGS" ] && TAGS=("createdate" "datetimeoriginal" "filemodifydate" "modifydate")

FILE_FMT="%Y%m%d.%H%M%S%%c.%%le"
IMG_DIR_FMT="$IMG_DESTINATION/%Y/%m"
VID_DIR_FMT="$VID_DESTINATION/%Y/%m"
AUDIO_DIR_FMT="$AUDIO_DESTINATION/%Y/%m"

readarray -t IMG_FILE_EXT < "$THIS_DIR/share/img.extensions.list"
for ext in "${IMG_FILE_EXT[@]}"; do
    IMG_FILE_EXT_OPTS+="-ext $ext "
done

readarray -t VID_FILE_EXT < "$THIS_DIR/share/video.extensions.list"
for ext in "${VID_FILE_EXT[@]}"; do
    VID_FILE_EXT_OPTS+="-ext $ext "
done

readarray -t AUDIO_FILE_EXT < "$THIS_DIR/share/audio.extensions.list"
for ext in "${AUDIO_FILE_EXT[@]}"; do
    AUDIO_FILE_EXT_OPTS+="-ext $ext "
done

COMMON_OPTS="-recurse -extractEmbedded -ignoreMinorErrors"

for tag in "${TAGS[@]}"; do
    if [ -n "$( find "$SOURCE" -prune -empty 2>/dev/null )" ]; then
	echo "${CYN}$SOURCE is empty. Nothing to do.${NC}"
	break
    fi
    echo "${YEL}Renaming all files in $SOURCE to $FILE_FMT using $tag... ${NC}"
    exiftool "-filename<$tag" -dateFormat "$FILE_FMT" -ext "*" $COMMON_OPTS "$SOURCE"
    echo "${YEL}Moving all image files in $SOURCE to $IMG_DIR_FMT using $tag... ${NC}"
    exiftool "-directory<$tag" -dateFormat "$IMG_DIR_FMT" $IMG_FILE_EXT_OPTS $COMMON_OPTS "$SOURCE"
    echo "${YEL}Moving all video files in $SOURCE to $VID_DIR_FMT using $tag... ${NC}"
    exiftool "-directory<$tag" -dateFormat "$VID_DIR_FMT" $VID_FILE_EXT_OPTS $COMMON_OPTS "$SOURCE"
    echo "${YEL}Moving all audio files in $SOURCE to $AUDIO_DIR_FMT using $tag... ${NC}"
    exiftool "-directory<$tag" -dateFormat "$AUDIO_DIR_FMT" $AUDIO_FILE_EXT_OPTS $COMMON_OPTS "$SOURCE"
done

"$THIS_DIR/find_file_types.sh" "$IMG_DESTINATION" video
"$THIS_DIR/find_file_types.sh" "$VID_DESTINATION" img
