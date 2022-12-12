#!/usr/bin/bash -x
# SPDX-FileCopyrightText: 2022 Maxwell G <gotmax@e.email>
# SPDX-License-Identifier: GPL-2.0-or-later

set -euo pipefail

outdir="${1:-results_fedrq}"
projectdir="$(pwd)"
specfile="fedrq.spec"
lastref="7eb724c"

mkdir -p "${outdir}"
find -maxdepth 1 \( -name 'fedrq-*.tar.gz' -o -name '*.src.rpm' \) -delete -print
find "${outdir}" -maxdepth 1 -type f -name '*.src.rpm' -delete -print

origversion="$(rpmspec -q --qf '%{version}\n' "${specfile}" | sed 's|~1$||')"
newversion="$(printf '%s~%s.%s\n' \
                "${origversion}" \
                "$(git show -s --pretty=%cs.%h | sed 's|-||g')" \
                "$(git log --oneline "${lastref}..HEAD" | wc -l)")"
archivename="fedrq-${newversion}"

sed "s|^\(Version: *\)[^ ]*$|\1${newversion}|" -i "${specfile}"

git archive -o "${archivename}.tar.gz" --prefix "${archivename}/" HEAD

fedpkg --name fedrq --release rawhide srpm
cp -p *.src.rpm "${outdir}"
