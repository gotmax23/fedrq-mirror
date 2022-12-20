# SPDX-FileCopyrightText: 2022 Maxwell G <gotmax@e.email>
# SPDX-License-Identifier: GPL-2.0-or-later

import pytest

import fedrq.cli


@pytest.mark.no_rpm_mock
def test_pkgs_basic_rawhide(capsys, target_cpu):
    fedrq.cli.main(["pkgs", "bash", "-Fna"])
    stdout, stderr = capsys.readouterr()
    assert stdout.splitlines() == ["bash.src", f"bash.{target_cpu}"]
