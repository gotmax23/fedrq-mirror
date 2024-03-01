# Copyright (C) 2023 Maxwell G <maxwell@gtmx.me>
# SPDX-License-Identifier: GPL-2.0-or-later

outdir ::= results_fedrq
COPR_URL ::= https://copr.fedorainfracloud.org/coprs/gotmax23/fclogr/repo/fedora-rawhide/gotmax23-fclogr-fedora-rawhide.repo

srpm:
	command -v wget || $(SUDO) dnf install -y wget
	command -v fclogr || $(SUDO) wget $(COPR_URL) -O /etc/yum.repos.d/fclogr.repo
	command -v fclogr || $(SUDO) dnf install -y fclogr
	command -v nox || $(SUDO) dnf install -y nox
	nox --no-venv -e srpm -- -o $(outdir)
