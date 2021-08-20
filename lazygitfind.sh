#!/usr/bin/env bash
# Define colors to be used when echoing output
readonly NC=$(tput sgr0);
readonly BLACK=$(tput setaf 0);
readonly RED=$(tput setaf 1);
readonly GREEN=$(tput setaf 2);
readonly YELLOW=$(tput setaf 3);
readonly BLUE=$(tput setaf 4);
readonly MAGENTA=$(tput setaf 5);
readonly CYAN=$(tput setaf 6);
readonly WHITE=$(tput setaf 7);

REPOS=()

getrepos() {
    local parent="$1" longest=0

    while IFS= read -r repo; do
	REPOS+=("${repo%/.git}")
    done < <(find "$parent" -name ".git" -type d)
}

lazygit() {
    for repo in "${REPOS[@]}"; do
	# using $@ is probably pretty dangerous, but I'm feeling spicy today.
	if git -C "$repo" "$@"; then
	    echo "${CYAN}git -C $repo $@${GREEN} SUCCEEDED.${NC}"
	else
	    echo "${YELLOW}git -C $repo $@${RED} FAILED.${NC}"
	fi
    done
}

main() {
    if [[ -z "$*" ]]; then
	echo "No arguments provided."
	exit 1
    fi

    getrepos "$1"
    shift 1
    lazygit "$@"
}

main "$@"
