# SPDX-FileCopyrightText: 2022 Maxwell G <gotmax@e.email>
# SPDX-License-Identifier: GPL-2.0-or-later


from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from typing import Any, cast

import pytest

from fedrq import config as rqconfig
from fedrq.backends.base import (
    BackendMod,
    PackageCompat,
    PackageQueryCompat,
    RepoqueryBase,
)
from fedrq.release_repo import MultiNameG


def test_make_base_rawhide_repos() -> None:
    config = rqconfig.get_config()
    rawhide = config.get_release("rawhide")
    bm = config.backend_mod.BaseMaker()
    base = rawhide.make_base(config, fill_sack=False, base_maker=bm)  # noqa: F841
    repos = bm.repolist(True)
    repog = cast(MultiNameG, rawhide.repog)
    assert len(repos) == len(repog.repos)
    assert set(repos) == set(repog.repos)


def test_package_protocol(repo_test_rq: RepoqueryBase):
    package = repo_test_rq.get_package("packagea", arch="noarch")
    assert isinstance(package, PackageCompat)


def test_query_protocol(repo_test_rq: RepoqueryBase):
    query = repo_test_rq.query()
    assert isinstance(query, PackageQueryCompat)


def test_baseurl_repog(repo_test_rq: RepoqueryBase, data_path: Path):
    for i in ("", "file://"):
        second_rq = rqconfig.get_config().get_rq(
            "rawhide", f"@baseurl:{i}{data_path/ 'repos' / 'repo1' / 'repo'}"
        )
        assert sorted(map(str, repo_test_rq.query())) == sorted(
            map(str, second_rq.query())
        )


@pytest.mark.parametrize("explicit_forms", [pytest.param(True), pytest.param(False)])
def test_resolve_pkg_specs_forms(
    explicit_forms: bool, repo_test_rq: RepoqueryBase, default_backend: BackendMod
) -> None:
    packages = [repo_test_rq.get_package("packagea", arch="noarch")]
    assert len(packages) == 1
    packages2 = packages + [repo_test_rq.get_package("packagea", arch="src")]

    func = repo_test_rq.resolve_pkg_specs
    forms = default_backend.NEVRAForms

    # nevra_forms excludes "packagea.noarch" (0)
    nevra_forms: list[int] | None = [forms.NAME]
    assert not list(func(["packagea.noarch"], nevra_forms=nevra_forms))

    # forms.NAME (2)
    nevra_forms = [forms.NAME] if explicit_forms else None
    assert list(func(["packagea"], nevra_forms=nevra_forms)) == packages2

    # forms.NEV (2)
    nevra_forms = [forms.NEV] if explicit_forms else None
    assert list(func(["packagea-0:1"], nevra_forms=nevra_forms)) == packages2

    # forms.NA (1)
    nevra_forms = [forms.NAME, forms.NA]
    assert list(func(["packagea.noarch"], nevra_forms=nevra_forms)) == packages

    # forms.NEVRA (1)
    nevra_forms = [forms.NEVRA]
    assert list(func(["packagea-1-1.fc36.noarch"], nevra_forms=nevra_forms)) == packages


@pytest.mark.parametrize(
    "specs,kwargs,count",
    [
        pytest.param(["/usr/share/packagea"], {"resolve": True}, 1, id="resolve"),
        pytest.param(
            ["/usr/share/packagea"], {"resolve": False}, 0, id="resolve-false"
        ),
        pytest.param(
            ["/usr/share/packagea"],
            {"resolve": True, "with_filenames": False},
            0,
            id="resolve-without-filenames",
        ),
        pytest.param(
            ["/usr/share/packagea", "package(a)"],
            {"resolve": True, "with_filenames": False},
            1,
            id="resolve-without-filenames-provides",
        ),
        pytest.param(
            ["/usr/share/packagea"],
            {"resolve": True, "with_filenames": True},
            1,
            id="resolve-with-explict-filenames",
        ),
        pytest.param(
            ["/usr/share/packagea"],
            {"with_filenames": True},
            1,
            id="with-filenames",
        ),
    ],
)
def test_resolve_pkg_specs_resolve(
    repo_test_rq: RepoqueryBase,
    specs: Sequence[str],
    kwargs: dict[str, Any],
    count: int,
    request: pytest.FixtureRequest,
) -> None:
    results = repo_test_rq.resolve_pkg_specs(specs, **kwargs)
    canfail = False
    # https://github.com/rpm-software-management/libdnf/issues/1673
    if (
        request.node.callspec.id == "resolve-without-filenames"
        and repo_test_rq.backend.BACKEND == "dnf"
    ):
        import hawkey

        if hawkey.VERSION == "0.73.3":
            canfail = True
    try:
        assert len(results) == count
    except AssertionError:
        if not canfail:
            raise
        pytest.xfail("rpm-software-management/libdnf/issues/1673")
