#!/usr/bin/bash -x
# SPDX-FileCopyrightText: 2023 Maxwell G <maxwell@gtmx.me>
# SPDX-License-Identifier: GPL-2.0-or-later

set -euo pipefail

check_license() {
    local whl sdist
    whl="$(bsdtar tf dist/*.whl)"
    sdist="$(bsdtar tf dist/*.tar.gz)"
    for license in "GPL-2.0-or-later.txt" "Unlicense.txt" "MIT.txt" "PSF-2.0.txt"; do
        grep ${license} <<< "${whl}"
        grep ${license} <<< "${sdist}"
    done
}


rm -rf dist/* || :
python -m flit build
twine check --strict dist/*
check_license
twine upload -s -i "$(git config user.email)" --non-interactive -u __token__ dist/*
git push --follow-tags
hut git artifact upload dist/*
copr build fedrq fedrq.spec --nowait
sed -i 's|^\(version.*=.*\)"$|\1.post0"|' pyproject.toml
git add pyproject.toml
git commit -S -m "Post release version bump"
