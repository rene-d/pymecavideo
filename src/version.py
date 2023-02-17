# -*- coding: utf-8 -*-

"""
    version, a module for pymecavideo:
      a program to track moving points in a video frameset
      This module is just an utility to manage the version number which
      is important for releases of pymecavideo
      
    Copyright (C) 2008-2018 Georges Khaznadar

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import os.path
import gzip
import re


class version:
    def __init__(self, majeur, mineur, nuance=""):
        self.majeur = majeur
        self.mineur = mineur
        self.nuance = nuance

    def __lt__(self, other):
        return (self.majeur < other.majeur) or \
            (self.majeur == other.majeur and self.mineur < other.mineur)

    def __str__(self):
        return "%s.%s%s" % (self.majeur, self.mineur, self.nuance)

    def __repr__(self):
        return self.__str__()

def str2version(chaine):
    """
    extrait la version d'une chaîne de caractères
    """
    m = re.match(r"(\d+)\.(\d+)(.*)", chaine)
    if m:
        return version(int(m.group(1)), int(m.group(2)), m.group(3))
    return version(0, 0)

def versionFromDebianChangelog():
    """
    Renvoie une version selon le contenu éventuel d'un fichier
    /usr/share/doc/python3-mecavideo/changelog.Debian.gz
    """
    packageName = "python3-mecavideo"
    changelog = os.path.join("/usr/share/doc", packageName, "changelog.Debian.gz")
    if os.path.exists(changelog):
        with gzip.open(changelog) as chlog:
            firstline = chlog.readline().strip().decode("utf-8")
            m = re.match(r"^pymecavideo \((.*)\).*$", firstline)
            if m:
                return str2version(m.group(1))
    return None
    

###############################################################
# la version courante, à incrémenter lors de changements
###############################################################
Version = version(8, 1, '~rc3-1')

###############################################################
# incrémentation automatique pour une distribution debian
###############################################################
v = versionFromDebianChangelog()
if v: Version = v

if __name__ == "__main__":
    print(Version)
