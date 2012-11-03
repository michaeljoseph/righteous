#!/usr/bin/env python
# -*- coding: utf-8 -*-

__version__ = '0.4.0'
__author__ = 'Michael Joseph'

import os
import sys

try:
    from setuptools import setup
    hush_pyflakes = setup
except ImportError:
    from distutils.core import setup

from setuptools.command.test import test as TestCommand


class Coverage(TestCommand):
    """
    A command to run tests with coverage and generate an html report
    """
    description = "generates a coverage report"

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import coverage
        unittest = None
        if PY3:
            import unittest
            unittest = unittest
        else:
            import unittest2 as unittest
            unittest = unittest

        cov = coverage.coverage(branch=True, source=["righteous"])
        cov.erase()
        cov.start()

        loader = unittest.TestLoader()
        tests = loader.discover('tests')
        test_runner = unittest.runner.TextTestRunner()
        test_runner.run(tests)

        cov.stop()
        cov.html_report(directory='htmlcov')

if sys.argv[-1] == "publish":
    os.system("python setup.py sdist upload")
    sys.exit()

PY3 = sys.version_info[0] == 3
required = ['requests==0.14.1', 'clint==0.3.1', 'docopt==0.4.1', 'six==1.2.0']
test_suite = 'tests.unit'
tests_require = ['mock==0.8.0', 'coverage==3.5.3']
if not PY3:
    tests_require.append('unittest2==0.5.1')
    test_suite = 'unittest2.collector'


setup(
    name='righteous',
    version=__version__,
    description='Python RightScale API client.',
    long_description=(
        '**righteous** is a Python client implementation of the '
        '`RightScale API <http://support.rightscale.com/rdoc>`_ '
        'for EC2 instance management.\n\n'
        'Source Code: `https://github.com/michaeljoseph/righteous '
        '<https://github.com/michaeljoseph/righteous>`_\n\n'
        'RTFD: `http://righteous.readthedocs.org '
        '<http://righteous.readthedocs.org>`_'
    ),
    author=__author__,
    author_email='michaeljoseph@gmail.com',
    url='https://github.com/michaeljoseph/righteous',
    packages=[
        'righteous',
        'righteous.api',
    ],
    install_requires=required,
    entry_points={
        'console_scripts': [
            'righteous = righteous.cli:main',
        ],
    },
    tests_require=tests_require,
    test_suite=test_suite,
    classifiers=(
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: Implementation :: PyPy',
    ),
    cmdclass={'test': Coverage},
)
