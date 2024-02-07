# Copyright (C) 2024 Maxwell G <maxwell@gtmx.me>
# SPDX-License-Identifier: GPL-2.0-or-later

from __future__ import annotations

import argparse
from collections.abc import Callable

from fedrq._utils import mklog
from fedrq.cli.base import Command
from fedrq.cli.formatters import DefaultFormatters


class FormattersCommand(Command):
    """
    List available formatters
    """

    def __init__(self, args: argparse.Namespace) -> None:
        self.args = args

        self.v_logging()
        flog = mklog(__name__, self.__class__.__name__)
        flog.debug("args=%s", args)

    @classmethod
    def make_parser(
        cls,
        parser_func: Callable = argparse.ArgumentParser,
        *,
        add_help: bool = False,
        **kwargs,
    ) -> argparse.ArgumentParser:
        parser = super().make_parser(
            parser_func, add_help=add_help, parents=[], **kwargs
        )
        parser.add_argument(
            "--only-formatters", "--formatters", action="store_true", dest="formatters"
        )
        parser.add_argument(
            "--only-attrs", "--attrs", action="store_true", dest="attrs"
        )
        parser.add_argument(
            "--only-special-formatters",
            "--special-formatters",
            action="store_true",
            dest="special_formatters",
        )
        return parser

    def run(self) -> None:
        formatter_args_names = {"formatters", "attrs", "special_formatters"}
        formatter_args = {
            key: value
            for key, value in vars(self.args).items()
            if key in formatter_args_names
        }
        # If none of the --only-foo args are passed, set everything to True
        if set(formatter_args.values()) == {False}:
            formatter_args = dict.fromkeys(formatter_args.keys(), True)
        for formatter in sorted(DefaultFormatters.formatters_it(**formatter_args)):
            print(formatter)
