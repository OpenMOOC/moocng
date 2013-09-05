%if ! (0%{?fedora} > 12 || 0%{?rhel} > 5)
%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}
%endif

%global srcname anyjson

Name:           python-%{srcname}
Version:        0.3.3
Release:        1%{?dist}
Summary:        Wraps the best available JSON implementation available

Group:          Development/Languages
License:        BSD
URL:            http://pypi.python.org/pypi/anyjson
Source0:        http://pypi.python.org/packages/source/a/%{srcname}/%{srcname}-%{version}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch:      noarch

BuildRequires:  python-devel
BuildRequires:  python-setuptools


%description
Anyjson loads whichever is the fastest JSON module installed and
provides a uniform API regardless of which JSON implementation is used.


%prep
%setup -q -n %{srcname}-%{version}


%build
%{__python} setup.py build


%install
rm -rf %{buildroot}
%{__python} setup.py install --skip-build --root %{buildroot}


%clean
rm -rf %{buildroot}


%files
%defattr(-,root,root,-)
%doc CHANGELOG LICENSE README
%{python_sitelib}/%{srcname}/
%{python_sitelib}/%{srcname}*.egg-info


%changelog
* Wed Jul 03 2013 Alejandro Blanco <ablanco@yaco.es> - 0.3.3-1
- Upgrade to 0.3.3 version

* Sun Apr 03 2011 Fabian Affolter <fabian@bernewireless.net> - 0.3.1-1
- Updated to new upstream version 0.3.1

* Thu Jan 27 2011 Fabian Affolter <fabian@bernewireless.net> - 0.3-1
- Updated to new upstream version 0.3

* Sat Jul 31 2010 Orcan Ogetbil <oget[dot]fedora[at]gmail[dot]com> - 0.2.4-2
- Rebuilt for https://fedoraproject.org/wiki/Features/Python_2.7/MassRebuild

* Sat Jul 03 2010 Fabian Affolter <fabian@bernewireless.net> - 0.2.4-1
- Initial package
