#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import os
from setuptools import setup, find_packages


with open('cryptographic_fields/__init__.py', 'r') as init_file:
    version = re.search(
        '^__version__ = [\'"]([^\'"]+)[\'"]',
        init_file.read(),
        re.MULTILINE,
    ).group(1)

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-cryptographic-fields',
    version=version,
    packages=find_packages(),
    license='MIT',
    include_package_data=True,
    description=(
        'A set of django fields that internally are encrypted using the '
        'cryptography.io native python encryption library.'
    ),
    url='http://github.com/foundertherapy/django-cryptographic-fields/',
    download_url='https://github.com/foundertherapy/django-cryptographic-fields/archive/' + version + '.tar.gz',
    author='Dana Spiegel',
    author_email='nasief304@gmail.com',
    install_requires=[
        'Django>=1.7',
        'cryptography>=0.8.2',
    ],
    keywords=['encryption', 'django', 'fields', ],
)
