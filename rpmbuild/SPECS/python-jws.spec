%{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}

%define srcname jws

Name:           python-%{srcname}
Version:        0.1.0
Release:        1%{?dist}
Summary:        JSON Web Signatures implementation in Python

Group:          Development/Languages
License:        Python
URL:            http://github.com/brianlovesdata/python-%{srcname}
Source0:        https://pypi.python.org/packages/source/j/%{srcname}/%{srcname}-%{version}.tar.gz

BuildArch:      noarch
BuildRequires:  python-devel, python-setuptools

%description
A Python implementation of JSON Web Signatures draft 02
http://self-issued.info/docs/draft-jones-json-web-signature.html

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
%doc README.md README.txt
%{python_sitelib}/%{srcname}
%{python_sitelib}/%{srcname}-%{version}-py*.egg-info/

%changelog

* Fri Oct 11 2013 Alejandro Blanco <ablanco@yaco.es> - 0.1.0-1
- Initial package
