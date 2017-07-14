import sys
from setuptools import setup

VERSION='0.1.0'

ANTLR4 = 'antlr4-python{}-runtime'.format(sys.version_info.major)

setup(
    name='vfp2py',
    version=VERSION,
    description='Convert foxpro code to python',
    author='Michael Wisslead',
    author_email='michael.wisslead@gmail.com',
    url='https://github.com/mwisslead',
    packages=['vfp2py'],
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    install_requires=[ANTLR4, 'future', 'enum34', 'dbf', 'autopep8==1.2.4', 'isort'],
    test_suite='nose.collector',
    tests_require=['nose', 'Faker'],
)
