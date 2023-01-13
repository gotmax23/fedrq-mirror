# SPDX-FileCopyrightText: 2022 Maxwell G <gotmax@e.email>
# SPDX-License-Identifier: GPL-2.0-or-later

import pytest

from fedrq import config as rqconfig
from fedrq.backends.base import PackageCompat, PackageQueryCompat, RepoqueryBase


@pytest.mark.no_rpm_mock
def test_make_base_rawhide_repos():
    config = rqconfig.get_config()
    rawhide = config.get_release("rawhide")
    base = rawhide.make_base(fill_sack=False)
    backend: str = config.backend_mod.BACKEND
    if backend == "dnf":
        assert len(tuple(base.repos.iter_enabled())) == len(rawhide.repos)
        assert set(repo.id for repo in base.repos.iter_enabled()) == set(rawhide.repos)
    elif backend == "libdnf5":
        import libdnf5

        repoq = libdnf5.repo.RepoQuery(base)
        repoq.filter_enabled(True)
        assert len(tuple(repoq)) == len(rawhide.repos)
        assert set(repo.get_id() for repo in repoq) == set(rawhide.repos)
    else:
        raise TypeError


def test_package_protocol(repo_test_rq: RepoqueryBase):
    package = repo_test_rq.get_package("packagea", arch="noarch")
    assert isinstance(package, PackageCompat)


def test_query_protocol(repo_test_rq: RepoqueryBase):
    query = repo_test_rq.query()
    assert isinstance(query, PackageQueryCompat)
