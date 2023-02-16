# SPDX-FileCopyrightText: 2022 Maxwell G <gotmax@e.email>
# SPDX-License-Identifier: GPL-2.0-or-later

from __future__ import annotations

import importlib.resources as importlib_resources
import itertools
import logging
import os
import re
import sys
import typing as t
import warnings
import zipfile
from collections.abc import Callable
from enum import auto as auto_enum
from importlib.abc import Traversable
from pathlib import Path

from fedrq._compat import StrEnum
from fedrq.backends.base import BaseMakerBase

if sys.version_info < (3, 11):
    import tomli as tomllib
else:
    import tomllib

from pydantic import BaseModel, Field, validator

from fedrq._utils import mklog
from fedrq.backends import BACKENDS, get_default_backend

if t.TYPE_CHECKING:
    import dnf
    import libdnf5

    from fedrq.backends.base import BackendMod, RepoqueryBase

CONFIG_DIRS = (Path.home() / ".config/fedrq", Path("/etc/fedrq"))
DEFAULT_REPO_CLASS = "base"
logger = logging.getLogger(__name__)


class ConfigError(ValueError):
    pass


class LoadFilelists(StrEnum):
    auto = auto_enum()
    always = auto_enum()
    never = auto_enum()


class ReleaseConfig(BaseModel):
    name: str = Field(exclude=True)
    defs: dict[str, list[str]]
    matcher: t.Pattern
    repo_dirs: list[Path] = Field(
        default_factory=lambda: [
            directory.joinpath("repos") for directory in CONFIG_DIRS
        ]
    )
    defpaths: set[str] = Field(default_factory=set)
    system_repos: bool = True

    koschei_collection: t.Optional[str] = None
    copr_chroot_fmt: t.Optional[str] = None

    full_def_paths: t.ClassVar[list[t.Union[Traversable, Path]]] = []

    @validator("defpaths")
    def v_defpaths(cls, value, values) -> dict[str, t.Any]:
        flog = mklog(__name__, "ReleaseConfig", "_get_full_defpaths")
        flog.debug(f"Getting defpaths for {values['name']}: {value}")
        values["full_def_paths"] = cls._get_full_defpaths(
            values["name"], value.copy(), values["repo_dirs"]
        )
        return value

    @validator("matcher")
    def v_matcher(cls, value: t.Pattern) -> t.Pattern:
        if value.groups != 1:
            raise ValueError("'matcher' must have exactly one capture group")
        return value

    @validator("repo_dirs", pre=True)
    def v_repo_dirs(cls, value: str | list[Path]) -> list[Path]:
        if not isinstance(value, str):
            return value
        return [Path(directory) for directory in value.split(":")]

    def is_match(self, val: str) -> bool:
        return bool(re.match(self.matcher, val))

    def is_valid_repo(self, val: str) -> bool:
        return val in self.defs

    def release(self, branch: str, repo_name: str = "base") -> Release:
        return Release(self, branch, repo_name)

    @staticmethod
    def _repo_dir_iterator(
        repo_dirs: list[Path],
    ) -> t.Iterator[t.Union[Traversable, Path]]:
        flog = mklog(__name__, "ReleaseConfig", "_repo_dir_iterator")
        topdirs: tuple[t.Union[Traversable, Path], ...] = (
            *repo_dirs,
            importlib_resources.files("fedrq.data.repos"),
        )
        flog.debug("topdirs = %s", topdirs)
        for topdir in topdirs:
            if isinstance(topdir, Path):
                topdir = topdir.expanduser()
            if not topdir.is_dir():
                continue
            for file in topdir.iterdir():
                if file.is_file():
                    yield file

    @classmethod
    def _get_full_defpaths(
        cls, name: str, defpaths: set[str], repo_dirs: list[Path]
    ) -> list[t.Union[Traversable, Path]]:
        missing_absolute: list[t.Union[Traversable, Path]] = []
        full_defpaths: list[t.Union[Traversable, Path]] = []
        flog = mklog(__name__, cls.__name__, "_get_full_defpaths")
        flog.debug(f"Searching for absolute defpaths: {defpaths}")
        for defpath in defpaths.copy():
            if (path := Path(defpath).expanduser()).is_absolute():
                flog.debug(f"Is absolute: {path}")
                defpaths.discard(defpath)
                if path.is_file():
                    flog.debug(f"Exists: {path}")
                    full_defpaths.append(path)
                else:
                    flog.debug(f"Doesn't Exist: {path}")
                    missing_absolute.append(path)
        flog.debug(f"Getting relative defpaths: {defpaths}")
        files = cls._repo_dir_iterator(repo_dirs)
        while defpaths:
            try:
                file = next(files)
                flog.debug(f"file={file}")
            except StopIteration:
                flog.debug(msg="StopIteration")
                break
            if file.name in defpaths:
                flog.debug(f"{file.name} in {defpaths}")
                full_defpaths.append(file)
                defpaths.discard(file.name)
        if defpaths:
            _missing = ", ".join(
                sorted(str(p) for p in ((*defpaths, *missing_absolute)))
            )
            raise ConfigError(f"Missing defpaths in {name}: {_missing}")
        return full_defpaths

    def get_release(
        self, config: RQConfig, branch: str, repo_name: str = "base"
    ) -> Release:
        return Release(release_config=self, branch=branch, repo_name=repo_name)


class Release:
    def __init__(
        self,
        release_config: ReleaseConfig,
        branch: str,
        repo_name: str = "base",
    ) -> None:
        self.release_config = release_config
        if not self.release_config.is_match(branch):
            raise ConfigError(
                f"Branch {branch} does not match {self.release_config.name}"
            )
        if not self.release_config.is_valid_repo(repo_name):
            raise ConfigError(
                "{repo} is not a valid repo type for {name}".format(
                    repo=repo_name, name=self.release_config.name
                )
                + " Valid repos are: {}".format(tuple(release_config.defs))
            )
        self.branch = branch
        self.repo_name = repo_name

    @property
    def version(self) -> str:
        if match := re.match(self.release_config.matcher, self.branch):
            return match.group(1)
        raise ValueError(f"{self.branch} does not match {self.release_config.name}")

    @property
    def repos(self) -> tuple[str, ...]:
        return tuple(self.release_config.defs[self.repo_name])

    @property
    def copr_chroot_fmt(self) -> str | None:
        return self.release_config.copr_chroot_fmt

    @property
    def koschei_collection(self) -> str | None:
        return self.release_config.koschei_collection

    def make_base(
        self,
        config: RQConfig | None = None,
        base_conf: dict[str, t.Any] | None = None,
        base_vars: dict[str, t.Any] | None = None,
        base_maker: BaseMakerBase | None = None,
        fill_sack: bool = True,
    ) -> dnf.Base | libdnf5.base.Base:
        """
        :param config: An RQConfig object.
                       DEPRECATED since 0.4.0: A new RQConfig object will be
                                               created if this is None.
        :param base_conf: Base session configuration
        :param base_vars: Base session vars/substitutions (arch, basearch,
                                                           releasever, etc.)
        :param base_maker: Existing BaseMaker object to configure.
                           If base_maker is None, a new one will be created.
        :param fill_sack: Whether to fill the Base object's package sack or
                          just return the Base object after applying configuration.
        """
        if config is None:
            warnings.warn(
                "DEPRECATED since 0.4.0: Provide an RQConfig object for 'config'"
            )
            config = get_config()
        base_conf = base_conf or {}
        base_vars = base_vars or {}
        if config.smartcache and self.version != config.backend_mod.get_releasever():
            base_conf.setdefault(
                "cachedir", str(get_smartcache_basedir() / str(self.branch))
            )
        bm = base_maker or config.backend_mod.BaseMaker()
        bm.sets(base_conf, base_vars)
        if config.load_filelists:
            bm.load_filelists()
        bm.load_release_repos(self, "releasever" not in base_vars)
        return bm.fill_sack() if fill_sack else bm.base


class RQConfig(BaseModel):
    backend: t.Optional[str] = os.environ.get("FEDRQ_BACKEND")
    releases: dict[str, ReleaseConfig]
    default_branch: str = os.environ.get("FEDRQ_BRANCH", "rawhide")
    smartcache: bool = True
    load_filelists: LoadFilelists = LoadFilelists.auto
    _backend_mod = None

    class Config:
        json_encoders: dict[t.Any, Callable[[t.Any], str]] = {
            re.Pattern: lambda pattern: pattern.pattern,
            zipfile.Path: lambda path: str(path),
        }
        underscore_attrs_are_private = True
        validate_assignment = True

    @validator("backend")
    def v_backend(cls, value) -> str:
        assert (
            value is None or value in BACKENDS
        ), f"Valid backends are: {', '.join(BACKENDS)}"
        return value

    @property
    def backend_mod(self) -> BackendMod:
        if not self._backend_mod:
            self._backend_mod = get_default_backend(
                self.backend,
                # allow falling back to a non default backend
                # (i.e. not backends.DEFAULT_BACKEND)
                # when the user does not explicitly request a backend.
                fallback=not bool(self.backend),
            )
        return self._backend_mod

    def get_release(
        self, branch: str | None = None, repo_name: str | None = None
    ) -> Release:
        flog = mklog(__name__, "RQConfig", "get_releases")
        branch = branch or self.default_branch
        repo_name = repo_name or DEFAULT_REPO_CLASS
        pair = (branch, repo_name)
        for release in sorted(
            self.releases.values(), key=lambda r: r.name, reverse=True
        ):
            try:
                r = release.get_release(self, branch=branch, repo_name=repo_name)
            except ConfigError as exc:
                logger.debug(f"{release.name} does not match {pair}: {exc}")
            else:
                flog.debug("%s matches %s", release.name, pair)
                return r
        raise ConfigError(
            "{} does not much any of the configured releases: {}".format(
                pair, self.release_names
            )
        )

    @property
    def release_names(self) -> list[str]:
        return [rc.name for rc in self.releases.values()]

    def get_rq(
        self,
        branch: str | None = None,
        repo: str | None = None,
        base_conf: dict[str, t.Any] | None = None,
        base_vars: dict[str, t.Any] | None = None,
    ) -> RepoqueryBase:
        """
        Higher level interface that finds the Release object that mathces
        {branch} and {repo}, creates a (lib)dnf(5).base.Base session, and
        returns a Repoquery object.

        :param branch: branch name
        :param repo: repo class. defaults to 'base'.
        :param base_conf: Base session configuration
        :param base_vars: Base session vars/substitutions (arch, basearch,
                                                           releasever, etc.)
        """
        release = self.get_release(branch, repo)
        return self.backend_mod.Repoquery(release.make_base(self, base_conf, base_vars))


def get_smartcache_basedir() -> Path:
    basedir = Path(os.environ.get("XDG_CACHE_HOME", Path("~/.cache").expanduser()))
    return basedir.joinpath("fedrq").resolve()


def _get_files(
    directory: t.Union[Traversable, Path], suffix: str, reverse: bool = True
) -> list[t.Union[Traversable, Path]]:
    files: list[t.Union[Traversable, Path]] = []
    if not directory.is_dir():
        return files
    for file in directory.iterdir():
        if file.name.endswith(suffix) and file.is_file():
            files.append(file)
    return sorted(files, key=lambda f: f.name, reverse=reverse)


def _process_config(
    data: dict[str, t.Any], config: dict[str, t.Any], releases: dict[str, t.Any]
) -> None:
    if r := data.pop("releases", None):
        releases.update(r)
    config.update(data)


def get_config(**overrides: t.Any) -> RQConfig:
    """
    Retrieve config files from CONFIG_DIRS and fedrq.data.
    Perform naive top-level merging of the 'releases' table.
    """
    flog = mklog(__name__, "get_config")
    flog.debug(f"CONFIG_DIRS = {CONFIG_DIRS}")
    config: dict[str, t.Any] = {}
    releases: dict[str, t.Any] = {}
    all_files: list[list[t.Union[Traversable, Path]]] = [
        _get_files(importlib_resources.files("fedrq.data"), ".toml"),
        *(_get_files(p, ".toml") for p in reversed(CONFIG_DIRS)),
    ]
    flog.debug("all_files = %s", all_files)
    for path in itertools.chain.from_iterable(all_files):
        flog.debug("Loading config file: %s", path)
        with path.open("rb") as fp:
            data = tomllib.load(fp)
        _process_config(data, config, releases)
    _process_config(overrides, config, releases)
    config["releases"] = _get_releases(releases)
    flog.debug("Final config: %s", config)
    return RQConfig(**config)


def _get_releases(rdict: dict[str, dict[str, t.Any]]) -> dict[str, t.Any]:
    releases: dict[str, t.Any] = {}
    for name, data in rdict.items():
        releases[name] = dict(name=name, **data)
    return releases


def get_rq(
    branch: str | None = None,
    repo: str = "base",
    *,
    smart_cache: bool | None = None,
    load_filelists: bool | None = None,
) -> RepoqueryBase:
    """
    Higher level interface that creates an RQConfig object, finds the Release
    object that mathces {branch} and {repo}, creates a dnf.Base, and finally
    returns a Repoquery object.
    """
    warnings.warn("DEPRECATED since 0.4.0: use RQConfig.get_rq() instead.")
    config = get_config()
    if smart_cache is not None:
        config.smartcache = smart_cache
    if load_filelists is not None:
        config.load_filelists = (
            LoadFilelists.always if load_filelists else LoadFilelists.never
        )
    return config.get_rq(branch, repo)
