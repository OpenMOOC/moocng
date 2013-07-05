%if ! (0%{?fedora} > 12 || 0%{?rhel} > 5)
%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}
%endif

%global srcname django-admin-sortable

Name:           python-%{srcname}
Version:        1.4.9
Release:        1%{?dist}
Summary:        Drag and drop sorting for models and inline models in Django admin

Group:          Development/Languages
License:        APL
URL:            http://pypi.python.org/pypi/django-admin-sortable
Source0:        http://pypi.python.org/packages/source/d/%{srcname}/%{srcname}-%{version}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch:      noarch

BuildRequires:  python-devel
BuildRequires:  python-setuptools

Requires: Django14


%description
Drag and drop sorting for models and inline models in Django admin.


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
%{python_sitelib}/adminsortable/
%{python_sitelib}/django_admin_sortable*.egg-info


%changelog
* Thu Jul 04 2013 Alejandro Blanco <ablanco@yaco.es> - 0.3.3-1
- Initial package
