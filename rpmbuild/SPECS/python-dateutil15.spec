%global srcname python-dateutil
Name:           python-dateutil15
Version:        1.5
Release:        2%{?dist}
Summary:        Powerful extensions to the standard datetime module

Group:          Development/Languages
License:        Python
URL:            http://labix.org/python-dateutil
Source0:        http://labix.org/download/%{srcname}/%{srcname}-%{version}.tar.gz

BuildArch:      noarch
BuildRequires:  python-devel,python-setuptools

%description
The dateutil module provides powerful extensions to the standard datetime
module available in Python 2.3+.  This is a parallel installable newer version
for EPEL 6 only.  RHEL 6 base has python-dateutil 1.4.1

%prep
%setup -q -n %{srcname}-%{version}
iconv --from=ISO-8859-1 --to=UTF-8 NEWS > NEWS.new
mv NEWS.new NEWS

%build
%{__python} setup.py build

%install
rm -rf %{buildroot}
%{__python} setup.py install --skip-build --root %{buildroot}

%clean
rm -rf %{buildroot}

%files
%doc example.py LICENSE NEWS README
%{python_sitelib}/dateutil
%{python_sitelib}/python_dateutil-1.5-py2.6.egg-info

%changelog
* Wed Oct 02 2013 Alejandro Blanco <ablanco@yaco.es> - 1.5-2
- Change egg build and installation method

* Wed Jul 13 2011 Rahul Sundaram <sundaram@fedoraproject.org> - 1.5-1
- parallel installable newer version
- askbot indirectly requires this newer version via python-celery
