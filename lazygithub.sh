#!/usr/bin/env bash

#set -eo pipefail # Fail fast and be aware of exit codes.

[ "$(uname)" == "OpenBSD" ] && TERM=linux # otherwise colors don't work...

readonly NC=$(tput sgr0)
readonly BLACK=$(tput setaf 0)
readonly RED=$(tput setaf 1)
readonly GREEN=$(tput setaf 2)
readonly YELLOW=$(tput setaf 3)
readonly BLUE=$(tput setaf 4)
readonly MAGENTA=$(tput setaf 5)
readonly CYAN=$(tput setaf 6)
readonly WHITE=$(tput setaf 7)

readonly DIRS=($(find "$HOME" -maxdepth 10 -type d (-path ~/AppData -o-path ~/Library -o -path ~/OneDrive -o -path ~/.dbus -o -path ~/.local) -prune -o name ".git" -print | sed 's/\.git//g' 2>&1))

readonly URLS=("git@github.com")

usage () {
    echo "
    $(basename "$0") [GIT COMMAND] [USER]

    AUTOMATE TEDIOUS GIT TASKS FOR ALL LOCAL REPOS
    ----------------------------------------------

    Any valid git command can be given as an argument, it will be applied to all git
    repos in the users $HOME.

    Additional custom arguments initiate the following tasks:

    [scp]

    Stage all changes. Commit with "lazygitpush" message. Push changes to master.

    [urls] [add] [rm] [user]

    Add or remove additional git remote urls to push to, takes a username as 3rd
    argument. Defined in hardcoded array.

    [clone] [user]

    Clone all git repositories for a given GitHub user. Checks for ssh public key
    authentication to GitHub and if found, clones via ssh. Otherwise fall back to
    https.

    Repositories must be public.

    [backup]

    Zips up all your repos, adds them to a directory and then zips that up.
    "
}

# check for existence of a directory and if it doesn't exist create it.
check_dir () {
    local dir="$1"

    if [[ ! -d "$dir" ]]; then
	if ! mkdir -p "$dir"; then
	    echo "Error creating $dir";
	    exit 1
	fi
    fi
}

lazygit () {
    local arg="$1" dir output

    for dir in "${DIRS[@]}"; do
	repo=$(basename "$dir")
	output=""
	if [[ "$arg" == "scp" ]]; then
	    if git -C "$dir" status | grep -Eqi "untracked|modified"; then
		output+="$(git -C "$dir" add -A 2>&1 | sed '/^$/d')"
		output+="$(git -C "$dir" commit -m "lazygitpush" 2>&1 | sed '/^$/d')"
		output+="$(git -C "$dir" push -q origin master 2>&1 | sed '/^$/d')"
	    fi
	else
	    output+="$(git -C "$dir" $arg 2>&1 | sed '/^$/d')" # don't quote git arg as double params break
	fi
	[[ "$output" == "" ]] && output="Already up to date."
	if [[ "$output" =~ [Aa]lready.up.to.date ]]; then
	    output="${output,,}"
	    echo "${CYAN}$repo ${YELLOW}$output${NC}"
	else
	    echo "${CYAN}$repo${NC}"
	    echo "${output[@]}"
	fi
    done
}

backup () {
    local dest="$1"
    local date="$(date +%Y-%m-%d)"
    local bkupname="gitbkup"
    local bkupdir="$bkupname-$date"

    for d in "${DIRS[@]}"; do
	reponame=$(basename "$d")
	[[ ! -d "$bkupdir" ]] && mkdir "$bkupdir"
	if zip -r "$bkupdir/$reponame-$date.zip" "$d" &>/dev/null; then
	    echo "${CYAN}Sucessfully archived ${YELLOW}$reponame${NC}"
	else
	    echo "${RED}Oops. Something went wrong..${NC}"
	fi
    done

    if zip -r "$bkupdir.zip" "$bkupdir" &>/dev/null; then
	echo "${MAGENTA}Created $bkupdir.zip at $PWD"
	rm -rf "$bkupdir"
    else
	echo "${RED}Oops. Something went wrong..${NC}"
    fi

    if [[ ! -z "$dest" ]]; then
	if mv "$PWD/$bkupdir.zip" "$dest"; then
	    echo "${MAGENTA}Moved $bkupdir.zip to $dest.${NC}"
	else
	    echo "{RED}Failed to move $bkupdir.zip to $dest.${NC}"
	fi
    fi
}

urls () {
    local arg="$1" name="$2" fullname dir url

    for dir in "${DIRS[@]}"; do
	repo=$(basename "$dir")
	echo
	echo "${MAGENTA}Editing push urls of $repo...${NC}";
	for url in "${URLS[@]}"; do
	    flag=0
	    fullname="$url:$name/$repo.git"
	    if [ "$arg" == "add" ]; then
		if git -C "$dir" remote -v | grep -q "$fullname (push)"; then
		    echo "${YELLOW}$fullname is already added.${NC}"
		else
		    ((flag++))
		    echo "${YELLOW}Adding $url as push origin on $repo...${NC}";
		    git -C "$dir" remote set-url --add --push origin "$fullname"
		fi
	    elif [ "$arg" == "rm" ]; then
		if git -C "$dir" remote -v | grep -q "$fullname (push)"; then
		    echo "${YELLOW}Removing $url as push origin on $repo...${NC}";
		    git -C "$dir" remote set-url --delete --push origin "$fullname"
		else
		    echo "${YELLOW}$fullname not a push origin. Nothing to do.${NC}"
		fi
	    fi
	done
	echo "${CYAN}Finished editing push urls of $repo...${NC}";
	if [ "$arg" == "add" ] && [ "$flag" -gt 0 ]; then
	    echo
	    git -C "$dir" remote -v
	    echo
	    echo "${MAGENTA}Pushing to new origins of $repo...${NC}";
	    git -C "$dir" push --all -u
	    echo "${CYAN}Finished pushing to new origins or $repo.${NC}"
	fi
	[ "$dir" == "${DIRS[-1]}" ] && echo
    done
}

get_repos () {
    local user="$1"
    ssh -T git@github.com &> /dev/null
    local ssh_auth="$?"
    local apiurl="https://api.github.com/users/$user/repos?page=1&per_page=100"

    if [[ "$ssh_auth" -eq "1" ]]; then
	REPO_URLS=($(curl -s "$apiurl" | awk -F '\"' '/ssh_url/ {print $4}'))
	# use tr to line break on each space, and then seperate awk on / & .
	REPO_NAMES=($(echo "${REPO_URLS[@]}" | tr ' ' '\n' | awk -F '[\\/\\.]' '{print $3}'))
    else
	REPO_URLS=($(curl -s "$apiurl" | awk -F '\"' '/clone_url/ {print $4}'))
	# use tr to line break on each space, and then seperate awk on / & .
	REPO_NAMES=($(echo "${REPO_URLS[@]}" | tr ' ' '\n' | awk -F '[\\/\\.]' '{print $6}'))
    fi
}

check_clone () {
    local repo="$1" repo_name="$2" path="$3"

    if [ -d "$path/$repo_name/.git" ]; then
	echo "${CYAN}Not cloning. ${YELLOW}$repo_name already exists.${NC}"
	return 1
    else
	[ -d "$path" ] || mkdir -p "$path"
	return 0
    fi
}

clone () {
    local user="$1"

    get_repos "$user"

    # ! means $i is index, not value
    for i in "${!REPO_URLS[@]}"; do
	repo="${REPO_URLS[$i]}"
	repo_name="${REPO_NAMES[$i]}"
	# if [[ "$repo_name" =~ ^bin$|^etc$|^lib$ ]]; then
	#     path="$HOME"
	# else
	#     path="$HOME/src"
	# fi
	path="$HOME/src/github"
	if check_clone "$repo" "$repo_name" "$path"; then
	    echo "${MAGENTA}Cloning $repo_name...${NC}"
	    git clone -q "$repo" "$path/$repo_name"
	    echo "${CYAN}Finished cloning $repo_name.${NC}"
	fi
    done
}

main () {
    if [ ! -z "$1" ]; then
	case "$1" in
	    backup)
		backup "$2"
		;;
	    clone)
		if [[ ! -z "$2" ]]; then
		    clone "$2"
		else
		    echo
		    echo "${RED}Cloning needs a user name as an argument.${NC}"
		    usage
		fi
		;;
	    urls)
		if [[ ! -z "$2" && ! -z "$3" ]]; then
		    urls "$2" "$3"
		else
		    echo
		    echo "This function needs two arguments. [add] or [rm] [username]."
		    usage
		fi
		;;
	    *)
		lazygit "$1"
		;;
	esac
    else
	echo
	echo "${RED}This script needs an argument.${NC}"
	usage
    fi
}

main "$@"
