# -*- coding: utf-8 -*-
# Copyright 2012-2013 UNED
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import fnmatch
import os
from setuptools import setup, find_packages


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()


def recursive_include(directory, patterns):
    result = []
    for root, dirs, files in os.walk(directory):
        child_root = root.replace(directory, '').lstrip('/')
        for pattern in patterns:
            result.extend([os.path.join(child_root, name)
                           for name in fnmatch.filter(files, pattern)])
    return result


# be careful with the syntax of this line since it is parsed from
# the docs/conf.py file
VERSION = '0.1.3'


setup(
    name='moocng',
    version=VERSION,
    url='https://github.com/OpenMOOC/moocng',
    license='Apache 2.0 Software License',
    description=('MOOC web tool'),
    long_description=(read('README.rst') + '\n\n' + read('CHANGES')),
    author='UNED',
    classifiers=[
        'Development Status :: 6 - Development',
        'Environment :: Web Environment',
        'Framework :: Django',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
    packages=find_packages('.'),
    package_dir={'moocng': 'moocng'},
    package_data={
        'moocng': recursive_include('moocng', [
            '*.html', '*.css', '*.js', '*.txt', '*.png', '*.ico', '*.wsgi',
            '*.xml', '*.gif', '*.jpg', '*.otf', '*.svg', '*.example', '*.woff',
        ])
    },
    zip_safe=False,
    install_requires=[
        'boto>=2.8.0',
        'celery==3.0.20',
        'Django==1.4.8',
        'django-admin-sortable==1.4.9',
        'django-celery==3.0.17',
        'django-tinymce==2.0.0-openmooc',
        'django-tastypie==0.9.11-openmooc',
        'South==0.7.5',
        'psycopg2==2.4.2',
        'pymongo==2.4.2',
        'djangosaml2==0.11.0',
        'PIL>=1.1.6',
        'django_compressor==1.2',
        'python-memcached==1.48',
        'django-grappelli==2.4.4',
        'django-mathjax==0.0.2',
        'requests==1.2.0',
        'django-deep-serializer==0.1.0',
        'fabric==1.7.0',
        'django-pagination==1.0.7',
        'lxml==2.2.3',
        'BeautifulSoup==3.2.1', #http://www.crummy.com/software/BeautifulSoup/bs3/download/3.x/BeautifulSoup-3.0.8.1.tar.gz
    ],
    entry_points = """
        [moocng.externalapp]
        askbot = moocng.externalapps.apps:Askbot
        nodebb = moocng.externalapps.apps:NodeBB
    """,
)
