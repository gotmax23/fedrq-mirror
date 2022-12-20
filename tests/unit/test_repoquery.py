# SPDX-FileCopyrightText: 2022 Maxwell G <gotmax@e.email>
# SPDX-License-Identifier: GPL-2.0-or-later

import pytest

from fedrq import config as rqconfig


@pytest.mark.no_rpm_mock
def test_make_base_rawhide_repos():
    config = rqconfig.get_config()
    rawhide = config.get_release("rawhide")
    base = rawhide.make_base(fill_sack=False)
    assert len(tuple(base.repos.iter_enabled())) == len(rawhide.repos)
    assert set(repo.id for repo in base.repos.iter_enabled()) == set(rawhide.repos)
