# SPDX-FileCopyrightText: 2022 Maxwell G <gotmax@e.email>
#
# SPDX-License-Identifier: GPL-2.0-or-later

from __future__ import annotations

import typing as t

from fedrq._utils import get_source_name
from fedrq.repoquery import dnf, hawkey, needs_dnf

ATTRS = (
    "name",
    "arch",
    "epoch",
    "version",
    "release",
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
    "obsoletes",
    "conflicts",
    "sourcerpm",
    "description",
    "summary",
    "license",
    "url",
    "reason",
    "files",
    "repo",
    "reponame",
    "repoid",
)


def plain_formatter(packages: hawkey.Query) -> t.Iterable[str]:
    for p in packages:
        yield str(p)


def nv_formatter(packages: hawkey.Query) -> t.Iterable[str]:
    for p in packages:
        yield f"{p.name}-{p.version}"


def na_formatter(packages: hawkey.Query) -> t.Iterable[str]:
    for p in packages:
        yield f"{p.name}.{p.arch}"


def nev_formatter(packages: hawkey.Query) -> t.Iterable[str]:
    for p in packages:
        yield f"{p.name}-{p.epoch}:{p.version}"


def source_formatter(packages: hawkey.Query) -> t.Iterable[str]:
    return sorted({get_source_name(pkg) for pkg in packages})


# FORMATTERS = {
#     "plain": plain_formatter,
#     "nv": nv_formatter,
#     "na": na_formatter,
#     "nev": nev_formatter,
#     "source": source_formatter,
# }


def stringify(value: t.Any) -> str:
    needs_dnf()
    if value is None or value == "":
        return "(none)"
    if isinstance(value, dnf.repo.Repo):
        return value.id
    if isinstance(value, str) and "\n" in value:
        return value + "\n---\n"
    return str(value)


FormatterT: dict[str, t.Callable[..., t.Iterable[str]]]


class FormatterContainer:
    formatters: dict[str, t.Callable[..., t.Iterable[str]]] = dict(
        plain=plain_formatter,
        nv=nv_formatter,
        na=na_formatter,
        nev=nev_formatter,
        source=source_formatter,
    )

    # def __init__(self, extras: FormatterT | None, default: FormatterT | None) -> None:
    #     pass

    @staticmethod
    def attr_formatter(packages: hawkey.Query, attr: str) -> t.Iterable[str]:
        for p in packages:
            result = getattr(p, attr)
            if isinstance(result, list):
                yield from (stringify(i) for i in result)
                continue
            yield stringify(result)

    def list_all_formatters(self) -> t.Iterable[str]:
        yield from self.formatters
        yield from ATTRS
        yield from (f"attr:{f}" for f in ATTRS)

    def format(
        self, _packages: hawkey.Query, /, formatter: str = "plain"
    ) -> t.Iterable[str]:
        packages = sorted(_packages)
        if not packages:
            return ()
        if formatter in self.formatters:
            return self.formatters[formatter](packages)
        if formatter.startswith("attr:"):
            formatter = formatter[5:]
        if formatter in ATTRS:
            return self.attr_formatter(packages, formatter)
        raise ValueError(f"{formatter} does not exist")

    @classmethod
    def add_formatters(cls, **kwargs) -> FormatterContainer:
        new = cls()
        new.formatters = dict(**new.formatters, **kwargs)
        return new
