# Copyright 2012 Rooter Analysis S.L.
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
VERSION = '0.0'


setup(
    name='moocng',
    version=VERSION,
    url='https://github.com/OpenMOOC/moocng',
    license='Apache 2.0 Software License',
    description=('MOOC web tool'),
    long_description=(read('README') + '\n\n' + read('CHANGES')),
    author='Rooter',
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
        'moocng': recursive_include('moocng', ['*.html', '*.css', '*.js', '*.txt',
                                               '*.png', '*.ico', '*.wsgi'])
        },
    zip_safe=False,
    install_requires=[
        'celery==3.0.5',
        'Django>=1.4.1',
        'django-admin-sortable==1.3.3',
        'django-celery==3.0.4',
        'django-gravatar==0.1.0',
        'django-tinymce==1.5.1b2',
        'django-tastypie==0.9.11',
#        'South==0.7.3',
        'psycopg2==2.4.2',
        'pymongo==2.2.1',
        'djangosaml2==0.7.0',
        'PIL>=1.1.7',
        'django_compressor==1.1.2',
        ],
)
