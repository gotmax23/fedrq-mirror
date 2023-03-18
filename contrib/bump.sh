#!/usr/bin/bash -x
# SPDX-FileCopyrightText: 2022 Maxwell G <gotmax@e.email>
# SPDX-License-Identifier: GPL-2.0-or-later

set -euo pipefail

if [ "$#" -eq 1 ]; then
    oldversion=""
    newversion="${1}"
elif [ "$#" -eq 2 ]; then
    oldversion="${1}"
    newversion="${2}"
else
    echo "Argument error"
    exit 1
fi

rpmdev-bumpspec -c "Release ${newversion}" --new "${newversion}" fedrq.spec
sed -i 's|^version.*$|version = "'"${newversion}"'"|' pyproject.toml

if ! grep "fedrq ${newversion}" NEWS.md -q; then
    { cat FRAG.md && echo && cat NEWS.md ;} | sponge NEWS.md
fi
git add pyproject.toml fedrq.spec NEWS.md
git commit -S -m "Release ${newversion}"
git tag -a "v${newversion}" -F FRAG.md
