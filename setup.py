#!/usr/bin/env python
import sys
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand
from unnaturalcode import __version__

with open('requirements.txt') as f:
    requires = [l.strip() for l in f.readlines()]

with open('test-requirements.txt') as f:
    tests_require = [l.strip() for l in f.readlines()]
    

# from https://pytest.org/latest/goodpractises.html 2015-9-11
class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        #import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)
# end from

setup(
    name = "unnaturalcode",
    version = __version__,
    packages = find_packages(
        exclude = ["testdata", "js/javascript-sources"]
      ),
    entry_points = {
        "console_scripts": [
            "ucwrap = unnaturalcode.wrap:main",
            "uclearn = unnaturalcode.learn:main",
            "uccheck = unnaturalcode.wrap:check"
        ],
    },
    author = "Joshua Charles Campbell",
    description = "Compiler Error Augmentation System",
    license='AGPL3+',
    include_package_data = True,
    install_requires = requires,
    tests_require=tests_require,
    zip_safe = False,
    cmdclass = {'test': PyTest},
)
