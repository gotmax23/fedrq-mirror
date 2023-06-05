# Copyright (C) 2023 Maxwell G <maxwell@gtmx.me>
#
# SPDX-License-Identifier: GPL-2.0-or-later

from __future__ import annotations

import pytest

import fedrq.config


@pytest.mark.parametrize(
    "args",
    [
        pytest.param("gotmax23/fedrq"),
        pytest.param("gotmax23/fedrq@copr.fedoraproject.org/"),
        pytest.param("gotmax23/fedrq@https://copr.fedoraproject.org/"),
        pytest.param("gotmax23/fedrq@copr.fedoraproject.org"),
        pytest.param("gotmax23/fedrq@https://copr.fedoraproject.org"),
    ],
)
def test_copr_repo(args):
    config = fedrq.config.get_config()
    f37 = config.get_release("f37")
    url = f37._copr_repo(args)
    assert url == "https://copr.fedoraproject.org/coprs/gotmax23/fedrq/repo/fedora-37"


@pytest.mark.parametrize(
    "args",
    [
        pytest.param("@python/python3.12"),
        pytest.param("@python/python3.12@copr.fedoraproject.org/"),
        pytest.param("@python/python3.12@https://copr.fedoraproject.org/"),
        pytest.param("@python/python3.12@copr.fedoraproject.org"),
        pytest.param("@python/python3.12@https://copr.fedoraproject.org"),
    ],
)
def test_copr_repo_group(args):
    config = fedrq.config.get_config()
    rawhide = config.get_release("rawhide")
    url = rawhide._copr_repo(args)
    expected = (
        "https://copr.fedoraproject.org/coprs/g/python/python3.12/repo/fedora-rawhide"
    )
    assert url == expected


def test_copr_custom():
    config = fedrq.config.get_config()
    rawhide = config.get_release("rawhide")
    url = rawhide._copr_repo("@python/python3.12@example.com")
    assert url == "https://example.com/coprs/g/python/python3.12/repo/fedora-rawhide"
