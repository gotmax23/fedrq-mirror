# SPDX-FileCopyrightText: 2022 Maxwell G <gotmax@e.email>
# SPDX-License-Identifier: GPL-2.0-or-later

Name:           packageb
Version:        1
Release:        1%{?dist}
Summary:        %{name} is a test package

License:        (Unlicense OR Unlicense OR Unlicense)
URL:            ...

Provides:       package(b)
Provides:       vpackage(b) = %{?epoch:%{epoch}:}%{version}-%{release}
Recommends:     subpackage(b)


%description
...


%package sub
Summary:        %{name}-sub is a subpackage of %{name}
BuildArch:      noarch
Provides:       subpackage(b)
Provides:       vsubpackage(b) = %{version}-%{release}
# In a proper specfile, vpackage(b) should be replaced with the actual name.
# This is here to allow us to test fedrq whatrequires.
Requires:       vpackage(b) = %{?epoch:%{epoch}:}%{version}-%{release}


%description sub
%{name}-sub is a subpackage of %{name}.

%prep


%build


%install

echo '%{name}' | install -Dpm 0644 /dev/stdin %{buildroot}%{_datadir}/%{name}
echo '%{name}-sub' | install -Dpm 0644 /dev/stdin %{buildroot}%{_datadir}/%{name}-sub

%check


%files
%{_datadir}/%{name}

%files sub
%{_datadir}/%{name}-sub


%changelog

* Sun Jul 16 2023 Maxwell G <maxwell@gtmx.me> - 1-1
- Dummy changelog entry
