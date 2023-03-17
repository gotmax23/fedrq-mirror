# Copyright (C) 2023 Maxwell G <gotmax@e.email>
#
# SPDX-License-Identifier: GPL-2.0-or-later
# ruff: noqa: ARG002

from __future__ import annotations

import abc
import logging
import os
import re
import tempfile
from collections.abc import (
    Callable,
    ItemsView,
    Iterator,
    KeysView,
    Mapping,
    Sequence,
    ValuesView,
)
from contextlib import contextmanager
from typing import TYPE_CHECKING, Any, NoReturn

import requests

from fedrq._config import ConfigError

if TYPE_CHECKING:
    from fedrq.backends.base import BaseMakerBase
    from fedrq.config import Release, RQConfig

LOG = logging.getLogger(__name__)


@contextmanager
def _get_file(path: str) -> Iterator[str]:
    if path.startswith(("http://", "https://")):
        try:
            name = None
            LOG.info("Downloading %s", path)
            req = requests.get(path)
            if req.status_code != 200:
                raise ConfigError(f"Failed to download {path}")
            fd, name = tempfile.mkstemp()
            os.write(fd, req.content)
            os.close(fd)
            yield name
        finally:
            if name:
                os.unlink(name)
    elif path.startswith("file://"):
        yield path[7:]
    else:
        yield path


class RepoG(metaclass=abc.ABCMeta):
    """
    Base class containing a repo group to load. These can be added to a Repos
    container class.
    """

    name: str
    seperator: str
    args: str
    config: RQConfig
    release: Release
    container: Repos

    def __init__(
        self,
        name: str,
        seperator: str,
        args: str,
        container: Repos | None = None,
    ) -> None:
        self.name = name
        self.seperator = seperator
        self.args = args
        self.container = container or Repos({})
        self.validate()

    @abc.abstractmethod
    def load(
        self, base_maker: BaseMakerBase, config: RQConfig, release: Release
    ) -> None:
        ...

    def err_fmt(self, msg: str) -> ConfigError:
        return ConfigError(msg)

    def err(self, msg: str, from_value: Any = ...) -> NoReturn:
        if from_value == ...:
            raise self.err_fmt(msg)
        else:
            raise self.err_fmt(msg) from from_value

    def validate(self) -> None:
        if not self.seperator and not self.args:
            self.err("Expected an argument")

    def __str__(self) -> str:
        return f"{self.name}{self.seperator}{self.args}"


class SimpleRepoG(RepoG):
    def load(
        self, base_maker: BaseMakerBase, config: RQConfig, release: Release
    ) -> None:
        try:
            base_maker.enable_repo(self.args)
        except ValueError:
            self.err(f"No repo named {self.args}", None)


class MultiNameG(RepoG):
    repos: Sequence[str] = ()
    repogs: list[RepoG]

    def validate(self):
        if self.args:
            raise ConfigError("No arguments are accepted")
        self.repogs = [self.container.get_repo(repo) for repo in self.repos]

    def load(
        self, base_maker: BaseMakerBase, config: RQConfig, release: Release
    ) -> None:
        for repog in self.repogs:
            repog.load(base_maker, config, release)

    @classmethod
    def from_names(
        cls, class_name: str, names: Sequence[str] | str
    ) -> type[MultiNameG]:
        dct = dict(
            __doc__=f"Load the following repos: {names}",
            __module__=__name__,
            repos=[names] if isinstance(names, str) else names,
        )
        typ = type(f"{class_name.upper()}MultiNameG", (cls,), dct)
        return typ


class AliasRepoG(RepoG):
    fmt_str: str
    final: RepoG

    @classmethod
    def from_str(cls, fmt_str: str, class_name: str) -> type[AliasRepoG]:
        dct = dict(
            __doc__=f"Load a repo from the {fmt_str!r} alias",
            __module__=__name__,
            fmt_str=fmt_str,
        )
        typ = type(f"{class_name.upper()}AliasRepoG", (cls,), dct)
        return typ

    @classmethod
    def from_str_mapping(cls, mapping: dict[str, str]) -> dict[str, type[AliasRepoG]]:
        return {name: cls.from_str(fmt_str, name) for name, fmt_str in mapping.items()}

    def validate(self) -> None:
        super().validate()
        expanded = self.fmt_str.format(*self.args.split(";"))
        self.final = self.container.get_repo(expanded)

    def load(
        self, base_maker: BaseMakerBase, config: RQConfig, release: Release
    ) -> None:
        self.final.load(base_maker, config, release)


class FileRepoG(RepoG):
    def load(
        self, base_maker: BaseMakerBase, config: RQConfig, release: Release
    ) -> None:
        with _get_file(self.args) as path:
            base_maker.read_repofile(path)


class CoprRepoG(RepoG):
    url: str

    def load(
        self, base_maker: BaseMakerBase, config: RQConfig, release: Release
    ) -> None:
        self.url = release._copr_repo(self.args, config.copr_baseurl)
        with _get_file(self.url) as path:
            base_maker._read_repofile_new(path, True)


class BaseurlRepoG(RepoG):
    _ALLOWED_REPOID = re.compile(
        "[^ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_.:]"
    )

    def load(
        self, base_maker: BaseMakerBase, config: RQConfig, release: Release
    ) -> None:
        url, _, key = self.args.partition(";")
        repoid = self._ALLOWED_REPOID.sub("_", url)
        repo_kwargs: dict[str, Any] = dict(baseurl=[url], gpgcheck=bool(key))
        if key:
            repo_kwargs["gpgkey"] = key
        base_maker.create_repo(repoid, **repo_kwargs)


class Repos(Mapping[str, type[RepoG]]):
    """
    Immutable mapping like class of RepoG types.
    Converts repo aliases (strings) and list of repos in RepoG objects.
    Allows merging and adding other Repos objects.
    """

    # Normally, get_repo() will only select RepoGs in the container if the key
    # starts with '@' to avoid conflicts with plain repoids.
    # However, get_repo() will return a RepoG that's a subclass of
    # _ALLOWED_PLAIN even if the key doesn't start with '@'.
    _ALLOWED_PLAIN: tuple[type[RepoG]] = (MultiNameG,)
    # This RepoG will be used when get_repo() is passed a key that doesn't
    # start with '@'.
    _DEFAULT: type[RepoG] = SimpleRepoG
    # Factory function to generate a RepoG from a plain string or list.
    _FALLBACK_FACTORY: Callable[
        [str, Sequence[str] | str], type[RepoG]
    ] = MultiNameG.from_names

    def __init__(
        self,
        repo_classes: Mapping[str, Sequence[str] | str | type[RepoG]],
    ) -> None:
        self.__data: dict[str, type[RepoG]] = {
            name: repos
            if isinstance(repos, type) and issubclass(repos, RepoG)
            else self._FALLBACK_FACTORY(name, repos)
            for name, repos in ItemsView(repo_classes)
        }

    def get_repo(self, key: str) -> RepoG:
        if key.startswith("@"):
            name, seperator, args = key.partition(":")
            try:
                typ = self[name[1:]]
            except KeyError:
                raise ConfigError(f"{key} is not a valid repository class") from None
            return typ(name, seperator, args, self)
        # Repo groups are special cased to maintain backwards compatibility
        elif key in self.keys() and issubclass(self[key], self._ALLOWED_PLAIN):
            return self[key](key, "", "", self)
        else:
            return self._DEFAULT("", "", key, self)

    def __getitem__(self, key: str) -> type[RepoG]:
        return self.__data[key]

    def __len__(self) -> int:
        return len(self.__data)

    def __iter__(self) -> Iterator[str]:
        return iter(self.__data)

    def __or__(self, other: Mapping[str, Sequence[str] | type[RepoG]]) -> Repos:
        return type(self)({**self, **other})

    def new(self, other: Mapping[str, Sequence[str] | type[RepoG]]) -> Repos:
        return self | other

    def items(self) -> ItemsView[str, type[RepoG]]:
        return self.__data.items()

    def keys(self) -> KeysView[str]:
        return self.__data.keys()

    def values(self) -> ValuesView[type[RepoG]]:
        return self.__data.values()

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.__data!r})"


DefaultRepoGs = Repos(
    dict(file=FileRepoG, copr=CoprRepoG, repo=SimpleRepoG, baseurl=BaseurlRepoG)
)
