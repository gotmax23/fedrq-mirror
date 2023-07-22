# Copyright (C) 2023 Maxwell G <gotmax@e.email>
#
# SPDX-License-Identifier: GPL-2.0-or-later

from __future__ import annotations

import pytest

from fedrq.backends.base import BackendMod

# ruff: noqa: E501
TEST_REPO = "https://download.copr.fedorainfracloud.org/results/gotmax23/community.general.copr_integration_tests/fedora-$releasever-$basearch/"
TEST_REPO_KEY = "https://download.copr.fedorainfracloud.org/results/gotmax23/community.general.copr_integration_tests/pubkey.gpg"
TEST_BASEARCH = "x86_64"
TEST_RELEASEVER = "37"


@pytest.mark.no_rpm_mock
def test_bm_create_repo_failure(default_backend: BackendMod) -> None:
    bm = default_backend.BaseMaker()
    bm.sets({}, dict(basearch=TEST_BASEARCH, releasever="nonexistant"))
    bm.create_repo(
        "copr_integration_tests",
        baseurl=[TEST_REPO],
        skip_if_unavailable=False,
    )
    with pytest.raises(default_backend.RepoError):
        default_backend.Repoquery(bm.fill_sack())


@pytest.mark.parametrize(
    "baseurl",
    (
        (TEST_REPO),
        (
            TEST_REPO.replace("$basearch", TEST_BASEARCH).replace(
                "$releasever", TEST_RELEASEVER
            )
        ),
    ),
)
@pytest.mark.no_rpm_mock
def test_bm_create_repo_full(default_backend: BackendMod, baseurl):
    bm = default_backend.BaseMaker()
    bm.sets({}, dict(basearch=TEST_BASEARCH, releasever=TEST_RELEASEVER))
    bm.create_repo(
        "copr_integration_tests",
        baseurl=[TEST_REPO],
        skip_if_unavailable=False,
        type="rpm-md",
        gpgcheck=True,
        repo_gpgcheck=False,
    )
    rq = default_backend.Repoquery(bm.fill_sack())
    query = rq.query()
    assert {p.name for p in query} == {"copr-module-integration-dummy-package"}
