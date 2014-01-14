#!/usr/bin/env python

from setuptools import setup

# Read README.rst for PyPI
with open('README.rst') as f:
    long_description = f.read()

# Package setup
setup(
    name='obsub',
    version='0.1.1',
    description='Implementation of the observer pattern via a decorator',
    long_description=long_description,
    author='Eduard Bopp',
    author_email='eduard.bopp@aepsil0n.de',
    url='https://github.com/aepsil0n/obsub',
    py_modules=['obsub',],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: CC0 1.0 Universal (CC0 1.0) Public Domain Dedication',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development',
    ],
    license='Public Domain',
    tests_require='nose',
    test_suite='nose.collector',
)
