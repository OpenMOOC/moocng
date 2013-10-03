%{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}

%define component Fabric

Name:           python-fabric
Version:        1.7.0
Release:        1%{?dist}
Summary:        Fabric is library and command-line tool for streamlining the use of SSH.

Group:          Development/Languages
License:        Python
URL:            https://pypi.python.org/pypi/%{component}/%{version}
Source0:        https://pypi.python.org/packages/source/F/%{component}/%{component}-%{version}.tar.gz

BuildArch:      noarch
BuildRequires:  python-devel, python-setuptools

%description
Fabric is a Python (2.5 or higher) library and command-line tool for
streamlining the use of SSH for application deployment or systems
administration tasks.

It provides a basic suite of operations for executing local or remote shell
commands (normally or via sudo) and uploading/downloading files, as well as
auxiliary functionality such as prompting the running user for input, or
aborting execution.

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
%doc README.rst LICENSE AUTHORS INSTALL
%attr(755,root, %{name}) %{_bindir}/fab
%{python_sitelib}/fabfile
%{python_sitelib}/fabric
%{python_sitelib}/%{component}-%{version}-py*.egg-info/

%changelog

* Thu Oct 03 2013 Alejandro Blanco <ablanco@yaco.es> - 1.7.0-1
- Initial package
