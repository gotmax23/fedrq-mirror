#!/usr/bin/bash -x

# SPDX-FileCopyrightText: 2022 Maxwell G <gotmax@e.email>
# SPDX-License-Identifier: GPL-2.0-or-later

set -eu
if [ "${check-}" == "true" ]; then
  c="--check"
else
  c=""
fi
r=0

fail() {
  r=1
}


isort fedrq ${c} || fail
black fedrq ${c} || fail
flake8 --max-line-length 89 fedrq || fail
mypy fedrq || fail
exit $r
