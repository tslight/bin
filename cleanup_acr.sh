#!/usr/bin/env bash
#
# Reference:
#
# https://docs.microsoft.com/en-us/azure/container-registry/container-registry-delete
#
# Automated alternative to running this script:
#
# https://docs.microsoft.com/en-us/azure/container-registry/container-registry-auto-purge
# https://docs.microsoft.com/en-us/azure/container-registry/container-registry-tasks-scheduled
#

usage() {
    echo "
$(basename "$0") [-r] [REGISTRY] [-i] [REPOSITORY/IMAGE] [-d] [DATE] [-u] [-o]

Cleanup old or untagged (orphaned) manifests/images in an Azure Container Registry.

-u : Show and/or delete untagged (orphaned) images.
-o : Show and/or delete images older than -d [DATE].

Date must be in the following format: YYYY-MM-DD

For example - to show and delete all images older than 2nd January 1970 - run:

$(basename "$0") -r RegistryName -i Repository/Image -d 1970-01-02 -o

Date is not necessary if you are only looking to delete untagged images with -u.
"
}

ask() {
    local question="$1"

    while :; do
	read -rep "$question " ans
	case $ans in
	    [Yy][Ee][Ss]|[Yy])
		return 0
		;;
	    [Nn][Oo]|[Nn])
		return 1
		;;
	    [Qq][Uu][Ii][Tt]|[Qq])
		exit 0
		;;
	    *)
		echo "$ans is invalid. Enter (y)es, (n)o or (q)uit."
		;;
	esac
    done
}

###############################################################################
#                                OLD MANIFESTS                                #
###############################################################################

get_old_manifests() {
    local registry="$1" repository="$2" older_than="$3"

    echo "Getting manifests from $registry/$repository last updated before $older_than..."
    IFS=$'\n'
    OLD_MANIFESTS=($(az acr repository show-manifests \
			--name "$registry" \
			--repository "$repository" \
			--orderby time_asc \
			--output tsv \
			--detail \
			--query "[?lastUpdateTime < '$older_than'].[digest, tags, createdTime, lastUpdateTime]"))
    unset IFS

    if [[ "${#OLD_MANIFESTS[@]}" -lt 1 ]]; then
	echo "No manifests last updated before $older_than in $registry/$repository."
	return 1
    fi
}

show_old_manifests() {
    local registry="$1" repository="$2" older_than="$3"

    if ask "${#OLD_MANIFESTS[@]} older than $older_than in $registry/$repository. View?"; then
	for manifest in "${OLD_MANIFESTS[@]}"; do
	    echo "$manifest"
	done | "$PAGER"
    fi
}

delete_old_manifests() {
    local registry="$1" image="$2" older_than="$3"

    if ask "Delete all manifests older than $older_than in $registry/$image?"; then
	for manifest in "${OLD_MANIFESTS[@]}"; do
	    manifest="$(echo $manifest | awk '{print $1}')"
	    az acr repository delete \
	       --name "$registry" \
	       --image "$image@$manifest" \
	       --yes
	done
    fi
}

###############################################################################
#                          UNTAGGED (ORPHANED) IMAGES                         #
###############################################################################

get_untagged_images() {
    local registry="$1" repository="$2"

    echo "Getting untagged/orphaned images from $registry/$repository..."
    IFS=$'\n'
    UNTAGGED_IMAGES=($(az acr repository show-manifests \
			  --name "$registry" \
			  --repository "$repository" \
			  --orderby time_asc \
			  --output tsv \
			  --detail \
			  --query "[?tags[0]==null].[digest, tags, createdTime, lastUpdateTime]"))
    unset IFS

    if [[ "${#UNTAGGED_IMAGES[@]}" -lt 1 ]]; then
	echo "No untagged/orphaned manifests in $registry/$repository."
	return 1
    fi
}

show_untagged_images() {
    local registry="$1" repository="$2"

    if ask "${#UNTAGGED_IMAGES[@]} untagged/orphaned images in $registry/$repository. View?"; then
	for image in "${UNTAGGED_IMAGES[@]}"; do
	    echo "$image"
	done | "$PAGER"
    fi
}

delete_untagged_images() {
    local registry="$1" image="$2"

    if ask "Delete all untagged/orphaned images in $registry/$image?"; then
	for manifest in "${UNTAGGED_IMAGES[@]}"; do
	    manifest="$(echo $manifest | awk '{print $1}')"
	    az acr repository delete \
	       --name "$registry" \
	       --image "$image@$manifest" \
	       --yes
	done
    fi
}

###############################################################################
#                                     MAIN                                    #
###############################################################################

main_old() {
    [ -z "$3" ] && { printf "\nNO DATE PROVIDED!\n"; usage; exit 1; }
    get_old_manifests "$@" && \
	show_old_manifests "$@" && \
	delete_old_manifests "$@"
}

main_untagged() {
    get_untagged_images "$@" && \
	show_untagged_images "$@" && \
	delete_untagged_images "$@"
}

main() {
    local -a functions=()

    while getopts ":r:i:d:ouh" opt; do
	case $opt in
	    h) usage
	       exit 0
	       ;;
	    r) registry="$OPTARG"
	       ;;
	    i) image="$OPTARG"
	       ;;
	    d) date="$OPTARG"
	       ;;
	    o) functions+=(main_old)
	       ;;
	    u) functions+=(main_untagged)
	       ;;
	    \?) echo "INVALID OPTION -$OPTARG" >&2
		;;
	esac
    done

    # date defaults to 1 month ago
    [[ -z "$date" ]] && date="$(date --date="$(date +%Y-%m-%d) -1 month" '+%Y-%m-%d')"
    # image defaults to iterating over all repos in registry
    [[ -z "$image" ]] && repos=($(az acr repository list --name "$registry" --output tsv))

    if [ "${#functions[@]}" -lt 1 ]; then
	printf "\nNothing to do!\n"
	usage
    else
	for i in "${!functions[@]}"; do
	    if [[ "${#repos[@]}" -gt 0 ]]; then
		for r in "${repos[@]}"; do
		    echo "Running cleanup on $r..."
		    ${functions[$i]} "$registry" "$r" "$date"
		done
	    else
		${functions[$i]} "$registry" "$image" "$date"
	    fi
	done
    fi
}

main "$@"
