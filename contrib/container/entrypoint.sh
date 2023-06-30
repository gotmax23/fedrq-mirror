#!/usr/bin/bash
# Copyright (C) 2023 Maxwell G <maxwell@gtmx.me>
# SPDX-License-Identifier: GPL-2.0-or-later
set -euo pipefail

# Refresh redhat.repo on container startup.
# fedrq doesn't deal with dnf plugins such as subman,
# but calling a dnf command will.

dnf repolist &>/dev/null
exec "$@"
