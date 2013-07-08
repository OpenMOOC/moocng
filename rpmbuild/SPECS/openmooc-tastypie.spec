#
# spec file for package openmooc-tastypie
#

Name:           openmooc-tastypie
Version:        0.9.11
Release:        1%{?dist}
Url:            http://github.com/OpenMOOC/django-tastypie/
Summary:        Fork of django-tastypie for OpenMOOC
License:        BSD-3-Clause
Group:          Development/Languages/Python
# We had to hardcode the source url
Source:         http://github.com/OpenMOOC/django-tastypie/archive/0.9.11_no_related_saved.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-build
BuildRequires:  python-devel
BuildRequires:  python-distribute
BuildRequires:  make
BuildRequires:  python-sphinx
Requires:       python-mimeparse >= 0.1.3
Requires:       python-dateutil >= 1.5
Requires:       python-django >= 1.2
BuildArch:      noarch

%description
Creating delicious APIs for Django apps since 2010.

%prep
%setup -q -n django-tastypie-0.9.11_no_related_saved

%build
python setup.py build
# Build documentation
cd docs
make html

%install
python setup.py install --prefix=%{_prefix} --root=%{buildroot}

%files
%defattr(-,root,root,-)
%doc AUTHORS LICENSE README.rst docs/_build/html
%{python_sitelib}/*

%changelog
* Fri Jul 5 2013 Oscar Carballal Prego <ocarballal@yaco.es>
- Modification for packaging OpenMOOC fork

* Wed Mar 21 2012 saschpe@gmx.de
- Initial version
