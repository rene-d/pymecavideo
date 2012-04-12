# -*- coding: utf-8 -*-

"""
    version, a module for pymecavideo:
      a program to track moving points in a video frameset
      This module is just an utility to manage the version number which
      is important for releases of pymecavideo
      
    Copyright (C) 2008 Georges Khaznadar

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


class version:
    def __init__(self, majeur, mineur, nuance=""):
        self.majeur=majeur
        self.mineur=mineur
        self.nuance=nuance
    def __str__(self):
        return "%s.%s%s" %(self.majeur,self.mineur, self.nuance)
    def __repr__(self):
        return self.__str__()


###############################################################
# la version courante, à incrémenter lors de changements
###############################################################
Version=version(5,4)
###############################################################


if __name__=="__main__":
    print Version
    
