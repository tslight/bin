#!/usr/bin/env bash
readonly DATE="$(date +%Y-%m-%d)"

[ -n "$1" ] && GITROOT="$1" || GITROOT="$HOME/src"
[ -n "$2" ] && BACKUP_DEST="$2" || BACKUP_DEST="$HOME/Dropbox/Documents/gitbak"

NAME="$(basename "$GITROOT")"

[ -d "$BACKUP_DEST" ] || mkdir "$BACKUP_DEST"
[ -d "/tmp/$NAME-$DATE" ] || mkdir "/tmp/$NAME-$DATE"

readarray -d '' REPOS < <(find "$GITROOT" \
			       -maxdepth 10 \
			       -type d \
			       -name ".git" \
			       -print0 | \
			      sed 's/\/\.git//g')

for repo in "${REPOS[@]}"; do
    name="$(basename "$repo")"
    zip -qr "/tmp/$NAME-$DATE/$name-$DATE.zip" "$repo" && \
	echo "Sucessfully archived $name" || \
	    echo "Oops. Something went wrong.."
done

cd /tmp && zip -qr "$BACKUP_DEST/$NAME-$DATE.zip" "$NAME-$DATE" && \
    echo "Created $BACKUP_DEST/$NAME-$DATE.zip." ||
	echo "Oops. Something went wrong.."

rm -r "/tmp/$NAME-$DATE"
