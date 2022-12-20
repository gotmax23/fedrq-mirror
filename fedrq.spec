# This specfile is licensed under:
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2022 Maxwell G <gotmax@e.email>
Name:           fedrq
Version:        0.0.2
Release:        %autorelease
Summary:        A tool to query the Fedora and EPEL repositories

# - code is GPL-2.0-or-later
# - the data and config files in fedrq/config are UNLICENSEed
License:        GPL-2.0-or-later AND Unlicense
URL:            https://git.sr.ht/~gotmax23/fedrq
Source:         %{url}/archive/%{version}.tar.gz#/fedrq-%{version}.tar.gz

BuildArch:      noarch

BuildRequires:  python3-devel
# Test deps
BuildRequires:  createrepo_c
BuildRequires:  fedora-repos-rawhide
BuildRequires:  python3-dnf
# Manpage
BuildRequires:  scdoc

Requires:       python3-dnf
Requires:       fedora-repos-rawhide

# fedrq config --dump
Recommends:     python3-tomli-w


%description
fedrq is a tool to query the Fedora and EPEL repositories.


%prep
%autosetup -p1

# Workaround F36's old flit-core
# https://bugzilla.redhat.com/show_bug.cgi?id=2155118
rm -r .data/*
sed -i \
    -e 's|^requires = \["flit_core >=3.7,<4"\]|requires = ["flit_core >=3.2,<4"]|' \
    -e '/\[tool.flit.external-data\]/d' \
    -e '/^directory = ".data"$/d' \
    pyproject.toml



%generate_buildrequires
%pyproject_buildrequires -x test


%build
%pyproject_wheel
scdoc < doc/fedrq.1.scd > fedrq.1


%install
%pyproject_install
%pyproject_save_files fedrq
install -Dpm 0644 fedrq.1 -t %{buildroot}%{_mandir}/man1/


%check
%pytest -v -m "not no_rpm_mock"


%files -f %{pyproject_files}
%license LICENSES/GPL-2.0-or-later.txt
%license LICENSES/Unlicense.txt
%doc README.md CONTRIBUTING.md
%{_bindir}/fedrq*
%{_mandir}/man1/fedrq.1*


%changelog
%autochangelog
