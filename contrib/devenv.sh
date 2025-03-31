#!/bin/bash -x
# Copyright (C) 2025 Maxwell G <maxwell@gtmx.me>
# SPDX-License-Identifier: GPL-2.0-or-later

set -euo pipefail
if ! [ "${VIRTUAL_ENV+x}" ]; then
    virtualenv venv --system-site-packages
    . ./venv/bin/activate
fi
exec uv pip install -e '.[dev]' -c requirements/all.txt  ipython pytest-cov
