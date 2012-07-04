#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import righteous

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

if sys.argv[-1] == "publish":
    os.system("python setup.py sdist upload")
    sys.exit()

required = [
    'requests==0.10.8', 'clint==0.3.1', 
    'omnijson==0.1.2', 'docopt==0.4.1',
]

setup(
    name='righteous',
    version=righteous.__version__,
    description='Python RightScale API client.',
    long_description=open('README.md').read() + '\n\n' +
                     open('HISTORY.md').read(),
    author='Michael Joseph',
    author_email='michaeljoseph@gmail.com',
    url='https://github.com/michaeljoseph/righteous',
    packages= [
        'righteous',
    ],
    install_requires=required,
    entry_points = {
        'console_scripts': [
            'righteous = righteous.cli:main',
        ],
    },
    classifiers=(
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: ISC License (ISCL)', # ??
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ),
)

