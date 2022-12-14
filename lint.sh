#!/usr/bin/bash
# SPDX-FileCopyrightText: 2022 Maxwell G <gotmax@e.email>
# SPDX-License-Identifier: GPL-2.0-or-later

set -eu

if [ "${1-}" == "--check" ]; then
  c="--check"
else
  c=""
fi

r=0
run() {
    echo "**** Running: $@ ****"
    "$@" || { r=$?; echo "**** Failed: $r ****" ; }
    echo
}


run isort fedrq ${c}
run black fedrq ${c}
run flake8 --max-line-length 89 fedrq
run mypy fedrq
run reuse lint
exit $r
