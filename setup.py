# -*- coding: utf-8 -*-

"""The setup script."""

import sys
from setuptools import setup, find_packages

requirements = ["pyserial"]

with open("README.md") as f:
    description = f.read()


setup(
    name="vacuubrand",
    author="Tiago Coutinho",
    author_email="tcoutinho@cells.es",
    version="1.0.0",
    description="vacuubrand library",
    long_description=description,
    long_description_content_type="text/markdown",
    entry_points={
        "console_scripts": [
            "Vacuubrand = vacuubrand.tango.server:main [tango]",
        ]
    },
    extras_require={
        "tango": ["pytango"],
        "simulator": ["sinstruments>=1"]
    },
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7"
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
