#!/usr/bin/env python

from setuptools import setup
from distutils.spawn import find_executable

# Convert markdown to reST for PyPI:
pandoc = find_executable('pandoc')
if pandoc:
    from subprocess import check_output
    long_description = check_output(
            [pandoc, 'README.md', '-t', 'rst'],
            universal_newlines=True)
else:
    long_description = None


setup(name='obsub',
    version='0.1.1',
    description='Implementation of the observer pattern via a decorator',
    long_description=long_description,
    author='Emilia Bopp',
    author_email='Emilia.bopp@aepsil0n.de',
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
    )
