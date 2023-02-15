# SPDX-FileCopyrightText: 2022 Maxwell G <gotmax@e.email>
# SPDX-License-Identifier: GPL-2.0-or-later

import glob

TEST_REPO = "repo1"


def test_repo_package_count(repo_test_rq, data_path):
    directory = data_path / "repos" / "repo1"
    count_specs = len(glob.glob(str(directory / "specs/**/*.spec"), recursive=True))
    assert count_specs == len(repo_test_rq.query(arch="src"))
    assert count_specs == 3
