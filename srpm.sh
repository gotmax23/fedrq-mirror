#!/usr/bin/bash -x
# SPDX-FileCopyrightText: 2022 Maxwell G <gotmax@e.email>
# SPDX-License-Identifier: GPL-2.0-or-later

set -euo pipefail

outdir="${1:-results_fedrq}"
projectdir="$(pwd)"
specfile="fedrq.spec"
lastref="v0.0.1"
RELEASE="${RELEASE-rawhide}"

mkdir -p "${outdir}"
find -maxdepth 1 \( -name 'fedrq-*.tar.gz' -o -name '*.src.rpm' \) -delete -print
find "${outdir}" -maxdepth 1 -type f -name '*.src.rpm' -delete -print

origversion="$(rpmspec -q --qf '%{version}\n' "${specfile}" | sed 's|~1$||')"
if [ "$(git rev-list -n1 ${lastref})" = "$(git rev-parse HEAD)" ]; then
    newversion="${origversion}"
else
    newversion="$(printf '%s^%s.%s\n' \
                "${origversion}" \
                "$(( $(git log --oneline "${lastref}..HEAD" | wc -l) + 1 ))" \
                "$(git show -s --pretty=%cs.%h | sed 's|-||g')"
            )"
fi
archivename="fedrq-${newversion}"

cp "${specfile}" "${specfile}.bak"
sed "s|^\(Version: *\)[^ ]*$|\1${newversion}|" -i "${specfile}"

git archive -o "${archivename}.tar.gz" --prefix "${archivename}/" HEAD

fedpkg --name fedrq --release "${RELEASE}" srpm
cp -p *.src.rpm "${outdir}"

[ -z "${keep_spec-}" ] && mv "${specfile}.bak" "${specfile}" || :
