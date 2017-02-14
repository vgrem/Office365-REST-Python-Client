#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from distutils.core import setup
import setuptools

def read(fname):
    """From an_example_pypi_project (https://pypi.python.org/pypi/an_example_pypi_project). """
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name="Office365-REST-Python-Client",
    version="1.0.0",
    author="Vadim Gremyachev",
    author_email="vvgrem@gmail.com",
    maintainer="Konrad Gądek",
    maintainer_email="kgadek@gmail.com",
    description="Office 365 REST client for Python",
    long_description=read("README.md"),
    url="https://github.com/vgrem/Office365-REST-Python-Client",
    install_requires=['requests'],
    license="MIT",
    keywords="git",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries"
    ],
    packages=setuptools.find_packages()
)

