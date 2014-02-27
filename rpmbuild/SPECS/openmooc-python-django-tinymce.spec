%global modname tinymce

Name:               openmooc-python-django-tinymce
Version:            2.0.0
Release:            1%{?dist}
Summary:            A Django application that contains a widget to render a form field as a TinyMCE editor.

Group:              Development/Libraries
License:            MIT
URL:                https://github.com/OpenMOOC/django-tinymce
Source0:            https://github.com/OpenMOOC/django-tinymce/archive/${version}.tar.gz

BuildArch:          noarch
Conflicts:          python-django-tinymce
BuildRequires:      python2-devel
BuildRequires:      python-setuptools

%description
django-tinymce is a Django application that contains a widget to render
a form field as a TinyMCE editor.

%prep
%setup -q -n django-tinymce-%{version}

# Remove bundled egg-info in case it exists
rm -rf %{modname}.egg-info

%build
%{__python} setup.py build

%install
%{__python} setup.py install -O1 --skip-build --root=%{buildroot}

%check
%{__python} setup.py test

# Remove tests once done with them
rm -rf %{buildroot}%{python_sitelib}/testtinymce/

%files
%doc docs/ LICENSE.txt
%{python_sitelib}/%{modname}/
%{python_sitelib}/django_tinymce-%{version}*

%changelog
* Mon Feb 04 2013 Ralph Bean <rbean@redhat.com> - 1.5.1b4-1
- Initial packaging for Fedora
