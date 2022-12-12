#!/usr/bin/bash -x
# SPDX-FileCopyrightText: 2022 Maxwell G <gotmax@e.email>
# SPDX-License-Identifier: GPL-2.0-or-later

set -euo pipefail
archivename="$(spectool -s0 fedrq.spec | sd '^.*#/(\S+)\.tar.gz$' '$1')"
git archive -o "${archivename}.tar.gz" --prefix "${archivename}/" HEAD
fedpkg --release rawhide srpm
