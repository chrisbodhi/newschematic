#!/bin/sh
# Install Hugo, https://gohugo.io/
# adapted from https://github.com/codeship/scripts/blob/master/packages/hugo.sh
#
HUGO_VERSION="0.58.3"
HUGO_DIR=${HUGO_DIR:="$HOME/hugo"}

set -e
CACHED_DOWNLOAD="${HOME}/cache/hugo_${HUGO_VERSION}_linux_amd64.tar.gz"

mkdir -p "${HUGO_DIR}" && echo "Made directory ${HUGO_DIR}"
wget -v --continue --output-document "${CACHED_DOWNLOAD}" "https://github.com/gohugoio/hugo/releases/download/v${HUGO_VERSION}/hugo_${HUGO_VERSION}_Linux-64bit.tar.gz"

tar -xaf "${CACHED_DOWNLOAD}" --directory "${HUGO_DIR}"

# Check that everything worked
${HOME}/hugo/hugo version
