# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
import os

version = '0.0.1'

with open("requirements.txt", "r") as f:
	install_requires = f.readlines()

setup(
    name='helpdesk',
    version=version,
    description='helpdesk',
    author='helpdesk',
    author_email='makarand.b@indictranstech.com',
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=install_requires
)
