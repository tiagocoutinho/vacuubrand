# -*- coding: utf-8 -*-

"""The setup script."""

import sys
from setuptools import setup, find_packages

requirements = ['pyserial', 'PyTango']


setup(
    name='vacuubrand',
    author="Tiago Coutinho",
    author_email='tcoutinho@cells.es',
    version='1.0.0',
    description="vacuubrand library",
    long_description="Vacuubrand library (DCP 3000)",
    entry_points={
        'console_scripts': [
            'PyDsVacuuBrand = vacuubrand.tango.server:main',
        ]
    },
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7'
    ],
    install_requires=requirements,
    license="LGPLv3",
    include_package_data=True,
    keywords='vacuubrand, library, tango',
    packages=find_packages(),
    url='https://github.com/ALBA-Synchrotron/vacuubrand')
