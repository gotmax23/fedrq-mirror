#!/usr/bin/bash -x
# SPDX-FileCopyrightText: 2022 Maxwell G <gotmax@e.email>
# SPDX-License-Identifier: GPL-2.0-or-later

set -euo pipefail

outdir="${1:-.}"
projectdir="$(dirname "$(readlink -f "${0}")")"
specfile="${projectdir}/fedrq.spec"

mkdir -p "${outdir}"
find "${outdir}" \
    -maxdepth 1 \( -name 'fedrq-*.tar.gz' -o -name '*.src.rpm' \) \
    -delete -print
fclogr --debug dev-srpm \
    -r $(git describe --abbrev=0 HEAD) \
    ${keep_spec+"--keep"} -o ${outdir} ${specfile}
