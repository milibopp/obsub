#!/usr/bin/env python

from distutils.core import setup

setup(name='Event',
    version='0.1.0',
    description='Implementation of the observer pattern via a decorator',
    author='Emilia Bopp',
    author_email='Emilia.bopp@aepsil0n.de',
    url='https://github.com/aepsil0n/event',
    py_modules=['event',],
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