#!/usr/bin/bash
# SPDX-FileCopyrightText: 2022 Maxwell G <gotmax@e.email>
# SPDX-License-Identifier: GPL-2.0-or-later

set -eu

cd "$(dirname "$(readlink -f "$0")")"

if [ "${1-}" == "--check" ]; then
  c="--check"
else
  c=""
fi

r=0
run() {
    printf "**** Running:"
    for arg in "$@"; do
        printf " '%s'" "${arg}"
    done
    echo " ****"
    "$@" || { r=$?; echo "**** Failed: $r ****" ; }
    echo
}

run isort --add-import "from __future__ import annotations" ${c} src/fedrq/
run isort ${c} tests/
run black ${c} src/fedrq tests/
run flake8 --max-line-length 89 src/fedrq/
run mypy --enable-incomplete-feature=Unpack src/fedrq/
run reuse lint
exit $r
