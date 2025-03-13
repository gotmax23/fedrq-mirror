# Copyright (C) 2023 Maxwell G <maxwell@gtmx.me>
# SPDX-License-Identifier: MIT

"""
PRIVATE: Utilities for dealing with RPM archives
"""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import closing, contextmanager
from pathlib import Path
from typing import TYPE_CHECKING

import rpm

if TYPE_CHECKING:
    from typing_extensions import Self


class RPMArchiveError(Exception):
    """
    Error occured while handling an RPMArchive
    """


class RPMArchive:
    def __init__(self, path: Path, *, ts: rpm.TransactionSet | None = None) -> None:
        self.path = path
        self.ts: rpm.TransactionSet = ts or rpm.TransactionSet()
        self.fd: rpm.fd = rpm.fd(str(path), "r")
        self.hdr: rpm.hdr = self.ts.hdrFromFdno(self.fd)
        self._loc: int = self.fd.tell()

    def __repr__(self) -> str:  # pragma: no cover
        path, ts = self.path, self.ts
        typ = type(self).__name__
        return f"{typ}({path=}, {ts=})"

    @contextmanager
    def unpack_archive(self) -> Iterator[tuple[rpm.files, rpm.fd, rpm.archive]]:
        """
        Open the RPM's archive payload.

        Yields:
            A tuple of the `rpm.files` object, the payload's open `rpm.fd`, and
            the `rpm.archive` object
        """
        self.fd.seek(self._loc)
        files: rpm.files = rpm.files(self.hdr)
        payload: rpm.fd = rpm.fd(self.fd, "r", self.hdr["payloadcompressor"])
        archive: rpm.archive = files.archive(payload)
        with closing(payload), closing(archive):
            yield files, payload, archive

    def _extract_afile(
        self, archive: rpm.archive, file: rpm.file, destdir: Path
    ) -> Path:
        final = destdir / file.name
        with closing(rpm.fd(str(final), "w")) as fd:
            archive.readto(fd)
        return final

    def extract_specfile(self, destdir: Path) -> Path:
        """
        Extract the SRPM's specfile to `destdir`.

        Args:
            destdir:
                Directory in which to extract the specfile.
                The directory must already exist
        Raises:
            `RPMArchiveError` if `self` is not a *source* RPM

        """
        if not self.hdr.isSource():
            raise RPMArchiveError(f"{self} is not a source rpm")
        with self.unpack_archive() as (_, _, archive):
            for afile in archive:
                if afile.fflags & rpm.RPMFILE_SPECFILE:
                    return self._extract_afile(archive, afile, destdir)
        raise RPMArchiveError("No specfile found in the SRPM")  # pragma: no cover

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *_) -> None:
        self.fd.close()


__all__ = ("RPMArchive", "RPMArchiveError")
