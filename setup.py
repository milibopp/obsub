#!/usr/bin/env python

import logging
from setuptools import setup


# Create a front page for PyPI:
long_description = None
try:
    long_description = open('README.rst').read()
    long_description += '\n' + open('CHANGELOG.rst').read()
except IOError:
    # some file is not available
    # just use what we got so far but issue a warning
    logging.warn('documentation files missing')


setup(
    name='obsub',
    version='0.2.1',
    description='Implementation of the observer pattern via a decorator',
    long_description=long_description,
    long_description_content_type='text/x-rst',
    author='Emilia Bopp',
    author_email='contact@ebopp.de',
    url='https://github.com/milibopp/obsub',
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
