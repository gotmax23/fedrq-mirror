# This specfile is licensed under:
#
# Copyright (C) 2022 Maxwell G <gotmax@e.email>
# SPDX-License-Identifier: MIT
# License text: https://spdx.org/licenses/MIT.html

%bcond libdnf5 %[0%{?fedora} >= 38]

Name:           fedrq
Version:        0.6.0
Release:        1%{?dist}
Summary:        A tool to query the Fedora and EPEL repositories

# - code is GPL-2.0-or-later
# - the data and config files in fedrq/data are UNLICENSEed
# - Embeded repo defs are MIT.
# - PSF-2.0 code copied from Cpython 3.11 for older Python versions
License:        GPL-2.0-or-later AND Unlicense AND MIT AND PSF-2.0
URL:            https://fedrq.gtmx.me
%global furl    https://git.sr.ht/~gotmax23/fedrq
Source0:        %{furl}/refs/download/v%{version}/fedrq-%{version}.tar.gz

BuildArch:      noarch

BuildRequires:  python3-devel
# Test deps
BuildRequires:  createrepo_c
BuildRequires:  fedora-repos-rawhide
BuildRequires:  distribution-gpg-keys
BuildRequires:  python3-argcomplete
BuildRequires:  python3-dnf
%if %{with libdnf5}
BuildRequires:  python3-libdnf5
BuildRequires:  python3-rpm
%endif
# Manpage
BuildRequires:  scdoc

Requires:       (python3-dnf or (python3-libdnf5 and python3-rpm))
Suggests:       python3-dnf
Requires:       distribution-gpg-keys
Recommends:     fedora-repos-rawhide
Recommends:     python3-argcomplete

# fedrq config --dump
Recommends:     python3-tomli-w


%description
fedrq is a tool to query the Fedora and EPEL repositories.


%prep
%autosetup -p1


%generate_buildrequires
%pyproject_buildrequires -x test


%build
%py3_shebang_fix contrib/api_examples/*.py

%pyproject_wheel
scdoc <doc/fedrq.1.scd >fedrq.1
scdoc <doc/fedrq.5.scd >fedrq.5
register-python-argcomplete --shell bash fedrq >fedrq.bash
register-python-argcomplete --shell fish fedrq >fedrq.fish


%install
%pyproject_install
%pyproject_save_files fedrq
install -Dpm 0644 fedrq.1 -t %{buildroot}%{_mandir}/man1/
install -Dpm 0644 fedrq.5 -t %{buildroot}%{_mandir}/man5/
install -Dpm 0644 fedrq.bash %{buildroot}%{bash_completions_dir}/fedrq
install -Dpm 0644 fedrq.fish %{buildroot}%{fish_completions_dir}/fedrq.fish


%check
FEDRQ_BACKEND=dnf %pytest -v -m "not no_rpm_mock"
%if %{with libdnf5}
FEDRQ_BACKEND=libdnf5 %pytest -v -m "not no_rpm_mock"
%endif


%files -f %{pyproject_files}
# Licenses are included in the wheel
%license %{_licensedir}/fedrq/
%doc README.md CONTRIBUTING.md NEWS.md contrib/api_examples
%{_bindir}/fedrq*
%{bash_completions_dir}/fedrq
%{fish_completions_dir}/fedrq.fish
%{_mandir}/man1/fedrq.1*
%{_mandir}/man5/fedrq.5*


%changelog
* Sat Apr 08 2023 Maxwell G <maxwell@gtmx.me> - 0.6.0-1
- Release 0.6.0

* Sat Mar 18 2023 Maxwell G <maxwell@gtmx.me> - 0.5.0-1
- Release 0.5.0

* Tue Mar 14 2023 Maxwell G <maxwell@gtmx.me> - 0.4.1-1
- Release 0.4.1

* Tue Feb 21 2023 Maxwell G <maxwell@gtmx.me> - 0.4.0-1
- Release 0.4.0

* Mon Feb 13 2023 Maxwell G <gotmax@e.email> - 0.3.0-1
- Release 0.3.0

* Sat Jan 14 2023 Maxwell G <gotmax@e.email> - 0.2.0-1
- Release 0.2.0

* Tue Jan 03 2023 Maxwell G <gotmax@e.email> 0.1.0-1
- Release 0.1.0

* Tue Dec 20 2022 Maxwell G <gotmax@e.email> 0.0.2-1
- Release 0.0.2

* Tue Dec 20 2022 Maxwell G <gotmax@e.email> 0.0.1-1
- Release 0.0.1
