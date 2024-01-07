# PYTHON_ARGCOMPLETE_OK
# SPDX-FileCopyrightText: 2022 Maxwell G <gotmax@e.email>
#
# SPDX-License-Identifier: GPL-2.0-or-later

from __future__ import annotations

import abc
import argparse
import collections.abc as cabc
import json
import logging
import re
import sys
from functools import wraps
from pathlib import Path
from typing import TYPE_CHECKING, Any

from fedrq.backends.base import BaseMakerBase, PackageCompat

try:
    import tomli_w
except ImportError:
    HAS_TOMLI_W = False
else:
    HAS_TOMLI_W = True

from pydantic import ValidationError

from fedrq._utils import mklog
from fedrq.backends import BACKENDS, MissingBackendError
from fedrq.cli.formatters import (
    DefaultFormatters,
    Formatter,
    FormatterError,
    Formatters,
)
from fedrq.config import ConfigError, LoadFilelists, Release, RQConfig, get_config

if TYPE_CHECKING:
    from fedrq.backends.base import BackendMod, PackageQueryCompat

logger = logging.getLogger("fedrq")

FORMATTER_ERROR_SUFFIX = "See fedrq(1) for more information about formatters."

MISSING_BACKEND_MSG = """
Failed to load the package management backend: {}
These modules are only available for the default system Python interpreter.
""".strip()


SPLIT_REGEX = re.compile(r"\s*[,\s]\s*")


# Based on dnf.cli.option_parser._RepoCallback
class _EnableDisableRepo(argparse.Action):
    OPERATORS = {"-e": "enable", "--enablerepo": "enable", "--disablerepo": "disable"}

    def __call__(
        self,
        parser: argparse.ArgumentParser,  # noqa: ARG002
        namespace: argparse.Namespace,
        values: str | cabc.Sequence[Any] | None,
        option_string: str | None = None,
    ) -> None:
        assert isinstance(values, str) and isinstance(option_string, str)
        operator = self.OPERATORS[option_string]
        getattr(namespace, self.dest).extend(
            (operator, repo) for repo in SPLIT_REGEX.split(values)
        )


def _append_error(lst: list[str], error: cabc.Iterable | str | None = None) -> None:
    if isinstance(error, str):
        lst.append(error)
    elif isinstance(error, cabc.Iterable):
        lst.append(*error)
    elif error:
        raise TypeError(f"{type(error)} is not a valid return type.")


def v_add_errors(func: cabc.Callable[..., str | cabc.Iterable | None]) -> cabc.Callable:
    @wraps(func)
    def wrapper(self: Command, *args, **kwargs) -> str | cabc.Iterable | None:
        error = func(self, *args, **kwargs)
        _append_error(self._v_errors, error)
        return error

    return wrapper


def v_fatal_error(
    func: cabc.Callable[..., str | cabc.Iterable | None]
) -> cabc.Callable:
    def wrapper(self: Command, *args, **kwargs) -> None:
        error = func(self, *args, **kwargs)
        fatal: list[str] = []
        _append_error(fatal, error)
        if not fatal:
            return None
        self._v_handle_errors(False)
        for err in fatal:
            print("FATAL ERROR:", err, file=sys.stderr)
        sys.exit(1)

    return wrapper


class Command(metaclass=abc.ABCMeta):
    config: RQConfig
    release: Release
    query: PackageQueryCompat
    formatters: Formatters = DefaultFormatters
    formatter: Formatter

    def __init__(self, args: argparse.Namespace):
        self.args = args

        self.v_logging()
        flog = mklog(__name__, self.__class__.__name__)
        flog.debug("args=%s", args)

        if hasattr(self.args, "names"):
            self.get_names()

        try:
            self.config = self._get_config()
        except ValidationError as exc:
            sys.exit(str(exc))
        self._set_config("backend")
        self._set_config("smartcache")
        if (
            self.args.load_filelists == LoadFilelists.auto
            and "files" in self.args.formatter
        ):
            self.config.load_filelists = LoadFilelists.always
        else:
            self._set_config("load_filelists")

        self._v_errors: list[str] = []

    def _get_config(self):
        # This makes it easier to mock the config
        return get_config()

    @property
    def backend(self) -> BackendMod:
        return self.config.backend_mod

    @abc.abstractmethod
    def run(self) -> None:
        ...

    def _set_config(self, key: str) -> None:
        arg = getattr(self.args, key, None)
        if arg is not None:
            setattr(self.config, key, arg)

    def _logq(
        self, query: PackageQueryCompat, name: str = "query", level=logging.DEBUG
    ) -> PackageQueryCompat:
        """
        Log a query object after performing the appropriate formatting.
        Don't iterate over the query unless the logging level is low enough to
        avoid a performance penalty.
        """
        if logger.getEffectiveLevel() <= level:
            logger.debug("%s = %s", name, tuple(query))
        return query

    @classmethod
    def branch_repo_parser(cls) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(add_help=False)
        parser.add_argument(
            "-b",
            "--branch",
            help="Fedora or EPEL branch name "
            "(e.g. epel7, rawhide, epel9-next, f37) to query",
        )
        parser.add_argument("-r", "--repos", default="base")
        parser.add_argument(
            "-e",
            "--enablerepo",
            dest="enable_disable",
            default=[],
            action=_EnableDisableRepo,
            metavar="REPO",
            help="""
            Enable certain repositories for the duration of this operation.
            All repositories in the system configuration and any additional
            defs in the selected branch are available.
            """,
        )
        parser.add_argument(
            "--disablerepo",
            dest="enable_disable",
            default=[],
            action=_EnableDisableRepo,
            metavar="REPO",
            # PROVISIONAL
            help=argparse.SUPPRESS,
        )
        return parser

    @classmethod
    def arch_parser(cls) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(add_help=False)
        arch_group = parser.add_mutually_exclusive_group()
        arch_group.add_argument(
            "-A",
            "--arch",
            help="Only include packages that match ARCH",
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
        arch_group.add_argument(
            "-s",
            "--src",
            dest="arch",
            action="store_const",
            const="src",
            help="Query for BuildRequires of NAME. "
            "This is equivalent to --arch=src.",
        )
        return parser

    @classmethod
    def resolve_parser(cls) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(add_help=False)
        parser.add_argument(
            "-P",
            "--resolve-packages",
            action="store_true",
            help="Resolve the correct Package when given a virtual Provide."
            " For instance, /usr/bin/yt-dlp would resolve to yt-dlp",
        )
        return parser

    @classmethod
    def assume_parser(cls) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(add_help=False)
        run_parser = parser.add_mutually_exclusive_group()
        run_parser.add_argument("-y", "--assumeyes", action="store_true")
        run_parser.add_argument("-n", "--dry-run", action="store_true")
        return parser

    @classmethod
    def parent_parser(
        cls, *, formatter: bool = True, latest: bool = True, name=True
    ) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(
            add_help=False, parents=[cls.branch_repo_parser()]
        )
        if name:
            parser.add_argument(  # type: ignore[attr-defined]
                "names",
                metavar="NAME",
                nargs="*",
                help="Mutually exclusive with --stdin",
            ).completer = lambda **_: ()
            parser.add_argument(
                "-i",
                "--stdin",
                help="Read package names from stdin.",
                action="store_true",
            )
        if latest:
            parser.add_argument("-l", "--latest", default=1, help="'all' or an integer")
        if formatter:
            parser.add_argument(  # type: ignore[attr-defined]
                "-F",
                "--formatter",
                default="plain",
            ).completer = cls.formatters._argcompleter
        cachedir_group = parser.add_mutually_exclusive_group()
        cachedir_group.add_argument(
            "--system-cache",
            action="store_true",
            help="Use the default dnf cachedir and ignore `smartcache` config option",
        )
        cachedir_group.add_argument(
            "--sc",
            "--smartcache",
            action="store_true",
            default=None,
            dest="smartcache",
            help="See `smartcache` in fedrq(5)."
            " smartcache is enabled by default,"
            " so this is noop unless you set `smartcache=false` in the config file.",
        )
        cachedir_group.add_argument(
            "--smartcache-always",
            action="store_const",
            dest="smartcache",
            const="always",
        )
        # This is mutually exclusive with --smartcache. It's still undocumented
        # and subject to change.
        cachedir_group.add_argument("--cachedir", help=argparse.SUPPRESS, type=Path)
        parser.add_argument("--debug", action="store_true")
        parser.add_argument(
            "-L",
            "--filelists",
            choices=tuple(LoadFilelists),
            dest="load_filelists",
            help="Whether to load filelists."
            " By default, filelists are only loaded when using the files formatter."
            " This only applies when using the libdnf5 backend,"
            " which doesn't load filelists by default to save memory and bandwidth."
            " dnf4 always loads filelists.",
        )
        parser.add_argument("-B", "--backend", choices=tuple(BACKENDS))
        parser.add_argument(
            "--forcearch", help="Query a foreign architecture's repositories"
        )
        return parser

    @classmethod
    @abc.abstractmethod
    def make_parser(
        cls,
        parser_func: cabc.Callable[
            ..., argparse.ArgumentParser
        ] = argparse.ArgumentParser,
        *,
        add_help: bool = False,
        **kwargs,
    ) -> argparse.ArgumentParser:
        kwargs = {
            "description": cls.__doc__,
            "help": cls.__doc__,
            "parents": [cls.parent_parser()],
        } | kwargs
        if not add_help:
            kwargs.pop("help", None)

        parser = parser_func(**kwargs)
        return parser

    @classmethod
    def standalone(cls, argv: list[str] | None = None) -> None:
        parser = cls.make_parser(add_help=False)
        return cls(args=parser.parse_args(argv)).run()

    def get_names(self) -> None:
        if self.args.names and self.args.stdin:
            sys.exit("Postional NAMEs can not be used with --stdin")
        if self.args.stdin:
            self.args.names = [line.strip() for line in sys.stdin.readlines()]
        if not self.args.names:
            sys.exit("No package names were passed")

    def format(
        self, query: cabc.Iterable[PackageCompat] | None = None
    ) -> cabc.Iterable[str]:
        """
        Helper to run `self.formatter.format(self.query)`
        """
        return self.formatter.format(query if query is not None else self.query)

    def _v_handle_errors(self, should_exit: bool = True):
        if self._v_errors:
            for line in self._v_errors:
                print("ERROR:", line, file=sys.stderr)
            if should_exit:
                sys.exit(1)

    def v_logging(self) -> None:
        if getattr(self.args, "debug", None):
            logger.setLevel(logging.DEBUG)

    @v_add_errors
    def v_latest(self) -> str | None:
        if not hasattr(self.args, "latest"):
            return None
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

    @v_add_errors
    def v_formatters(self) -> str | None:
        if not hasattr(self.args, "formatter"):
            return None
        try:
            self.formatter = self.formatters.get_formatter(self.args.formatter)
        except FormatterError as err:
            logger.debug("FormatterError", exc_info=err)
            return str(err) + "\n" + FORMATTER_ERROR_SUFFIX
        return None

    @v_add_errors
    def v_arch(self) -> str | None:
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

    @v_fatal_error
    def v_release(self) -> str | None:
        try:
            self.release = self.config.get_release(self.args.branch, self.args.repos)
        except ConfigError as err:
            return str(err)
        return None

    def _enable_disable_bm(self, bm: BaseMakerBase):
        for func, repo in self.args.enable_disable:
            if func == "enable":
                self.release.get_repog(repo).load(bm, self.config, self.release)
            elif func == "disable":
                bm.disable_repo(repo, True)
            else:
                raise ValueError

    @v_fatal_error
    def v_rq(self) -> str | None:
        flog = mklog("fedrq.cli.Command", "v_rq")
        conf: dict[str, Any] = {}
        bvars: dict[str, Any] = {}

        # Set cachedir if it's explicitly passed
        if self.args.cachedir:
            conf["cachedir"] = str(self.args.cachedir)
        # Disable release based smartcache if user explicitly disabled it or if
        # forcearch is in use.
        elif self.args.system_cache or (
            self.args.forcearch and self.config.smartcache != "always"
        ):
            self.config.smartcache = False

        if self.args.forcearch:
            conf["ignorearch"] = True
            bvars["arch"] = self.args.forcearch
        bm = self.backend.BaseMaker()
        try:
            self.release.make_base(self.config, conf, bvars, bm, False)
            self._enable_disable_bm(bm)
        except ConfigError as exc:
            return str(exc)
        try:
            filled = bm.fill_sack()
        except self.backend.RepoError as exc:
            flog.debug("RepoError: ", exc_info=exc)
            return str(exc)
        self.rq = self.backend.Repoquery(filled)
        return None

    @v_fatal_error
    def v_backend(self) -> str | None:
        try:
            _ = self.backend
        except MissingBackendError as exc:
            return MISSING_BACKEND_MSG.format(str(exc))
        return None

    def v_default(self) -> None:
        self.v_formatters()
        self.v_latest()
        self.v_arch()
        # Fatal
        self.v_backend()
        self._v_handle_errors()
        self.v_release()
        self.v_rq()
        self._v_handle_errors()


class CheckConfig(Command):
    """
    Verify fedrq configuration
    """

    def __init__(self, args: argparse.Namespace):
        self.args = args
        self.v_logging()

    @staticmethod
    def _strip_nones(dct: dict[Any, Any], level=0) -> dict[Any, Any]:
        """
        Recurisvely remove None values from a dictionary so they can be TOML
        serialized
        """
        flog = mklog("fedrq.cli.CheckConfig", "_strip_nones_")
        for k in tuple(dct):
            if dct[k] is None:
                flog.debug("%s: Strip %s key", level, k)
                del dct[k]
            elif isinstance(dct[k], dict):
                flog.debug("%s: Recursing through %s dict", level, k)
                CheckConfig._strip_nones(dct[k], level + 1)
        return dct

    @classmethod
    def make_parser(
        cls,
        parser_func: cabc.Callable = argparse.ArgumentParser,
        *,
        add_help: bool = False,
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
        flog = mklog("fedrq.cli.CheckConfig")
        if self.args.dump and not HAS_TOMLI_W:
            sys.exit("tomli-w is required for --dump.")
        if not self.args.dump:
            print("Validating config...")
        try:
            self.config = get_config()
        except ValidationError as exc:
            sys.exit(str(exc))
        try:
            self.config.get_release(self.config.default_branch)
        except ConfigError:
            sys.exit(f"default_branch '{self.config.default_branch}' is invalid")
        if not self.args.dump:
            print("No validation errors found!")
        else:
            flog.debug("Removing Nones from configuration dict")
            data_dict = self._strip_nones(json.loads(self.config.json()))
            tomli_w.dump(data_dict, sys.stdout.buffer)
