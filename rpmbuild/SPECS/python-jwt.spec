%{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}

%define srcname jwt

Name:           python-%{srcname}
Version:        0.2.0
Release:        1%{?dist}
Summary:        Module for generating and verifying JSON Web Tokens.

Group:          Development/Languages
License:        MIT
URL:            https://github.com/davedoesdev/python-%{srcname}
Source0:        https://pypi.python.org/packages/source/p/python_%{srcname}/python_%{srcname}-%{version}.tar.gz
Source1:        python-jwt-setup.py

BuildArch:      noarch
BuildRequires:  python-devel, python-setuptools

Requires:       python-jws = 0.1.0

%description
Module for generating and verifying JSON Web Tokens.

  Uses jws to do the heavy lifting.
  Supports RS256, RS384, RS512, PS256, PS384, PS512, HS256, HS384, HS512 and
  none signature algorithms.

%prep
%setup -q -n python_%{srcname}-%{version}
cp -vf %{SOURCE1} setup.py

%build
%{__python} setup.py build

%install
rm -rf $RPM_BUILD_ROOT
%{__python} setup.py install -O1 --skip-build --root $RPM_BUILD_ROOT

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root,-)
%doc README.rst
%{python_sitelib}/%{srcname}
%{python_sitelib}/%{srcname}-%{version}-py*.egg-info/

%changelog

* Thu Oct 10 2013 Alejandro Blanco <ablanco@yaco.es> - 0.2.0-1
- Initial package
