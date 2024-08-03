#!/usr/bin/env python3

# SPDX-License-Identifier: GPL-2.0-or-later
# Copyright (C) 2024 Maxwell G <maxwell@gtmx.me>

"""
Find out which packages in a repo have the longest license tags!
"""

from __future__ import annotations

from typing import cast

import click

import fedrq.config
from fedrq.backends.base import PackageCompat


def get_source_name(package: PackageCompat) -> str:
    return package.name if package.arch == "src" else cast(str, package.source_name)


@click.command(
    context_settings={"show_default": True, "help_option_names": ["-h", "--help"]}
)
@click.option("-b", "--branch")
@click.option("-r", "--repo", default="@base")
@click.option("-n", "--limit", type=click.INT, default=10)
@click.option(
    "--show-license / --no-show-license",
    " / --only-length",
    default=False,
    help="Whether to print the full license tag or just its length in results",
)
def main(
    branch: str | None,
    repo: str | None,
    limit: int,
    show_license: bool,
) -> None:
    """
    Find out which packages in a repo have the longest license tags!
    """
    config = fedrq.config.get_config()
    branch = branch or config.default_branch
    rq = config.get_rq(branch, repo)
    packages = rq.query(latest=1)
    packages_sorted = sorted(
        packages,
        # Sort by:
        key=lambda package: (
            # Length of license tag
            len(package.license),
            # Package source name
            get_source_name(package),
            # Source packages first
            1 if "src" in package.arch else 0,
            # Then sort by name for further tie-breaking,
            package.name,
        ),
        reverse=True,
    )
    total = 0
    length = 0
    last_package: PackageCompat | None = None
    for package in packages_sorted:
        if total >= limit:
            break
        # If the previous package has the same license length and comes from the
        # same source, skip it
        if (
            last_package
            and len(package.license) == len(last_package.license)
            and get_source_name(last_package) == get_source_name(package)
        ):
            continue
        length = len(package.license)
        print(
            f"{package.name}.{package.arch} (from {get_source_name(package)}):",
            package.license if show_license else length,
        )
        total += 1
        last_package = package


if __name__ == "__main__":
    main()
