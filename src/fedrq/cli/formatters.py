# Copyright (C) 2023 Maxwell G <gotmax@e.email>
#
# SPDX-License-Identifier: GPL-2.0-or-later

from __future__ import annotations

import abc
import logging
import warnings
from collections.abc import Callable, ItemsView, Iterable, Iterator, Mapping
from contextlib import suppress
from typing import TYPE_CHECKING, Any, NoReturn

from fedrq._utils import get_source_name

if TYPE_CHECKING:
    from fedrq.backends.base import PackageCompat

LOG = logging.getLogger(__name__)


class FormatterError(Exception):
    pass


_ATTRS: tuple[str, ...] = (
    "name",
    "arch",
    "a",
    "epoch",
    "e",
    "version",
    "v",
    "release",
    "r",
    "from_repo",
    "evr",
    "debug_name",
    "source_name",
    "source_debug_name",
    "installtime",
    "buildtime",
    "size",
    "downloadsize",
    "installsize",
    "provides",
    "requires",
    "recommends",
    "suggests",
    "supplements",
    "enhances",
    "obsoletes",
    "conflicts",
    "sourcerpm",
    "description",
    "summary",
    "license",
    "url",
    "reason",
    "files",
    "reponame",
    "repoid",
    "vendor",
    "packager",
    "location",
)


def _stringify(value: Any, *, multiline_allowed: bool = True) -> str:
    if value is None or value == "":
        return "(none)"
    if isinstance(value, str) and "\n" in value:
        if not multiline_allowed:
            raise FormatterError("Multiline values are not allowed")
        return value + "\n---\n"
    return str(value)


class Formatter(abc.ABC):
    ATTRS = _ATTRS
    MULTILINE = False

    """
    Convert PackageCompat objects into a string representation
    for use with the fedrq CLI.
    """

    def __init__(
        self,
        name: str,
        seperator: str,
        args: str,
        container: Formatters | None = None,
    ) -> None:
        self.name = name
        self.seperator = seperator
        self.args = args
        self.container: Formatters = container or Formatters({})
        self.validate()

    @abc.abstractmethod
    def format_line(self, package: PackageCompat) -> str:
        """
        Format a single Package object
        """
        pass

    def format(self, packages: Iterable[PackageCompat]) -> Iterable[str]:
        """
        Convert an Iterable of PackageCompat objects
        (or a PackageQueryCompat object) to an Iterable of str.
        """
        yield from map(self.format_line, sorted(packages))

    def err(self, msg: str) -> NoReturn:
        raise FormatterError(f"{self.name!r} FormatterError: {msg}")

    def validate(self) -> None:
        if self.seperator:
            self.err("no arguments are accepted")

    @classmethod
    def frompat(cls, fmt: str, name: str) -> type[Formatter]:
        """
        Convert Python format string (e.g. `{0.name}.{0.arch}`)
        in a Formatter class.
        """

        def format_line(self, package):  # noqa: ARG001
            return fmt.format(package)

        dct = dict(
            __doc__=f"{name} -- {fmt}",
            __module__=__name__,
            format_line=format_line,
        )
        typ = type(f"{name.upper()}Formatter", (cls,), dct)
        return typ

    @classmethod
    def fromfunc(
        cls, func: Callable[[PackageCompat], str], name: str
    ) -> type[Formatter]:
        """
        Convert a function (or other callable) into a Formatter class.
        The function is used as the format_line() method.
        """
        dct = dict(
            format_line=func,
            __module__=__name__,
            __doc__=func.__doc__ if func.__doc__ else name,
        )
        typ = type(f"{name.upper()}Formatter", (cls,), dct)
        return typ

    def __str__(self) -> str:
        return f"{self.name}{self.seperator}{self.args}"


class Formatters(Mapping[str, type[Formatter]]):
    __slots__ = ("__data", "fallback")

    """
    Immutable mapping like class of Formatter classes.
    Converts strings and simple functions to Formatter objects.
    Allows merging and adding other Formatters.
    """

    def __init__(
        self,
        formatters: Mapping[str, Callable | type[Formatter] | str],
        fallback: type[Formatter] | None = None,
    ) -> None:
        self.__data = self._formattersv(dict(formatters))
        self.fallback: type[Formatter] | None = fallback

    def get_formatter(self, key: str) -> Formatter:
        name, seperator, args = key.partition(":")
        with suppress(KeyError):
            return self[name](name, seperator, args, self)
        if self.fallback:
            with suppress(FormatterError):
                return self.fallback(name, seperator, args, self)
        raise FormatterError(f"{key!r} is not a valid formatter")

    def __getitem__(self, key: str) -> type[Formatter]:
        return self.__data[key]

    def __len__(self) -> int:
        return len(self.__data)

    def __iter__(self) -> Iterator[str]:
        return iter(self.__data)

    def __or__(
        self, other: Mapping[str, Callable | type[Formatter] | str]
    ) -> Formatters:
        fallback: type[Formatter] | None = self.fallback
        if hasattr(other, "fallback"):
            fallback = other.fallback
        return type(self)({**self, **other}, fallback)

    def __contains__(self, name: object) -> bool:
        if not isinstance(name, str):
            raise TypeError
        try:
            self.get_formatter(name)
        except FormatterError:
            return False
        else:
            return True

    def singleline(self) -> Formatters:
        return Formatters(
            {
                name: formatter
                for name, formatter in self.items()
                if not formatter.MULTILINE
            }
        )

    def new(self, other: Mapping[str, str | Callable | type[Formatter]]) -> Formatters:
        return self | other

    def items(self) -> ItemsView[str, type[Formatter]]:
        return ItemsView(self)

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.__data!r})"

    def _formattersv(self, formatters) -> dict[str, type[Formatter]]:
        if not formatters:
            return {}
        for name, formatter in formatters.items():
            if isinstance(formatter, type) and issubclass(formatter, Formatter):
                pass
            elif isinstance(formatter, str):
                formatters[name] = Formatter.frompat(formatter, name)
            elif callable(formatter):
                formatters[name] = Formatter.fromfunc(
                    formatter,  # type: ignore[arg-type]
                    name,
                )
            else:
                raise TypeError
        return formatters


class SourceFromatter(Formatter):
    def format(self, packages: Iterable[PackageCompat]) -> Iterable[str]:
        return sorted(set(map(self.format_line, packages)))

    def format_line(self, package: PackageCompat) -> str:
        return get_source_name(package)


class SpecialFormatter(Formatter):
    """
    Formatter that accepts arguments
    """

    ATTRS: tuple[str, ...] = Formatter.ATTRS

    def _get_attrs(self, args: str) -> Iterator[str | Formatter]:
        for attr in args.split(","):
            if attr in self.ATTRS:
                yield attr
            elif attr in self.container.singleline():
                yield self.container.get_formatter(attr)
            else:
                self.err(f"invalid argument {attr!r}")

    def validate(self) -> None:
        if not self.args.strip() or self.args.strip() == ",":
            self.err("received less than 1 argument")


class AttrFormatter(SpecialFormatter):
    MULTILINE = True

    def validate(self) -> None:
        super().validate()
        self._validate()

    def _validate(self) -> None:
        if self.args not in self.ATTRS:
            raise FormatterError(f"'{self.args}' is not a valid attribute")
        self.attr = self.args

    def format_line(self, package: PackageCompat) -> str:
        # Return one string if there's multiple lines
        return "\n".join(self.format([package]))

    def format(self, packages: Iterable[PackageCompat]) -> Iterable[str]:
        for p in sorted(packages):
            result = getattr(p, self.attr)
            if isinstance(result, Iterable) and not isinstance(result, str):
                yield from map(_stringify, result)
            else:
                yield _stringify(result)


class AttrFallbackFormatter(AttrFormatter):
    def validate(self) -> None:
        if self.seperator:
            self.err("no arguments are accepted")
        self.args = self.name
        self._validate()


class JsonFormatter(SpecialFormatter):
    MULTILINE = True

    def validate(self) -> None:
        super().validate()
        self.attrs: list[Formatter | str] = list(self._get_attrs(self.args))

    def _format(self, package: PackageCompat) -> Iterable[tuple[str, Any]]:
        for attr in self.attrs:
            if isinstance(attr, str):
                result = getattr(package, attr)
                if isinstance(result, Iterable) and not isinstance(result, str):
                    result = [str(i) for i in result]
            else:
                result = attr.format_line(package)
            yield str(attr), result

    def format(self, packages: Iterable[PackageCompat]):
        import json

        data = [dict(self._format(package)) for package in packages]
        yield json.dumps(data, indent=2)

    def format_line(self, package: PackageCompat):
        raise NotImplementedError


class SingleLineFormatter(SpecialFormatter):
    DEFAULT_DIVIDER = " : "
    ATTRS: tuple[str, ...] = tuple(
        set(SpecialFormatter.ATTRS)
        - {
            "description",
            "provides",
            "requires",
            "recommends",
            "suggests",
            "supplements",
            "enhances",
            "obsoletes",
            "conflicts",
            "files",
        }
    )

    def validate(self) -> None:
        args, seperator, args2 = self.args.rpartition(":")
        LOG.debug(
            "parsing %s args: %r, %r, %r",
            "SingleLineFormatter.validate",
            args,
            seperator,
            args2,
        )
        # line:name:| -> params=name, divider = |
        if args and seperator and args2:
            LOG.debug("case 1")
            self.params = args
            self.divider = args2
        # line:name -> params=name, divider = DEFAULT_DIVIDER
        # line: -> params='', divider=DEFAULT_DIVIDER -> error in _get_attr()
        # line:: -> params='', divider=DEFAULT_DIVIDER -> error in _get_attr()
        elif not args:
            LOG.debug("case 2")
            self.params = args2
            self.divider = self.DEFAULT_DIVIDER
        # line:name: (trailing :) -> params=name, divider=DEFAULT_DIVIDER
        # line:otherformatter:arg: -> params=otherformatter:args,
        #                             divider=DEFAULT_DIVIDER
        # line::: -> error
        elif args and seperator and not args2:
            LOG.debug("case 3")
            self.params = args
            self.divider = self.DEFAULT_DIVIDER
        else:
            raise RuntimeError
        self.attrs = list(self._get_attrs(self.params))

    def format_line(self, package: PackageCompat) -> str:
        out = ""
        for index, attr in enumerate(self.attrs):
            if isinstance(attr, str):
                out += _stringify(getattr(package, attr), multiline_allowed=False)
            else:
                out += attr.format_line(package)
            if index != len(self.attrs) - 1:
                out += self.divider
        return out


class _DefaultFormatters(Formatters):
    def __call__(self) -> Any:
        warnings.warn(
            "DEPRECATED since 0.4.0: DefaultFormatters no longer needs to be called."
            " It's already initialized."
            " Just call DefaultFormatters.get_formatter() directly."
        )
        return self


DefaultFormatters = _DefaultFormatters(
    dict(
        plain="{0}",
        plainwithrepo="{0} {0.reponame}",
        nevrr="{0} {0.reponame}",
        na="{0.name}.{0.arch}",
        nev="{0.name}-{0.epoch}:{0.version}",
        nevr="{0.name}-{0.evr}",
        nevra="{0}",
        full_nevra="{0.name}-{0.evr}.{0.arch}",
        nv="{0.name}-{0.version}",
        source=SourceFromatter,
        src=SourceFromatter,
        attr=AttrFormatter,
        json=JsonFormatter,
        line=SingleLineFormatter,
    ),
    AttrFallbackFormatter,
)
