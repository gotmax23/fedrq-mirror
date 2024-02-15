#!/usr/bin/bash

# SPDX-FileCopyrightText: 2022 Maxwell G <gotmax@e.email>
# SPDX-License-Identifier: GPL-2.0-or-later

set -euo pipefail
HERE="$(readlink -f "$(dirname "${0}")")"
cd "${HERE}"

# Return 1 if the repodata is up to date
# Return 0 if the repodata needs to be regenerated
regenerate() {
    [ "${1-}" = "--force" ] && return 0

    { [ -f "built" ] && [ -d "repo/repodata" ]; } || return 0

    local built_files fs_files
    built_files="$(awk '{print $2}' built | sort)"
    fs_files="$(find specs/ -name '*.spec' | sort)"
    [ "${built_files}" = "${fs_files}" ] || return 0

    sha256sum -c built &> /dev/null || return 0

    return 1
}

for repo in repos/*; do
    cd "${repo}"
    specs="$(find specs -name '*.spec')"
    if regenerate "$@"; then
        rm -rf repo
        echo "${specs}"
        while read -r spec; do
            specdir="$(dirname "${spec}")"
            base_specdir="$(basename "${specdir}")"
            rpmbuild -ba --nodeps \
                -D "_srcrpmdir %(pwd)/repo/SRPMS/${base_specdir}" \
                -D "_rpmdir %(pwd)/repo/RPMS/${base_specdir}" \
                -D '_build_name_fmt %%{NAME}-%{?EPOCH:%%{EPOCH}:}%%{VERSION}-%%{RELEASE}.%%{ARCH}.rpm' \
                -D "_sourcedir ${specdir}" \
                -D "_specdir ${specdir}" \
                -D 'dist .fc36' \
                "${spec}"
        done <<< "${specs}"
        createrepo_c ./repo
        xargs sha256sum > built <<< "${specs}"
    cd -
    fi
done
