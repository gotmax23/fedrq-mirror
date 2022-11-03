Name:           packageb
Epoch:          11111
Version:        2
Release:        1%{?dist}
Summary:        %{name} is a test package

License:        (Unlicense OR Unlicense OR Unlicense)
URL:            ...
Provides:       package(b)
Provides:       vpackage(b) = %{?epoch:%{epoch}:}%{version}-%{release}


%description
...


%package sub
Summary:        %{name}-sub is a subpackage of %{name}
BuildArch:      noarch
Provides:       subpackage(b)
Provides:       vsubpackage(b) = %{version}-%{release}
# In a proper specfile, this Requires would be versioned.
# This is here to allow us to test fedrq whatrequires.
Requires:       package(b)

Supplements:    (vpackage(b) and package(a))


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

