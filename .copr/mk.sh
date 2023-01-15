#!/usr/bin/bash -x
# SPDX-FileCopyrightText: 2023 Maxwell G <gotmax@e.email>
# SPDX-License-Identifier: GPL-2.0-or-later

set -euo pipefail
SUDO=""
if command -v sudo; then
    SUDO=sudo
fi

${SUDO} dnf install -y --setopt=install_weak_deps=False \
        git-core fedpkg rpmdevtools python3-specfile
python3 -m venv copr_venv --system-site-packages
. ./copr_venv/bin/activate
./copr_venv/bin/pip install 'git+https://git.sr.ht/~gotmax23/fclogr#main'
./srpm.sh "${1}"
deactivate
rm -rf copr_venv/
ls -al "${1}"
