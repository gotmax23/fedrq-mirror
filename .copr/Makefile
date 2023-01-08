# SPDX-FileCopyrightText: 2022 Maxwell G <gotmax@e.email>
# SPDX-License-Identifier: GPL-2.0-or-later

outdir ::= results_fedrq
srpm:
	dnf install -y --setopt=install_weak_deps=False \
		git-core fedpkg rpmdevtools python3-specfile
	python -m venv venv --system-site-packages
	. ./venv/bin/activate
	pip install fclogr
	./srpm.sh $(outdir)
