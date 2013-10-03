%{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}

%define srcname pycrypto

Name:           python-crypto
Version:        2.6
Release:        1%{?dist}
Summary:        This is a collection of both secure hash functions, and various encryption algorithms.

Group:          Development/Languages
License:        Python
URL:            https://pypi.python.org/pypi/%{srcname}/%{version}
Source0:        https://pypi.python.org/packages/source/p/%{srcname}/%{srcname}-%{version}.tar.gz

BuildRequires:  python-devel, python-setuptools, make, gcc

%description
This is a collection of both secure hash functions (such as SHA256 and
RIPEMD160), and various encryption algorithms (AES, DES, RSA, ElGamal, etc.).
The package is structured to make adding new modules easy. This section is
essentially complete, and the software interface will almost certainly not
change in an incompatible way in the future; all that remains to be done is to
fix any bugs that show up.

%prep
%setup -q

%build
%{__python} setup.py build

%install
rm -rf $RPM_BUILD_ROOT
%{__python} setup.py install -O1 --skip-build --root $RPM_BUILD_ROOT

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root,-)
%doc README ACKS ChangeLog COPYRIGHT TODO
%{python_sitelib}/%{srcname}
%{python_sitelib}/%{srcname}-%{version}-py*.egg-info/

%changelog

* Thu Oct 03 2013 Alejandro Blanco <ablanco@yaco.es> - 2.6-1
- Initial package
