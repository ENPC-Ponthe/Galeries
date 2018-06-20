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

#def readme():
#    with open('../README.md') as f:
#        return f.read()

with open(join(dirname(__file__), 'ponthe/version.py'), 'r') as f:
    exec(f.read())

with open (join(dirname(__file__), 'requirements.txt'), 'r') as f:
    install_requires = f.read().split("\n")

setup(
    name='Galeries Ponthe',
    version=__version__,
    description='Site du Ponthé',
#    long_description=readme(),
    keywords='ponthé club cinéma audivisuel',
    #url='http://github.com',
    author=['Ines Tazi', 'Fabien Lespagnol', 'Alexandre Pacaud', 'Arnaud Sadaca', 'Philippe Ferreira De Sousa'],
    author_email='ines.tazi@eleves.enpc.fr',
    license='MIT',
    packages=['ponthe'],
    test_suite='nose2.collector.collector',
    include_package_data=True,
    install_requires=install_requires,
    zip_safe=False
)
