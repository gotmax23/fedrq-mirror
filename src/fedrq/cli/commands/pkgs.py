# SPDX-FileCopyrightText: 2022 Maxwell G <gotmax@e.email>
# SPDX-License-Identifier: GPL-2.0-or-later

from __future__ import annotations

import argparse
from collections import abc as cabc

from fedrq._utils import filter_latest
from fedrq.cli import Command


class Pkgs(Command):
    """
    Find the packages that match NAMES.
    NAMES can be package package name globs or NEVRs.
    """

    def __init__(self, args: argparse.Namespace) -> None:
        super().__init__(args)
        self.v_default()

    @classmethod
    def make_parser(
        cls,
        parser_func: cabc.Callable = argparse.ArgumentParser,
        *,
        add_help: bool = False,
        **kwargs,
    ) -> argparse.ArgumentParser:
        parser = super().make_parser(
            parser_func,
            parents=[cls.parent_parser(), cls.arch_parser(), cls.resolve_parser()],
            help="Find the packages that match a list of package specs",
            add_help=add_help,
            **kwargs,
        )

        return parser

    def _paths_need_filelists(self, names: cabc.Iterable[str]) -> bool:
        """
        Override the parent _paths_need_filelists to only resolve files when
        --resolve-packages is passed.
        """
        return self.args.resolve_packages and super()._paths_need_filelists(names)

    def run(self) -> None:
        self.query = self.rq.query(empty=True)

        resolved_packages = self.rq.resolve_pkg_specs(
            self.args.names, self.args.resolve_packages
        )
        self._logq(resolved_packages, "resolved_packages")
        self.query = self.query.union(resolved_packages)

        glob_packages = self.rq.query(name__glob=self.args.names)
        self._logq(glob_packages, "glob_packages")
        self.query = self.query.union(glob_packages)

        self.query = self.rq.arch_filter(self.query, self.args.arch)
        filter_latest(self.query, self.args.latest)
        self._logq(self.query, "self.query")

        for p in self.format():
            print(p)
