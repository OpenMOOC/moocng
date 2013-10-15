import os
from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name="jwt",
    version="0.2.0",
    author="David Halls",
    description=("Module for generating and verifying JSON Web Tokens"),
    license="MIT",
    keywords="jwt json web security signing",
    url="https://github.com/davedoesdev/python-jwt",
    packages=['jwt'],
    long_description=read('README.rst'),
    classifiers=[
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
    ],
)
