#!/usr/bin/env python

import sys, os

# Try using setuptools first, if it's installed
from setuptools import setup, find_packages

# Need to add all dependencies to setup as we go!
setup(name='ledsart',
      packages=find_packages(),
      version='0.1',
      description='Package to control an LED art installation',
      author='Michael J. Harms',
      author_email='harmsm@gmail.com',
      url='https://github.com/harmsm/led-art-installation',
      download_url='https://XX',
      zip_safe=False,
      install_requires=["numpy"],
      classifiers=[])

