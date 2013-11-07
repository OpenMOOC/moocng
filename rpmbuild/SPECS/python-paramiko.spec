%{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}

%define srcname paramiko

Name:           python-%{srcname}
Version:        1.10.4
Release:        1%{?dist}
Summary:        Paramiko is a library for making SSH2 connections (client or server).

Group:          Development/Languages
License:        Python
URL:            https://github.com/%{srcname}/%{srcname}
Source0:        https://pypi.python.org/packages/source/p/%{srcname}/%{srcname}-%{version}.tar.gz

BuildArch:      noarch
BuildRequires:  python-devel, python-setuptools

Requires:       python-crypto >= 2.5

%description
This is a library for making SSH2 connections (client or server). Emphasis is
on using SSH2 as an alternative to SSL for making secure connections between
python scripts. All major ciphers and hash methods are supported. SFTP client
and server mode are both supported too.

%prep
%setup -q -n %{srcname}-%{version}

%build
%{__python} setup.py build

%install
rm -rf $RPM_BUILD_ROOT
%{__python} setup.py install -O1 --skip-build --root $RPM_BUILD_ROOT

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root,-)
%doc README LICENSE
%{python_sitelib}/%{srcname}
%{python_sitelib}/%{srcname}-%{version}-py*.egg-info/

%changelog

* Thu Oct 03 2013 Alejandro Blanco <ablanco@yaco.es> - 1.10.4-1
- Initial package
