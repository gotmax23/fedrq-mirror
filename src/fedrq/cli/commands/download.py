# Copyright (C) 2023 Maxwell G <maxwell@gtmx.me>
# SPDX-License-Identifier: MIT

"""
download commands
"""

from __future__ import annotations

import argparse
import logging
import shutil
import sys
from collections.abc import Callable, Iterator
from contextlib import suppress
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

import requests
import rpm

from fedrq._archive import RPMArchive
from fedrq._utils import exhaust_it
from fedrq.backends.base import PackageCompat
from fedrq.cli.base import Command

_LOG = logging.getLogger(__name__)


def callback_ind(start: int, end: int) -> Callable[[Path], None]:
    def inner(destpath: Path) -> None:
        print(f"Downloading {destpath.name} ({start}/{end})")

    return inner


def _get_req_kwargs(package: PackageCompat) -> dict[str, Any]:  # pragma: no cover
    req_kwargs: dict[str, Any] = {}
    repo_obj = package.repo
    # libdnf5 has a .get_config() attribute
    with suppress(AttributeError):
        repo_obj = repo_obj.get_config()
    if repo_obj.sslverify is False:
        repo_obj["verify"] = False
    elif repo_obj.sslcacert:
        req_kwargs["verify"] = repo_obj.sslcacert
    if repo_obj.sslclientcert and repo_obj.sslclientkey:
        req_kwargs["cert"] = (repo_obj.sslclientcert, repo_obj.sslclientkey)
    return req_kwargs


def download(
    package: PackageCompat,
    destdir: Path,
    callback: Callable[[Path], None] | None = None,
) -> Path:
    def _remote_dl(url: str, src: Path, dest: Path) -> None:  # noqa: ARG001
        req_kwargs = _get_req_kwargs(package)
        req = requests.get(url, allow_redirects=True, **req_kwargs)
        req.raise_for_status()
        dest.write_bytes(req.content)

    def _local_cp(url: str, src: Path, dest: Path) -> None:  # noqa: ARG001
        shutil.copy2(src, dest)

    url = package.remote_location()
    if not url:  # pragma: no cover
        raise ValueError(f"Could not determine url for {package}!")

    mode: Callable[[str, Path, Path], None]
    src: Path
    dest: Path

    if url.startswith("file://"):
        src = Path(url[7:])
        mode = _local_cp
    else:
        src = Path(url)
        mode = _remote_dl

    dest = destdir / src.name
    if callback:
        callback(dest)
    mode(url, src, dest)
    return dest


class DownloadCommand(Command):
    """
    EXPERIMENTAL: Download an (S)RPM from the repos.
    No gpg checking is preformed.
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
            help=(cls.__doc__ or "").strip().replace("\n", " "),
            parents=[
                cls.parent_parser(),
                cls.arch_parser(),
                cls.resolve_parser(),
                cls.assume_parser(),
            ],
            **kwargs,
        )
        parser.add_argument("-o", "--destdir", type=Path, default=Path())
        return parser

    def _select_packages(self) -> None:
        self.query = self.rq.resolve_pkg_specs(
            self.args.names, self.args.resolve_packages, self.args.latest
        )
        self.rq.arch_filterm(self.query, self.args.arch)

    def _prompt(self) -> bool:
        if not self.query:
            sys.exit("No packages found!")
        size = len(self.query)
        inflected = "package"
        if size > 1:
            inflected += "s"
        print(f"\nDownload {size} {inflected}")

        if self.args.assumeyes:
            return True
        if self.args.dry_run:
            return False

        inp = input("(Y/n) ")
        if inp.lower() in ("", "y"):
            return True
        print("Exiting...", file=sys.stderr)
        return False

    def _downloadit(self, destdir: Path) -> Iterator[tuple[PackageCompat, Path]]:
        size = len(self.query)
        for ind, package in enumerate(self.query):
            try:
                dest = download(package, destdir, callback_ind(ind + 1, size))
                yield package, dest
            except Exception as exc:
                _LOG.debug("Handled error:", exc_info=exc)
                sys.exit(f"Failed to download {package}: {exc!r}")

    def run(self) -> None:
        self._select_packages()
        for line in self.format():
            print(line)
        if not self._prompt():
            return
        exhaust_it(self._downloadit(self.args.destdir))


class DownloadSpecCommand(DownloadCommand):
    """
    EXPERIMENTAL: Download an SRPM and extract its specfile.
    No gpg checking is preformed.
    """

    @classmethod
    def make_parser(
        cls,
        parser_func: Callable = argparse.ArgumentParser,
        *,
        add_help: bool = False,
        **kwargs,
    ) -> argparse.ArgumentParser:
        parser = super(DownloadCommand, cls).make_parser(
            parser_func,
            help=(cls.__doc__ or "").strip().replace("\n", " "),
            add_help=add_help,
            parents=[
                cls.parent_parser(),
                cls.assume_parser(),
            ],
            **kwargs,
        )
        parser.add_argument("-o", "--destdir", type=Path, default=Path())
        parser.add_argument(
            "--gpgcheck",
            action=argparse.BooleanOptionalAction,
            default=False,
            help="Whether to check package gpg keys."
            " The keys must be part of the system RPM keyring."
            " Default: --no-gpgcheck",
        )
        parser.set_defaults(resolve_packages=False, arch="src")
        return parser

    def run(self) -> None:
        self._select_packages()
        for line in self.format():
            print(line)
        if not self._prompt():
            return

        ts = rpm.TransactionSet()
        if not self.args.gpgcheck:
            ts.setVSFlags(rpm.RPMVSF_MASK_NOSIGNATURES)
        with TemporaryDirectory() as _tmp:
            temp = Path(_tmp)
            for _, dest in self._downloadit(temp):
                with RPMArchive(dest, ts=ts) as archive:
                    archive.extract_specfile(self.args.destdir)
                dest.unlink()
