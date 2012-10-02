#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import righteous

try:
    from setuptools import setup
    hush_pyflakes = setup
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
    long_description=(
        '**righteous** is a Python client implementation of the '
        '`RightScale API <http://support.rightscale.com/rdoc>`_ '
        'for EC2 instance management.'
        'Source Code: `https://github.com/michaeljoseph/righteous '
        '<https://github.com/michaeljoseph/righteous>`_'
        'RTFD: `http://righteous.readthedocs.org '
        '<http://righteous.readthedocs.org>`_'
    ),
    author=righteous.__author__,
    author_email='michaeljoseph@gmail.com',
    url='https://github.com/michaeljoseph/righteous',
    packages=[
        'righteous',
    ],
    install_requires=required,
    entry_points={
        'console_scripts': [
            'righteous = righteous.cli:main',
        ],
    },
    classifiers=(
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ),
)
