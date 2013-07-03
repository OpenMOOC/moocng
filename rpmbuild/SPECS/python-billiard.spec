%if ! (0%{?fedora} > 12 || 0%{?rhel} > 5)
%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}
%endif

%global srcname billiard

Name:           python-%{srcname}
Version:        2.7.3.28
Release:        1%{?dist}
Summary:        Multiprocessing Pool Extensions

Group:          Development/Languages
License:        BSD
URL:            http://pypi.python.org/pypi/billiard
Source0:        http://pypi.python.org/packages/source/b/%{srcname}/%{srcname}-%{version}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch:      noarch

BuildRequires:  python-devel
BuildRequires:  python-setuptools


%description
This package contains extensions to the multiprocessing Pool.


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
%doc AUTHORS Changelog LICENSE README TODO docs/
%{python_sitelib}/%{srcname}/
%{python_sitelib}/%{srcname}*.egg-info


%changelog
* Wed Jul 03 2013 Alejandro Blanco <ablanco@yaco.es> - 2.7.3.28-1
- Upgrade to 2.7.3.28 version

* Tue Feb 08 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.3.1-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Sat Aug 14 2010 Fabian Affolter <fabian@bernewireless.net> - 0.3.1-2
- TODO removed

* Sat Jul 03 2010 Fabian Affolter <fabian@bernewireless.net> - 0.3.1-1
- Initial package
