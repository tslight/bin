#!/usr/bin/env bash
ETC="${HOME}/src/tspub/devops/etc"

usage() {
    echo "
$(basename "$0") [DIRECTORY] [-a/--all] [-h/--help]

Run Emacs in batch mode to either tangle the contents of a specific directory
or all my org mode configuration files.
"
}

refresh_packages () {
    emacs -Q --batch --eval '(package-refresh-contents)'
}

tangle_tangles () {
    emacs -Q --batch --eval '(org-babel-load-file "'$ETC'/emacs/site-lisp/my-tangles.org")'
}

tangle_all () {
    refresh_packages && tangle_tangles && \
    emacs -Q --batch -l ~/.emacs.d/site-lisp/my-tangles.el --eval '(my/tangle-all)'
}

tangle_dir () {
    local dir="$1"

    [[ -z "$dir" ]] && { echo "Invalid directory"; exit 1; }
    [[ "$dir" =~ .*emacs.* ]] && { refresh_packages; tangle_tangles; }

    emacs -Q --batch -l ~/.emacs.d/site-lisp/my-tangles.el\
	  --eval '(my/tangle-directory "'$dir'")'
}

main () {
    if [[ -z "$1" ]]; then
	tangle_all
    else
	case "$1" in
	    -a|--all)
		tangle_all
		;;
	    -h|--help)
		usage
		;;
	    *)
		tangle_dir "$1"
		;;
	esac
    fi
}

main "$@"
