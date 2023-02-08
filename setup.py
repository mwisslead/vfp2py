# coding=utf-8
from __future__ import absolute_import, division, print_function

import sys
from setuptools import setup

VERSION='0.1.1'

setup(
    name='vfp2py',
    version=VERSION,
    description='Convert foxpro code to python',
    author='Michael Wisslead',
    author_email='michael.wisslead@gmail.com',
    url='https://github.com/mwisslead/vfp2py',
    packages=['vfp2py'],
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    install_requires=[
        'antlr4-python3-runtime==4.11.1',
        'dbf',
        'autopep8',
        'isort<5',
        'python-dateutil',
        'pyodbc'
    ],
    test_suite='nose.collector',
    tests_require=['nose', 'Faker'],
    entry_points = {
        'console_scripts': ['vfp2py=vfp2py.__main__:main'],
    }
)
