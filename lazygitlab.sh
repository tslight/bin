#!/usr/bin/env bash

ACCESS_TOKEN="$(cat "$HOME"/.gitlab.api.key)"
DEST="$HOME"/src/oe/gitlab
LIBS="$HOME"/bin/lib/bash

DEPS=(
    "ask"
    "chkdirs"
    "colors"
)

GITGROUPS=(
    "be"
    "ds"
)

get_deps () {
    for d in "${DEPS[@]}"; do
	if [[ -f "$LIBS/$d" ]]; then
	    source "$LIBS/$d"
	else
	    echo "${RED}Can't find $d library.${NC}"
	    exit 1
	fi
    done
}

clone_repo () {
    local g="$1" r="$2" repo

    repo="${r#*/}"       # remove up to and including slash
    repo="${repo%*.git}" # remove from dot onwards

    if [[ -d "$HOME/$repo/.git" ]]; then
	echo "${YELLOW}$repo${GREEN} already cloned to ${YELLOW}$HOME/$repo.${NC}"
    elif [[ -d "$DEST/$repo/.git" ]]; then
	echo "${YELLOW}$repo${GREEN} already cloned to ${YELLOW}$DEST/$repo.${NC}"
    elif [[ -d "$DEST/$g/$repo/.git" ]]; then
	echo "${YELLOW}$repo${GREEN} already cloned to ${YELLOW}$DEST/$g/$repo.${NC}"
    else
	if ask "${MAGENTA}Clone $r to $DEST/$g/$repo? ${NC}"; then
	    echo "${CYAN}Cloning $repo...${NC}"
	    if git clone -q "$r" "$DEST/$g/$repo"; then
		echo "${YELLOW}Successfully cloned $repo.${NC}"
	    else
		echo "${RED}Failed to clone $repo.${NC}"
	    fi
	fi
    fi
}

main () {
    local perlregex
    get_deps
    get_colors

    [[ "$OSTYPE" =~ linux.*|msys ]] && perlregex="P" || perlregex="E"

    for g in "${GITGROUPS[@]}"; do
	echo
	if chkdirs -m "$DEST/$g"; then
	    url="https://gitlab.com/api/v4/groups/$g/projects"
	    json="$(curl -s --header "PRIVATE-TOKEN: $ACCESS_TOKEN" "$url")"
	    repos=($(echo "$json" |\
			 grep -"${perlregex}"o '"ssh_url_to_repo":(\d*?,|.*?[^\\]",)' |\
			 awk -F '"' '{print $4}'))

	    for r in "${repos[@]}"; do
		clone_repo "$g" "$r"
	    done
	else
	    echo "${RED}Failed to create destination directory at $g.${NC}"
	fi

	# echo on last element
	[[ "$g" == "${GITGROUPS[${#GITGROUPS[@]}-1]}" ]] && echo
    done
}

main
