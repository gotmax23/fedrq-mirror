#!/bin/bash -x
# Copyright (C) 2025 Maxwell G <maxwell@gtmx.me>
# SPDX-License-Identifier: GPL-2.0-or-later
set -euo pipefail

exec $EDITOR src/fedrq/backends/base/__init__.py src/fedrq/backends/*/backend/__init__.py
