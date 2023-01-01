# SPDX-FileCopyrightText: 2022 Maxwell G <gotmax@e.email>
# SPDX-License-Identifier: GPL-2.0-or-later

from __future__ import annotations

import abc
import typing as t
from collections.abc import Iterable, Mapping

from fedrq._utils import get_source_name, mklog

if t.TYPE_CHECKING:
    import dnf
    import hawkey

ATTRS = (
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
)


class InvalidFormatterError(ValueError):
    pass


def stringify(value: t.Any) -> str:
    if value is None or value == "":
        return "(none)"
    if isinstance(value, str) and "\n" in value:
        return value + "\n---\n"
    return str(value)


class Formatter(abc.ABC):
    @abc.abstractmethod
    def format(self, packages: hawkey.Query) -> Iterable[str]:
        ...


class SpecialFormatter(Formatter):
    def __init__(self, params: str) -> None:
        self.params = params
        self.verifier()

    def verifier(self) -> None:
        flog = mklog(__name__, self.__class__.__name__, "verifier")
        flog.debug("No verifier defined")
        return None


class FormatterContainer:
    _formatters: Mapping[str, type[Formatter]] = {}
    _special_formatters: Mapping[str, type[SpecialFormatter]] = {}
    _fallback_formatter: type[SpecialFormatter] | None = None

    formatters: dict[str, type[Formatter]]
    special_formatters: dict[str, type[SpecialFormatter]]

    __slots__ = (
        "formatters",
        "special_formatters",
    )

    def __init__(
        self,
        # formatters: dict[str, type[Formatter]] | None = None,
        # special_formatters: dict[str, type[SpecialFormatter]] | None = None,
    ) -> None:
        _formatters: dict[str, type[Formatter]] = {}
        _special_formatters: dict[str, type[SpecialFormatter]] = {}
        for container in reversed(self.__class__.__mro__):
            if issubclass(container, FormatterContainer):
                _formatters |= getattr(container, "_formatters", {})
                _special_formatters |= getattr(container, "_special_formatters", {})
        # _formatters |= formatters or {}
        # _special_formatters |= special_formatters or {}
        self.formatters = _formatters
        self.special_formatters = _special_formatters

    def __contains__(self, value: str) -> bool:
        if not isinstance(value, str):
            raise TypeError
        try:
            self.get_formatter(value)
        except InvalidFormatterError:
            return False
        return True

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, FormatterContainer):
            return False
        for attr in ("formatters", "special_formatters", "_fallback_formatter"):
            if getattr(self, attr) != (value, attr):
                return False
        return True

    def get_formatter(self, value: str) -> Formatter:
        name, part, params = value.partition(":")
        if part and name in self.special_formatters:
            return self.special_formatters[name](params)
        elif name in self.formatters:
            return self.formatters[name]()
        elif self._fallback_formatter:
            return self._fallback_formatter(value)
        raise InvalidFormatterError(f"'{value}' is not a valid formatter")


class PlainFormatter(Formatter):
    """
    Default Package formatter (%{name}-%{?epoch:%{epoch}:}%{version}-%{release}.%{arch})
    """

    def format(self, packages: hawkey.Query) -> Iterable[str]:
        for p in sorted(packages):
            yield str(p)


class NVFormatter(Formatter):
    """
    %{name}-%{version}
    """

    def format(self, packages: hawkey.Query) -> Iterable[str]:
        for p in sorted(packages):
            yield f"{p.name}-{p.version}"


class NAFormatter(Formatter):
    """
    %{name}.%{arch}
    """

    def format(self, packages: hawkey.Query) -> Iterable[str]:
        for p in sorted(packages):
            yield f"{p.name}.{p.arch}"


class NEVFormatter(Formatter):
    """
    %{name}-%{epoch}:%{version}
    """

    def format(self, packages: hawkey.Query) -> Iterable[str]:
        for p in sorted(packages):
            yield f"{p.name}-{p.epoch}:{p.version}"


class SourceFormatter(Formatter):
    def format(self, packages: hawkey.Query) -> Iterable[str]:
        return sorted({get_source_name(pkg) for pkg in packages})


class AttrFormatter(SpecialFormatter):
    """
    Lookup a Package attribute for each package in the query result.
    Equivalent to `dnf repoquery --qf=%{ATTR}` where ATTR is the formatter argument.
    """

    def verifier(self) -> None:
        self.params = self.params.strip()
        if self.params not in ATTRS:
            raise InvalidFormatterError(f"'{self.params}' is not a valid attribute")

    def format(self, packages: hawkey.Query) -> Iterable[str]:
        for p in sorted(packages):
            result = getattr(p, self.params)
            if isinstance(result, list):
                yield from map(stringify, result)
                continue
            yield stringify(result)


class JsonFormatter(SpecialFormatter):
    def _check_attr(self, attr: str) -> str:
        attr = attr.strip()
        if attr not in ATTRS:
            raise InvalidFormatterError(
                f"{self.params} contains an invalid argument: '{attr}'"
            )
        return attr

    def verifier(self) -> None:
        self.attrs: list[str] = [self._check_attr(a) for a in self.params.split(",")]

    def _format(self, package: dnf.package.Package) -> Iterable[tuple[str, t.Any]]:
        for attr in self.attrs:
            result = getattr(package, attr)
            if isinstance(result, list):
                result = [str(i) for i in result]
            yield attr, result

    def format(self, packages: hawkey.Query):
        import json

        data = [dict(self._format(package)) for package in packages]
        yield json.dumps(data, indent=2)


class DefaultFormatters(FormatterContainer):
    _formatters = dict(
        plain=PlainFormatter,
        nv=NVFormatter,
        na=NAFormatter,
        nev=NEVFormatter,
        source=SourceFormatter,
    )
    _special_formatters = dict(attr=AttrFormatter, json=JsonFormatter)
    _fallback_formatter = AttrFormatter
