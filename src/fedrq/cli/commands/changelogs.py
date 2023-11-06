# Copyright (C) 2023 Maxwell G <maxwell@gtmx.me>
# SPDX-License-Identifier: GPL-2.0-or-later

"""
changelog commands
"""

from __future__ import annotations

import argparse
import sys

from fedrq.backends.base import PackageCompat, PackageQueryCompat
from fedrq.cli.base import Command, v_add_errors


def _get_single_package(query: PackageQueryCompat) -> PackageCompat:
    if not query:
        sys.exit("No matches for package!")
    arches = {package.arch for package in query}
    if "src" in arches:
        for package in query:
            if package.arch == "src":
                return package
    if len(arches) != 1:
        sys.exit("Found duplicate packages:", *query)
    return next(iter(query))


def _positive_int(number: str) -> int:
    i = int(number)
    if i < 1:
        raise TypeError("--entry-limit must be positive!")
    return i


class ChangelogCommand(Command):
    """
    Retrieve a single package's changelog
    """

    def __init__(self, args: argparse.Namespace) -> None:
        super().__init__(args)
        self.config.load_other_metadata = True
        self._v_names()
        self.v_default()

    @v_add_errors
    def _v_names(self) -> str | None:
        if len(self.args.names) > 1:
            return "More than one package name was passed!"
        return None

    @classmethod
    def make_parser(
        cls, parser_func=argparse.ArgumentParser, *, add_help: bool = False, **kwargs
    ) -> argparse.ArgumentParser:
        kwargs["description"] = cls.__doc__
        kwargs["parents"] = [
            cls.parent_parser(formatter=False, latest=False),
            cls.arch_parser(),
        ]
        if add_help:
            kwargs["help"] = cls.__doc__

        parser = parser_func(**kwargs)
        parser.add_argument("--entry-limit", type=_positive_int)
        return parser

    def run(self) -> None:
        query = self.rq.resolve_pkg_specs(self.args.names, latest=1)
        self.rq.arch_filterm(query, self.args.arch)
        changelogs = sorted(
            self.backend.get_changelogs(_get_single_package(query)),
            key=lambda entry: entry.date,
            reverse=True,
        )
        i: int = 0
        if not changelogs:  # pragma: no cover
            sys.exit("(empty)")
        for entry in changelogs:
            i += 1
            print(entry)
            print()
            if self.args.entry_limit is not None and i >= self.args.entry_limit:
                break
