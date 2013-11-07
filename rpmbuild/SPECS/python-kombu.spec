%global srcname kombu

Name:           python-%{srcname}
Version:        2.5.12
Release:        1%{?dist}
Summary:        AMQP Messaging Framework for Python

Group:          Development/Languages
# utils/functional.py contains a header that says Python
License:        BSD and Python
URL:            http://pypi.python.org/pypi/%{srcname}
Source0:        http://pypi.python.org/packages/source/k/%{srcname}/%{srcname}-%{version}.tar.gz
BuildArch:      noarch

BuildRequires:  python2-devel
BuildRequires:  python-setuptools
BuildRequires:  python-nose
BuildRequires:  python-anyjson >= 0.3.3
BuildRequires:  python-amqplib
BuildRequires:  python-msgpack
# For documentation
#BuildRequires:  pymongo python-sphinx
#This causes tests error, needs fixing upstream. Incompatible with python > 2.7
#BuildRequires:  python-couchdb

%description
AMQP is the Advanced Message Queuing Protocol, an open standard protocol
for message orientation, queuing, routing, reliability and security.

One of the most popular implementations of AMQP is RabbitMQ.

The aim of Kombu is to make messaging in Python as easy as possible by
providing an idiomatic high-level interface for the AMQP protocol, and
also provide proven and tested solutions to common messaging problems.

%prep
%setup -q -n %{srcname}-%{version}
# Remove shehang
sed -i -e '/^#!\//, 1d' kombu/tests/test_serialization.py
# Remove hidden files
rm -rf docs/.static

%build
%{__python} setup.py build

%install
%{__python} setup.py install --skip-build --root %{buildroot}

# Documentation in docs folder is not useful without doing a make
# Seems to have a circular dependency.  Not building for now
#cd docs && make html
#cd - && mv docs/.build/html htmldocs
#rm -rf docs
#rm -f htmldocs/.buildinfo

%%check
#cd %%{srcname}/tests
#nosetests *.py

%files
%doc AUTHORS Changelog FAQ LICENSE READ* THANKS TODO examples/
%{python_sitelib}/%{srcname}/
%{python_sitelib}/%{srcname}*.egg-info

%changelog
* Tue Jul  2 2013 Alejandro Blanco <ablanco@yaco.es> - 2.5.12
-Upgrade to 2.5.12 version

* Fri Jul 15 2011 Rahul Sundaram <sundaram@fedoraproject.org> - 1.1.3-1
- initial spec.
- derived from the one written by Fabian Affolter
- spec patch from Lakshmi Narasimhan

