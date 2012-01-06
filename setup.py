#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

if sys.argv[-1] == "publish":
    os.system("python setup.py sdist upload")
    sys.exit()

if sys.argv[-1] == "test":
    os.system("python test_righteous.py")
    sys.exit()

required = [
    'requests', 'clint',
]

if sys.version_info[:2] < (2,6):
    required.append('simplejson')

setup(
    name='righteous',
    version='0.0.1',
    description='Python RightScale API client.',
    long_description=open('README.rst').read(),
    author='Michael Joseph',
    author_email='michaeljoseph@gmail.com',
    url='https://github.com/michaeljoseph/righteous',
    packages= [
        'righteous',
    ],
    install_requires=required,
    classifiers=(
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: ISC License (ISCL)', # ??
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
    ),
)

