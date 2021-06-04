# -*- coding: utf-8 -*-

"""The setup script."""

import sys
from setuptools import setup, find_packages

requirements = ["connio"]

with open("README.md") as f:
    description = f.read()


setup(
    name="vacuubrand",
    author="Tiago Coutinho",
    author_email="tcoutinho@cells.es",
    version="2.1.3",
    description="vacuubrand library",
    long_description=description,
    long_description_content_type="text/markdown",
    entry_points={
        "console_scripts": [
            "Vacuubrand = vacuubrand.tango.server:main [tango]",
        ],
        'sinstruments.device': [
            'DCP3000 = vacuubrand.simulator:DCP3000 [simulator]'
        ]
    },
    extras_require={
        "tango": ["pytango>=9"],
        "simulator": ["sinstruments>=1.3"]
    },
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8"
    ],
    install_requires=requirements,
    license="LGPLv3",
    include_package_data=True,
    keywords="vacuubrand, library, tango",
    packages=find_packages(),
    url="https://github.com/tiagocoutinho/vacuubrand",
    project_urls={
        "Documentation": "https://github.com/tiagocoutinho/vacuubrand",
        "Source": "https://github.com/tiagocoutinho/vacuubrand"
    }
)
