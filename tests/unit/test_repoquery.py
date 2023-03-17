# SPDX-FileCopyrightText: 2022 Maxwell G <gotmax@e.email>
# SPDX-License-Identifier: GPL-2.0-or-later


from fedrq import config as rqconfig
from fedrq.backends.base import PackageCompat, PackageQueryCompat, RepoqueryBase


def test_make_base_rawhide_repos() -> None:
    config = rqconfig.get_config()
    rawhide = config.get_release("rawhide")
    bm = config.backend_mod.BaseMaker()
    base = rawhide.make_base(config, fill_sack=False, base_maker=bm)  # noqa: F841
    repos = bm.repolist(True)
    assert len(repos) == len(rawhide.repog.repos)
    assert set(repos) == set(rawhide.repog.repos)


def test_package_protocol(repo_test_rq: RepoqueryBase):
    package = repo_test_rq.get_package("packagea", arch="noarch")
    assert isinstance(package, PackageCompat)


def test_query_protocol(repo_test_rq: RepoqueryBase):
    query = repo_test_rq.query()
    assert isinstance(query, PackageQueryCompat)
