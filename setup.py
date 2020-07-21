#!/usr/bin/env python
import io
from distutils.core import setup
import setuptools

with open("README.md", mode='r', encoding='utf-8') as fh:
    long_description = fh.read()

setup(
    name="Office365-REST-Python-Client",
    version="2.1.10",
    author="Vadim Gremyachev",
    author_email="vvgrem@gmail.com",
    maintainer="Konrad Gądek",
    maintainer_email="kgadek@gmail.com",
    description="Office 365 Library for Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/vgrem/Office365-REST-Python-Client",
    python_requires='>=3.7',
    install_requires=['requests', 'adal'],
    extras_require={
        'NTLMAuthentication': ["requests_ntlm"]
    },
    tests_require=['nose', 'flake8', 'isort'],
    test_suite='nose.collector',
    license="MIT",
    keywords="git",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries",
        'Programming Language :: Python',
        "Programming Language :: Python :: 3 :: Only",
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    packages=setuptools.find_packages(),
    package_data={
        'office365': ["runtime/auth/providers/templates/SAML.xml", "runtime/auth/providers/templates/RST2.xml", "runtime/auth/providers/templates/FederatedSAML.xml"]
    }
)
