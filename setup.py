# -*- coding: utf-8 -*-

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

try:
    import numpy
except ImportError:
    print 'numpy has to be installed first'
    exit()

try:
    import scipy
except ImportError:
    print 'scipy has to be installed first'
    exit()
    
with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('CHANGELOG.rst') as history_file:
    history = history_file.read()

requirements = [
]

test_requirements = [
    # TODO: put package test requirements here
]

setup(
    name='pyAPP6Tools',
    version='0.2',
    description="Python package with functions to be used with pyAPP and the ALR Aircraft Performance Program APP",
    long_description=readme + '\n\n' + history,
    author="ALR Aerospace",
    author_email='alr@alr-aerospace.ch',
    url='http://aircraftperformance.software',
    packages=[
        'pyAPP6Tools',
    ],
    package_dir={'pyAPP6Tools':
                 'pyAPP6Tools'},
    package_data={},         
    include_package_data=True,
    install_requires=requirements,
    zip_safe=False,
    keywords='pyAPP6Tools',
    test_suite='tests',
    tests_require=test_requirements
)
