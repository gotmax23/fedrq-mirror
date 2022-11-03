# SPDX-FileCopyrightText: 2022 Maxwell G <gotmax@e.email>
#
# SPDX-License-Identifier: GPL-2.0-or-later

from __future__ import annotations

import abc
import argparse
import collections.abc as cabc
import json
import logging
import sys
import typing as t
from functools import wraps

try:
    import tomli_w
except ImportError:
    HAS_TOMLI_W = False
else:
    HAS_TOMLI_W = True

from pydantic import ValidationError

from fedrq._dnf import HAS_DNF, dnf, hawkey
from fedrq._utils import filter_latest
from fedrq.cli.formatters import FormatterContainer
from fedrq.config import ConfigError
from fedrq.config import Release as Release3
from fedrq.config import RQConfig, get_config
from fedrq.repoquery import Repoquery

logger = logging.getLogger("fedrq")


def get_packages(
    sack: dnf.sack.Sack,
    packages: cabc.Collection[str],
    resolve: bool = False,
    latest: t.Optional[int] = None,
) -> hawkey.Query:
    flog = logging.getLogger(__name__ + ".get_packages()")
    flog.debug(
        f"get_packages(sack=..., packages={packages}, resolve={resolve}, latest={latest}"
    )
    packagesq = sack.query().filter(empty=True)
    kwargs = {}
    kwargs["with_provides"] = resolve
    kwargs["with_filenames"] = resolve
    for p in packages:
        flog.debug(f"dnf.subject.Subject({p}).get_best_query(sack, **{kwargs})")
        subject = dnf.subject.Subject(p).get_best_query(sack, **kwargs)
        flog.debug(f"subject query: {tuple(subject)}")
        packagesq = packagesq.union(subject)
    if resolve:
        flog.debug("Resolving provides...")
        pp = sack.query().filter(provides=packages)
        flog.debug(f"pp = {tuple(pp)}")
        packagesq = packagesq.union(pp)
    filter_latest(packagesq, latest)
    return packagesq


class Command(abc.ABC):
    _extra_formatters: dict[str, cabc.Callable[..., cabc.Iterable[str]]] = {}
    _create_rq: bool = False
    config: RQConfig
    release: Release3
    query: hawkey.Query

    def __init__(self, args: argparse.Namespace):
        self.args = args
        self.v_logging()
        self.config = get_config()
        self._v_errors: list[str] = []

    @property
    def formatter(self) -> FormatterContainer:
        return FormatterContainer.add_formatters(**self._extra_formatters)

    @abc.abstractmethod
    def run(self) -> None:
        ...

    @classmethod
    def parent_parser(cls) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(add_help=False)
        parser.add_argument(
            "-b",
            "--branch",
            default="rawhide",
            help="Fedora or EPEL branch name "
            "(e.g. epel7, rawhide, epel9-next, f37) to query",
        )
        parser.add_argument("-r", "--repos", default="base")
        parser.add_argument("-l", "--latest", default=1, help="'all' or an intenger")
        parser.add_argument(
            "-F",
            "--formatter",
            default="plain",
            # XXX: Steal --qf from dnf repoquery?
            help="PROVISIONAL: This option may be removed or have its interface"
            " changed in the near future",
        )
        # This is private for now; I'm not yet sure how I want to architect
        # passing extra configuration options.
        parser.add_argument("--cachedir", help=argparse.SUPPRESS)
        parser.add_argument("--debug", action="store_true")
        return parser

    @classmethod
    @abc.abstractmethod
    def make_parser(
        cls,
        parser_func: cabc.Callable = argparse.ArgumentParser,
        *,
        add_help: bool,
        **kwargs,
    ) -> argparse.ArgumentParser:
        ...

    @classmethod
    def standalone(cls) -> None:
        parser = cls.make_parser(add_help=False)
        return cls(args=parser.parse_args()).run()

    @staticmethod
    def _v_add_errors(
        func: cabc.Callable[..., str | cabc.Iterable | None]
    ) -> cabc.Callable:
        @wraps(func)
        def wrapper(self, *args, **kwargs) -> None:
            error = func(self, *args, **kwargs)
            if not error:
                return None
            if not isinstance(error, str) and isinstance(error, cabc.Iterable):
                self._v_errors.append(*error)
            else:
                self._v_errors.append(error)

        return wrapper

    def _v_handle_errors(self, should_exit: bool = True):
        if self._v_errors:
            for line in self._v_errors:
                print("ERROR:", line, file=sys.stderr)
            if should_exit:
                sys.exit(2)

    def v_logging(self) -> None:
        if getattr(self.args, "debug", None):
            logger.setLevel(logging.DEBUG)

    @_v_add_errors
    def v_latest(self) -> t.Optional[str]:
        try:
            self.args.latest = int(self.args.latest)
        except ValueError:
            if isinstance(self.args.latest, str) and self.args.latest.lower() in (
                "a",
                "all",
            ):
                self.args.latest = None
            else:
                return "--latest must equal 'all' or be an integer"
        return None

    @_v_add_errors
    def v_formatters(self) -> t.Optional[str]:
        if self.args.formatter not in self.formatter.list_all_formatters():
            # TODO: Properly document formatters
            return (
                f"{self.args.formatter} is not a valid formatter. "
                "See PLACEHOLDER for a list."
            )
        return None

    @_v_add_errors
    def v_arch(self) -> t.Optional[str]:
        # TODO: Verify that arches are actually valid RPM arches.
        if not self.args.arch:
            return None
        if "notsrc" in self.args.arch and "," in self.args.arch:
            return (
                f"Illegal option '--arch={self.args.arch}': "
                "'notsrc' is a special keyword that cannot be part of a list"
            )
        if "," in self.args.arch:
            self.args.arch = [item.strip() for item in self.args.arch.split(",")]
        return None

    def _get_release(self) -> t.Optional[str]:
        try:
            self.release = self.config.get_release(self.args.branch, self.args.repos)
        except ConfigError as err:
            return str(err)
        return None

    @_v_add_errors
    def v_rq(self) -> t.Optional[str]:
        if gr := self._get_release():
            return gr
        try:
            config = {}
            if self.args.cachedir:
                config["cachedir"] = self.args.cachedir
            base = self.release.make_base()
            self.rq = Repoquery(base)
        except ConfigError as exc:
            return str(exc)
        return None

    def needs_dnf(self) -> t.Optional[str]:
        if HAS_DNF:
            return None
        self._v_handle_errors(False)
        error = """\
The dnf and hawkey modules are not available in the current context.
These modules are only available for the default system Python interpreter."""
        print("FATAL ERROR:", error, file=sys.stderr)
        sys.exit(1)

    def v_default(self):
        self.v_formatters()
        self.v_latest()
        self.v_arch()
        self.needs_dnf()
        self.v_rq()
        self._v_handle_errors()


class CheckConfig(Command):
    """
    Verify fedrq configuration
    """

    def __init__(self, args: argparse.Namespace):
        self.args = args
        self.v_logging()

    @classmethod
    def make_parser(
        cls,
        parser_func: cabc.Callable = argparse.ArgumentParser,
        *,
        add_help: bool,
        **kwargs,
    ) -> argparse.ArgumentParser:
        kwargs = dict(description=cls.__doc__, **kwargs)
        if add_help:
            kwargs["help"] = cls.__doc__
        parser = parser_func(**kwargs)
        parser.add_argument("--debug", action="store_true")
        parser.add_argument(
            "--dump",
            action="store_true",
            help="Dump config as a toml file. Requires tomli-w.",
        )
        return parser

    def run(self):
        if not HAS_TOMLI_W:
            sys.exit("tomli-w is required for --dump.")
        if not self.args.dump:
            print("Validating config...")
        try:
            self.config = get_config()
        except (ValidationError) as exc:
            sys.exit(str(exc))
        if not self.args.dump:
            print("No validation errors found!")
        else:
            tomli_w.dump(json.loads(self.config.json()), sys.stdout.buffer)
