#!/usr/bin/env bash

SCRIPT=$(basename "$0")

usage() {
    echo "
Usage: $SCRIPT [REPO_PATH] [REPO_BRANCH] [TERRAFORM_PATH]

Add and push to Azure Function App Git remote.

Uses the output from from a terraform state file in [TERRAFORM_PATH] to derive
an Azure Function App Git URL. Adds that URL as a Git remote in [REPO_PATH] and
then pushes [REPO_BRANCH] to the Azure Function App Git remote.
"
}

[[ -d "$1" ]] && REPO_PATH="$1" || { usage; exit 1; }
[[ -z "$2" ]] && { usage; exit 1; } || BRANCH="$2"
[[ -d "$3" ]] && TF_PATH="$3" || { usage; exit 1; }

get_url() {
    local fa_name fa_user fa_pass az_url

    cd "$TF_PATH" || exit 1

    fa_name="$(terraform output functionapp)"
    fa_user="$(terraform output -json functionapp_credential | jq -r '.[0].username')"
    fa_pass="$(terraform output -json functionapp_credential | jq -r '.[0].password')"
    az_url="https://${fa_user}:${fa_pass}@${fa_name}.scm.azurewebsites.net:443/${fa_name}.git"

    echo "$az_url"
}

chkurl() {
    local url="$1" regex

    regex="^https\\:\\/\\/\\$.*\\:[A-z0-9]+\\@.*scm\\.azurewebsites\\.net\\:443\\/.*\\.git$"

    if [[ "$url" =~ $regex ]]; then
	echo "$url is valid."
    else
	echo "$url is invalid. Aborting"
	exit 1
    fi
}

add_url() {
    local url="$1"

    git -C "$REPO_PATH" remote -v | grep -q azure && git -C "$REPO_PATH" remote remove azure
    git -C "$REPO_PATH" remote add azure "$url"
    git -C "$REPO_PATH" remote -v
}

chkadd() {
    local url="$1"

    if git -C "$REPO_PATH" remote -v | grep -q azure; then
	echo "Successfully added $url to $REPO_PATH."
    else
	echo "Failed to add $url to $REPO_PATH. Aborting."
    fi
}

push() {
    local url="$1"

    if git -C "$REPO_PATH" branch | grep -q "$BRANCH"; then
	echo "$BRANCH exists in $REPO_PATH. Pushing..."
	if git -C "$REPO_PATH" push azure "$BRANCH":master; then
	    echo "Successfully pushed $BRANCH to $url."
	    exit 0
	else
	    echo "Failed to push $BRANCH to $url."
	    exit 1
	fi
    else
	echo "$BRANCH doesn't exist in $REPO_PATH. Aborting."
	exit 1
    fi
}

main() {
    local url

    url="$(get_url)"
    # chkurl "$url"
    add_url "$url"
    chkadd "$url"
    push "$url"
}

main
