# -*- coding: utf-8 -*-

"""
    dbg.py, a module for pymecavideo:
      a program to track moving points in a video frameset
      
    Copyright (C) 2007 Jean-Baptiste Butet <ashashiwa@gmail.com>
    Copyright (C) 2023 Georges Khaznadar <georgesk@debian.org>


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


class Dbg:
    def __init__(self, verbosite):
        self.verbosite = int(verbosite)

    def p(self, niveau, msg):
        """
        affiche un message si la verbosité est suffisante
        """
        if niveau <= self.verbosite:
            print(msg)

    def __str__(self):
        """
        Renvoie une chaîne lisible pour les humains.
        """
        return f"Le débogage a pour verbosité {self.verbosite}"
