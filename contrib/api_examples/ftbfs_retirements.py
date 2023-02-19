#!/usr/bin/env python3
# SPDX-License-Identifier: Unlicense
# SPDX-FileCopyrightText: None

"""
This is a commented, fully typed example script showing fedrq's API.
It searches the Fedora repositories for packages that haven't been rebuilt
in the last few releases (i.e. Long Term FTBFS packages).
Based on https://github.com/hroncok/fedora-report-ftbfs-retirements.
"""
from __future__ import annotations

import argparse

from fedrq.backends.base import PackageCompat, PackageQueryCompat, RepoqueryBase
from fedrq.config import RQConfig, get_config

DEFAULT_RELEASES = ".fc36", ".fc37", ".fc38", ".fc39"
DEFAULT_IGNORES = (
    "dummy-test-package",
    "fedora-obsolete-packages",
    "fedora-release",
    "fedora-repos",
    "generic-release",
    "shim",
)


def parseargs() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-R",
        "--releases",
        nargs="*",
        help=f"DEFAULT: {DEFAULT_RELEASES}",
        default=DEFAULT_RELEASES,
    )
    args = parser.parse_args()
    return args


def main(*, releases: list[str]):
    # get_config() loads the configuration from the filesystem as explained in
    # fedrq(5).
    # Extra kwargs may be passed to get_config() to override certain values.
    # For example, you can pass `backend="libdnf5"` if you'd like to change the
    # default backend.
    config: RQConfig = get_config(backend="libdnf5")

    # Query the Fedora Rawhide mirrored repositories.
    # This supports any release configuration builtin to fedrq
    # or configured on your local system.
    rq: RepoqueryBase = config.get_rq("rawhide")

    # PackageQueryCompat is a Protocol implemented by both backends.
    # It is an iterable of PackageCompat objects with extra methods to
    # filter packages and preform other similar tasks.
    #
    # rq.query() creates a PackageQuery instance and calls its filterm() method
    # with the provided kwargs.

    # This filters out all src packages
    query: PackageQueryCompat = rq.query(arch="src")

    # PackageCompat is a Protocol implemented by both the dnf and libdnf5
    # backends.
    packages: list[PackageCompat] = []

    for package in query:
        # fmt: off
        if (
            not any(package.name.startswith(i) for i in DEFAULT_IGNORES) and
            not any(i in package.release for i in releases)
        ):
            packages.append(package)
        # fmt: on
    for p in packages:
        print(p.name)


if __name__ == "__main__":
    main(**vars(parseargs()))
