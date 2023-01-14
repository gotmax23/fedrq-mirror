# This specfile is licensed under:
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2022 Maxwell G <gotmax@e.email>
Name:           fedrq
Version:        0.2.0
Release:        1%{?dist}
Summary:        A tool to query the Fedora and EPEL repositories

# - code is GPL-2.0-or-later
# - the data and config files in fedrq/config are UNLICENSEed
# - Embeded repo defs are MIT.
License:        GPL-2.0-or-later AND Unlicense AND MIT
URL:            https://git.sr.ht/~gotmax23/fedrq
Source:         %{url}/refs/download/v%{version}/fedrq-%{version}.tar.gz

BuildArch:      noarch

BuildRequires:  python3-devel
# Test deps
BuildRequires:  createrepo_c
BuildRequires:  fedora-repos-rawhide
BuildRequires:  distribution-gpg-keys
BuildRequires:  python3-dnf
# Manpage
BuildRequires:  scdoc

Requires:       python3-dnf
Requires:       (fedora-repos-rawhide or distribution-gpg-keys)
Suggests:       distribution-gpg-keys

# fedrq config --dump
Recommends:     python3-tomli-w


%description
fedrq is a tool to query the Fedora and EPEL repositories.


%prep
%autosetup -p1


%generate_buildrequires
%pyproject_buildrequires -x test


%build
%pyproject_wheel
scdoc < doc/fedrq.1.scd > fedrq.1
scdoc < doc/fedrq.5.scd > fedrq.5


%install
%pyproject_install
%pyproject_save_files fedrq
install -Dpm 0644 fedrq.1 -t %{buildroot}%{_mandir}/man1/
install -Dpm 0644 fedrq.5 -t %{buildroot}%{_mandir}/man5/


%check
%pytest -v -m "not no_rpm_mock"


%files -f %{pyproject_files}
# Licenses are included in the wheel
%license %{_licensedir}/fedrq/
%doc README.md CONTRIBUTING.md
%{_bindir}/fedrq*
%{_mandir}/man1/fedrq.1*
%{_mandir}/man5/fedrq.5*


%changelog
* Sat Jan 14 2023 Maxwell G <gotmax@e.email> - 0.2.0-1
- Release 0.2.0

* Tue Jan 03 2023 Maxwell G <gotmax@e.email> 0.1.0-1
- Release 0.1.0

* Tue Dec 20 2022 Maxwell G <gotmax@e.email> 0.0.2-1
- Release 0.0.2

* Tue Dec 20 2022 Maxwell G <gotmax@e.email> 0.0.1-1
- Release 0.0.1
