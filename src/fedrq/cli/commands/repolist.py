# Copyright (C) 2023 Maxwell G <maxwell@gtmx.me>
# SPDX-License-Identifier: GPL-2.0-or-later

from __future__ import annotations

import argparse
import sys
from collections import abc as cabc

from pydantic import ValidationError

from fedrq.cli.base import Command


class Repolist(Command):
    """
    Display list of enabled repositories
    """

    def __init__(self, args: argparse.Namespace) -> None:
        self.args = args
        self._v_errors: list[str] = []

        self.v_logging()
        try:
            self.config = self._get_config()
        except ValidationError as exc:  # pragma: no cover
            sys.exit(str(exc))
        self.v_release()

    @classmethod
    def make_parser(
        cls,
        parser_func: cabc.Callable = argparse.ArgumentParser,
        *,
        add_help: bool = False,
        **kwargs,
    ) -> argparse.ArgumentParser:
        parser: argparse.ArgumentParser = super().make_parser(
            parser_func, add_help=add_help, parents=[cls.branch_repo_parser()], **kwargs
        )
        parser.add_argument("--debug", action="store_true")
        parser.add_argument("--all", action="store_true")
        return parser

    def run(self) -> None:
        bm = self.backend.BaseMaker()
        self.release.make_base(self.config, base_maker=bm, fill_sack=False)
        self._enable_disable_bm(bm)
        for repo in bm.repolist(True):
            print(repo)
