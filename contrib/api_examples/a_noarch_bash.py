#!/usr/bin/env python3
# SPDX-License-Identifier: Unlicense
# SPDX-FileCopyrightText: None

# Roughly equivalent to:
#     fedrq whatrequires --arch=noarch -b rawhide -r buildroot bash | grep '^a'

from fedrq.backends.base import RepoqueryBase
from fedrq.config import RQConfig, get_config

# Load config from filesystem and override some options
config: RQConfig = get_config(backend="libdnf5")

# Query the Fedora Rawhide koji buildroot repositories
# This supports any release configuration builtin to fedrq
# or configured on your local system.
rq: RepoqueryBase = config.get_rq("rawhide", "buildroot")

# Get all noarch packages that start with 'a' and depend on bash
query = rq.query(
    name__glob="a*", arch="noarch", requires=rq.query(name="bash", arch="notsrc")
)
# By using sorted(), you'll get (relatively) consistent ordering between backends
for package in sorted(query):
    print(package)
