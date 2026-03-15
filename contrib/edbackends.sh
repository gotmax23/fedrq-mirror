#!/bin/bash -x

set -euo pipefail

exec $EDITOR src/fedrq/backends/base/__init__.py src/fedrq/backends/*/backend/__init__.py
