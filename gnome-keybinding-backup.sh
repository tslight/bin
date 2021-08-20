#!/usr/bin/env bash

# Backs up and restores gnome3 keybindings

set -e

if [[ $1 == 'backup' ]]; then
    if [[ -d "$2" ]]; then
        dconf dump '/org/gnome/desktop/wm/keybindings/' > "$2/gnome-keybindings.dconf"
        dconf dump '/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/' > "$2/gnome-custom-keybindings.dconf"
        echo "Backup keybindings to $2"
        exit 0
    else
        echo "$2 doesn't exist... Aborting!"
    fi
fi

if [[ $1 == 'restore' ]]; then
    if [[ -f "$2/gnome-keybindings.dconf" && -f "$2/gnome-custom-keybindings.dconf" ]]; then
        dconf load '/org/gnome/desktop/wm/keybindings/' < "$2/gnome-keybindings.dconf"
        dconf load '/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/' < "$2/gnome-custom-keybindings.dconf"
        echo "Restored keybindings from $2"
        exit 0
    else
        echo "$2 doesn't exist... Aborting!"
    fi
fi

echo "$(basename $BASH_SOURCE) [backup|restore] [path/to/backup/directory]"
