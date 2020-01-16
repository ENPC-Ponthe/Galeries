# -*- coding: utf-8 -*-
"""
    setup
    ~~~~
    Galeries Ponthé est le site du club d'audiovisuel des Ponts
    :copyright: (c) 2018 by Club Ponthé
    :license: MIT, see LICENSE for more details.
"""

from setuptools import setup
from os.path import join, dirname

with open (join(dirname(__file__), 'requirements.txt'), 'r') as f:
    install_requires = f.read().split("\n")

setup(
    name='Galeries Ponthe',
    version='2.0.0.dev0',
    description='Site du Ponthé',
    keywords='ponthé club cinéma audiovisuel',
    url='https://github.com/ENPC-Ponthe/Galeries',
    author=['Philippe Ferreira De Sousa'],
    author_email='philippe@fdesousa.fr',
    license='MIT',
    packages=['ponthe'],
    test_suite='py.test',
    include_package_data=True,
    install_requires=install_requires,
    zip_safe=False
)
