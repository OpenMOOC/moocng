%define mod_name mathjax
%define realm django

Name:           %{realm}-%{mod_name}
Version:        0.0.2
Release:        1%{?dist}
Summary:        Application to easy include MathJax in your django projects

Group:          Development/Libraries
License:        BSD License
URL:            http://pypi.python.org/pypi/%{name}
Source0:        https://pypi.python.org/packages/source/d/%{name}/%{name}-%{version}.tar.gz

BuildArch:      noarch
BuildRequires:  python-devel python-setuptools
Requires:       Django14


%description
Django-mathjax is an application to easy include MathJax in your django
projects as dependency, and easy configure directly from django settings.


%prep
%setup -q -n %{name}-%{version}


%build
%{__python} setup.py build


%install
%{__python} setup.py install -O1 --skip-build --root %{buildroot}


%files
%{python_sitelib}/%{realm}_%{mod_name}-%{version}-*.egg-info/
%{python_sitelib}/%{realm}_%{mod_name}/


%changelog
* Thu Jul 4 2013 Oscar Carballal Prego <ocarballal@yaco.es> - 0.0.2-1
- Initial RPM release
