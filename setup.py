# Copyright 2012 Rooter. All rights reserved.

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
    license='Undecided',
    description=('MOOC web tool'),
    long_description=(read('README') + '\n\n' + read('CHANGES')),
    author='Rooter',
    classifiers=[
        'Development Status :: 6 - Development',
        'Environment :: Web Environment',
        'Framework :: Django',
        'License :: OSI Approved :: BSD License',
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
        'Django>=1.4.1',
#        'South==0.7.3',
        'psycopg2==2.4.2',
#        'djangosaml2==0.4.2',
        'PIL>=1.1.7'
        ],
)
