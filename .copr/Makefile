# Copyright (C) 2023 Maxwell G <maxwell@gtmx.me>
# SPDX-License-Identifier: GPL-2.0-or-later

outdir ::= results_fedrq

srpm:
	command -v pip || $(SUDO) dnf install -y python3-pip
	command -v fclogr || $(SUDO) dnf install -y python3-pygit2
	command -v fclogr || pip install --user fclogr
	command -v nox || $(SUDO) dnf install -y nox
	python3 -m nox --no-venv -e srpm -- -o $(outdir)
