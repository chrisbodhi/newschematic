#!/bin/sh

hugo --theme=hugo-goa
source .env
rsync -e "$(which ssh)" --bwlimit=2000 -av public/ "$DH_USER"@"$DH_HOST":newschematic.org

