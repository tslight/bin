#!/usr/bin/env bash

generate_ssh_keys() {
    # https://unix.stackexchange.com/a/135090
    # cat /dev/zero | ssh-keygen -q -N ""
    # https://unix.stackexchange.com/a/69318
    ssh-keygen -t rsa -f "$HOME"/.ssh/id_rsa -q -N "" # 0>&- # don't overwrite without prompt

    command -v xclip &>/dev/null || sudo apt install xclip
    xclip < "$HOME"/.ssh/id_rsa.pub
    echo; cat "$HOME"/.ssh/id_rsa.pub

    printf "
    The key above has been copied to your clipboard.
    Paste it into the form at https://gitlab.com/profile/keys
    \n" && read -n1 -rs -p "Press any key to continue..." key && echo
}

generate_ssh_keys
