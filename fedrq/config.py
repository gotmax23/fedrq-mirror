# SPDX-FileCopyrightText: 2022 Maxwell G <gotmax@e.email>
# SPDX-License-Identifier: GPL-2.0-or-later

from __future__ import annotations

import importlib.abc
import importlib.resources
import itertools
import logging
import re
import typing as t
from collections.abc import Callable
from pathlib import Path

try:
    import tomllib  # type: ignore
except ImportError:
    import tomli as tomllib  # type: ignore

from pydantic import BaseModel, Field, validator

from fedrq._dnf import dnf, needs_dnf
from fedrq._utils import mklog
from fedrq.repoquery import Repoquery, base_enable_repos, base_read_system_repos

CONFIG_DIRS = (Path.home() / ".config/fedrq", Path("/etc/fedrq"))
logger = logging.getLogger(__name__)


class ConfigError(ValueError):
    pass


class ReleaseConfig(BaseModel):
    name: str = Field(exclude=True)
    defs: dict[str, list[str]]
    matcher: t.Pattern
    defpaths: set[str] = Field(default_factory=set)
    koschei_collection: t.Optional[str] = None
    copr_chroot_fmt: t.Optional[str] = None
    system_repos: bool = True
    full_def_paths: t.ClassVar[list[importlib.abc.Traversable]] = []

    @validator("defpaths")
    def v_defpaths(cls, value, values) -> dict[str, t.Any]:
        flog = mklog(__name__, "ReleaseConfig", "_get_full_defpaths")
        flog.debug(f"Getting defpaths for {values['name']}: {value}")
        values["full_def_paths"] = cls._get_full_defpaths(values["name"], value)
        return value

    def is_match(self, val: str) -> bool:
        return bool(re.match(self.matcher, val))

    def is_valid_repo(self, val: str) -> bool:
        return val in self.defs

    def release(self, branch: str, repo_name: str = "base") -> Release:
        return Release(self, branch, repo_name)

    @staticmethod
    def _repo_dir_iterator() -> t.Iterator[importlib.abc.Traversable]:
        for topdir in (
            *(dir.joinpath("repos") for dir in CONFIG_DIRS),
            importlib.resources.files("fedrq.data.repos"),
        ):
            if not topdir.is_dir():
                continue
            for file in topdir.iterdir():
                yield file

    @classmethod
    def _get_full_defpaths(
        cls, name: str, defpaths: set[str]
    ) -> list[importlib.abc.Traversable]:
        missing_absolute: list[importlib.abc.Traversable] = []
        full_defpaths: list[importlib.abc.Traversable] = []
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
        files = cls._repo_dir_iterator()
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

    def get_release(self, branch: str, repo_name: str = "base") -> Release:
        return Release(release_config=self, branch=branch, repo_name=repo_name)


class Release:
    def __init__(
        self, release_config: ReleaseConfig, branch: str, repo_name: str = "base"
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
        self, base: dnf.Base | None = None, fill_sack: bool = True
    ) -> dnf.Base:
        needs_dnf()
        flog = mklog(__name__, self.__class__.__name__, "make_base")
        base = base or dnf.Base()
        flog.debug("self.release = %s", self.version)
        base.conf.substitutions["releasever"] = self.version
        if self.release_config.system_repos:
            base_read_system_repos(base)
        flog.debug("full_def_paths: %s", self.release_config.full_def_paths)
        for path in self.release_config.full_def_paths:
            with importlib.resources.as_file(path) as fp:
                flog.debug("Reading %s", fp)
                rr = dnf.conf.read.RepoReader(base.conf, None)
                for repo in rr._get_repos(str(fp)):
                    base.repos.add(repo)
        flog.debug("Enabling repos: %s", self.repos)
        base_enable_repos(self.repos, base)
        if fill_sack:
            base.fill_sack(load_system_repo=False)
        return base


class RQConfig(BaseModel):
    releases: dict[str, ReleaseConfig]
    default_branch: str = "rawhide"

    class Config:
        json_encoders: dict[t.Any, Callable[[t.Any], str]] = {
            re.Pattern: lambda pattern: pattern.pattern
        }

    def get_release(
        self, branch: str | None = None, repo_name: str = "base"
    ) -> Release:
        flog = mklog(__name__, "RQConfig", "get_releases")
        branch = branch or self.default_branch
        pair = (branch, repo_name)
        for release in self.releases.values():
            try:
                r = release.get_release(branch=branch, repo_name=repo_name)
            except ConfigError as exc:
                logger.debug(
                    f"{release.name} does not match {pair}: {exc}",
                    # exc_info=exc,
                )
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


def _get_files(
    dir: importlib.abc.Traversable, suffix: str, reverse: bool = True
) -> list[importlib.abc.Traversable]:
    files: list[importlib.abc.Traversable] = []
    if not dir.is_dir():
        return files
    for file in dir.iterdir():
        if file.name.endswith(suffix):
            files.append(file)
    return sorted(files, key=lambda f: f.name, reverse=reverse)


def _process_config(
    data: dict[str, t.Any], config: dict[str, t.Any], releases: dict[str, t.Any]
) -> None:
    if r := data.pop("releases", None):
        releases.update(r)
    config.update(data)


def get_config() -> RQConfig:
    """
    Retrieve config files from CONFIG_DIRS and fedrq.data.
    Perform naive top-level merging of the 'releases' table.
    """
    flog = mklog(__name__, "get_config")
    flog.debug(f"CONFIG_DIRS = {CONFIG_DIRS}")
    config: dict[str, t.Any] = {}
    releases: dict[str, t.Any] = {}
    all_files: list[list[importlib.abc.Traversable]] = [
        _get_files(importlib.resources.files("fedrq.data"), ".toml"),
        *(_get_files(p, ".toml") for p in reversed(CONFIG_DIRS)),
    ]
    flog.debug("all_files = %s", all_files)
    for path in itertools.chain.from_iterable(all_files):
        flog.debug("Loading config file: %s", path)
        with path.open("rb") as fp:
            data = tomllib.load(fp)
        _process_config(data, config, releases)
    config["releases"] = _get_releases(releases)
    flog.debug("Final config: %s", config)
    return RQConfig(**config)


def _get_releases(rdict: dict[str, dict[str, t.Any]]) -> dict[str, t.Any]:
    releases: dict[str, t.Any] = {}
    for name, data in rdict.items():
        releases[name] = dict(name=name, **data)
    return releases


def get_rq(branch: str = "rawhide", repo: str = "base") -> Repoquery:
    """
    Higher level interface that creates an RQConfig object, finds the Release
    object that mathces {branch} and {repo}, creates a dnf.Base, and finally
    returns a Repoquery object.
    """
    config = get_config()
    release = config.get_release(branch, repo)
    rq = Repoquery(release.make_base())
    return rq
