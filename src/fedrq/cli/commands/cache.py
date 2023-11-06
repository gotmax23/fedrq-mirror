from __future__ import annotations

import argparse
from collections.abc import Callable

from fedrq.cli.base import Command


class MakeCacheCommand(Command):
    """
    Load the repodata for the current branch/repo config
    """

    def __init__(self, args: argparse.Namespace) -> None:
        super().__init__(args)
        self.v_default()

    @classmethod
    def make_parser(
        cls,
        parser_func: Callable = argparse.ArgumentParser,
        *,
        add_help: bool = False,
        **kwargs,
    ) -> argparse.ArgumentParser:
        parser = super().make_parser(
            parser_func,
            add_help=add_help,
            parents=[
                cls.parent_parser(formatter=False, latest=False, name=False),
                cls.arch_parser(),
            ],
            **kwargs,
        )
        return parser

    def run(self) -> None:
        enabled_repos = self.backend.BaseMaker(self.rq.base).repolist(True)
        inflected = "repo" if len(enabled_repos) == 1 else "repos"
        print(f"Loaded {len(enabled_repos)} {inflected}")
