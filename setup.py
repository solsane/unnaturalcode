#!/usr/bin/env python
import sys
import os
from os.path import isfile
import subprocess
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand
from distutils.core import Extension, Command
from distutils.command.build_ext import build_ext
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

class BuildConfigure(Command):
    def initialize_options(self):
        pass
      
    def finalize_options(self):
        pass

    def run(self):
        os.chdir("pymitlm/mitlm")
        if not isfile('configure'):
            subprocess.call([
              "./autogen.sh",
              "--disable-maintainer-mode",
              '--with-pic'
              ])
        if not isfile('Makefile'):
            subprocess.call([
              "./configure",
              "--disable-maintainer-mode",
              '--with-pic'
              ])
        subprocess.call(["make"])
        os.chdir("../..")

class BuildExtension(build_ext):
    def run(self):
        for cmd_name in self.get_sub_commands():
            self.run_command(cmd_name)

        build_ext.run(self)
    sub_commands = [("build_configure", None)] + build_ext.sub_commands

setup(
    name = "unnaturalcode",
    version = __version__,
    packages = ['unnaturalcode', 'pymitlm'],
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
    cmdclass = {'test': PyTest,
                "build_configure": BuildConfigure,
                "build_ext": BuildExtension},
    ext_modules=[Extension('pymitlm._pymitlm',
                           [
                             'pymitlm/pymitlm.i',
                           ],
                           extra_objects=[
                             'pymitlm/mitlm/.libs/libmitlm.a',
                           ],
                           include_dirs=['pymitlm/mitlm/src'],
                           #library_dirs=['pymitlm/mitlm/.libs'],
                           #runtime_library_dirs=['pymitlm/mitlm/.libs'],
                           libraries=['gfortran'],
                           swig_opts=['-c++'],
                           extra_compile_args=['-std=gnu++11', '-fPIC']
                          )],
    py_modules=['pymitlm.pymitlm'],
)
