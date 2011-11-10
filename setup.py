# -*- coding: utf-8 -*-
# Copyright (c) 2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from setuptools import setup, find_packages
import os

version = '3.0dev'

setup(name='Products.SilvaMetadata',
      version=version,
      description="Metadata support for Silva",
      long_description=open(os.path.join("Products", "SilvaMetadata", "README.txt")).read() + "\n" +
                       open(os.path.join("Products", "SilvaMetadata", "HISTORY.txt")).read(),
      classifiers=[
              "Framework :: Zope2",
              "License :: OSI Approved :: BSD License",
              "Programming Language :: Python",
              "Topic :: Software Development :: Libraries :: Python Modules",
              ],
      keywords='silva zope2 metadata',
      author='Infrae',
      author_email='info@infrae.com',
      url='http://infrae.com/products/silva',
      license='BSD',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'Products.Formulator',
        'five.grok',
        'setuptools',
        'silva.core.conf',
        'silva.core.interfaces',
        'silva.core.services',
        'silva.core.views',
        'zope.interface',
        'zope.annotation',
        'zope.component',
        ],
      )

