# Copyright (C) 2023 Maxwell G <gotmax@e.email>
#
# SPDX-License-Identifier: GPL-2.0-or-later

import pytest


@pytest.mark.parametrize(
    "args",
    [
        pytest.param(["packageb"]),
        pytest.param(["packageb.src"]),
    ],
)
def test_whatrequires_src(run_command2, args):
    stdout, stderr = run_command2(["wrsrc", "packageb", "-F", "source"], False)
    assert not stderr
    assert stdout == ["packagea", "packageb"]


def test_whatrequires_src_exclude(run_command2):
    stdout, stderr = run_command2(
        ["whatrequires-src", "packageb", "-F", "source", "-X"], False
    )
    assert not stderr
    assert stdout == ["packagea"]
