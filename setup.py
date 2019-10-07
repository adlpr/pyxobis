#!/usr/bin/python3
# -*- coding: UTF-8 -*-

version = '0.1'

import os
from setuptools import setup

with open(os.path.join(os.path.dirname(__file__), 'README.md'),'r') as inf:
    long_description = inf.read()

setup(
    name = 'pyxobis',
    version = version,
    # url = '',
    author = 'Alex DelPriore',
    author_email = 'delpriore@stanford.edu',
    license = 'Copyright © 2019 The Board of Trustees of The Leland Stanford Junior University, All Rights Reserved',
    packages = ['pyxobis'],
    python_requires='>=3.7',
    install_requires = ['git+git://github.com/adlpr/pymarc.git@master#egg=pymarc',
                        'lxml==4.3.3',
                        'regex==2019.4.14',
                        'tqdm==4.32.1',
                        'loguru==0.3.2'],
    description = 'Packages for transformation of Stanford Lane MARC data to XOBIS-XML',
    long_description = long_description,
    long_description_content_type = "text/markdown",
    # classifiers = ...,
)
