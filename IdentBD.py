#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sat Jan  6 13:50:50 2018

@author: ines
"""

import sqlite3

connexion = sqlite3.connect(’/Users/ines/Desktop/sitePonthe/projet_site_ponthe/ponthe’)
connexion.execute(’CREATE TABLE IdentDB(id INT, username STRING, mdp STRING, adresseEnpc STRING)’)
connexion.commit()
connexion.close()
 
