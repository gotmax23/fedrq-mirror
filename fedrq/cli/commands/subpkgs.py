# SPDX-FileCopyrightText: 2022 Maxwell G <gotmax@e.email>
#
# SPDX-License-Identifier: GPL-2.0-or-later

from __future__ import annotations

import argparse
from collections.abc import Callable

from fedrq.cli.base import Command, get_packages


class Subpkgs(Command):
    """
    For each SRPM name, list the subpackages that it provides
    """

    def __init__(self, args: argparse.Namespace) -> None:
        super().__init__(args)
        self.v_default()

    @classmethod
    def make_parser(
        cls,
        parser_func: Callable = argparse.ArgumentParser,
        *,
        add_help: bool,
        **kwargs,
    ) -> argparse.ArgumentParser:
        pargs = dict(description=cls.__doc__, parents=[cls.parent_parser()], **kwargs)
        if add_help:
            pargs["help"] = "Find the subpackages of a list of SRPMs"
        parser = parser_func(**pargs)
        arch_group = parser.add_mutually_exclusive_group()
        arch_group.add_argument(
            "-A", "--arch", help="Only show subpackages with this arch"
        )
        arch_group.add_argument(
            "-S",
            "--notsrc",
            dest="arch",
            action="store_const",
            const="notsrc",
            help="This includes all binary RPMs. Multilib is excluded on x86_64. "
            "Equivalent to --arch=notsrc",
        )
        return parser

    def run(self) -> None:
        srpms = get_packages(self.rq.sack, self.args.names, latest=self.args.latest)
        srpms.filterm(arch="src")
        subpackages = self.rq.get_subpackages(
            srpms, latest=self.args.latest, arch=self.args.arch
        )
        for p in self.formatter.format(subpackages, self.args.formatter):
            print(p)

    @Command._v_add_errors
    def v_arch(self) -> str | None:
        if r := super().v_arch():
            return r
        if (
            self.args.arch
            and "src" in self.args.arch
            and "notsrc" not in self.args.arch
        ):
            return "Illegal option '--arch=src': Subpackages are binary RPMs"
        return None
