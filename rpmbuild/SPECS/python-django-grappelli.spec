%if ! (0%{?fedora} > 12 || 0%{?rhel} > 5)
%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}
%endif

%global srcname django-grappelli

Name:           python-%{srcname}
Version:        2.4.5
Release:        1%{?dist}
Summary:        A jazzy skin for the Django Admin-Interface

Group:          Development/Languages
License:        BSD
URL:            http://pypi.python.org/pypi/%{srcname}
Source0:        http://pypi.python.org/packages/source/d/%{srcname}/%{srcname}-%{version}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch:      noarch

BuildRequires:  python-devel
BuildRequires:  python-setuptools

Requires: Django14


%description
A jazzy skin for the Django admin interface.

Grappelli is a grid-based alternative/extension to the Django administration
interface.


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
%{python_sitelib}/grappelli/
%{python_sitelib}/django_grappelli*.egg-info


%changelog
* Fri Jul 05 2013 Alejandro Blanco <ablanco@yaco.es> - 0.3.3-1
- Initial package
