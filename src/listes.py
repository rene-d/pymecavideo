# -*- coding: utf-8 -*-

"""
    listes, a module for pymecavideo:
      a program to track moving points in a video frameset
      this module is about defining a few list classes.
      
    Copyright (C) 2007 Jean-Baptiste Butet <ashashiwa@gmail.com>

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


class listePointee:
    """Une liste de données avec un pointeur, qui permet de revenir en arrière
    et en avant dans la liste.
    """

    def __init__(self):
        """Crée la liste, initialement vide.
        """
        self.data = []
        self.ptr = -1

    def count(self):
        """
        @return le nombre d'éléments existants, indépendamment de la
        position du pointeur
        """
        return len(self.data)

    def append(self, val):
        """Ajoute un élément. Si le pointeur n'était pas à la fin, détruit
        les enregistrements qui suivent.
        """
        if self.ptr < len(self.data) - 1:
            for i in range(len(self.data) - 1, self.ptr, -1):
                del self.data[i]
        self.data.append(val)
        self.ptr = len(self.data) - 1

    def incPtr(self):
        if self.ptr < len(self.data) - 1:
            self.ptr += 1
        return

    def decPtr(self):
        if self.ptr > -1:
            self.ptr -= 1
        return

    def __bool__(self):
        return len(self.data) > 0 and self.ptr >= 0

    def __iter__(self):
        return listePointeeIterateur(self)

    def __getitem__(self, i):
        if i >= 0 and i <= self.ptr:
            return self.data[i]
        elif i < 0 and 1+self.ptr+i >= 0:
            return self.data[1+self.ptr+i]
        else:
            raise IndexError

    def __len__(self):
        return self.ptr + 1

    def nextCount(self):
        """
        renvoie le nombre de données après le pointeur
        """
        return len(self.data) - self.ptr - 1

    def __str__(self):
        s = "liste pointee : ["
        for i in range(len(self.data)):
            if i == self.ptr:
                s += "@"
            s += "%s" % self.data[i]
            if i == self.ptr:
                s += "@"
            if i < len(self.data) - 1:
                s += ", "
        s += "]"
        return s

    def __repr__(self):
        return self.__str__()


class listePointeeIterateur:
    """Un itérateur pour le type précédent.
    """

    def __init__(self, lp):
        self.i = 0
        self.lp = lp

    def __iter__(self):
        self.i = 0
        return self

    def __next__(self):
        i = self.i
        self.i += 1
        if i > self.lp.ptr:
            raise StopIteration
        return self.lp.data[i]


def test():
    print ("quelques tests de liste pointée")
    l1 = listePointee()
    l1.append(1)
    l1.append(['a', 'b'])
    l1.append(2)
    l1.append(3)
    l1.decPtr()
    print ("""
    l1=listePointee()
    l1.append(1)
    l1.append(['a','b'])
    l1.append(2)
    l1.append(3)
    l1.decPtr()
""")
    print (">>> l1 = %s" % l1)
    print (">>> l1[0] = %s" % l1[0])

    print ("""
    for e in l1:
        print e
""")
    for e in l1:
        print (e)

    print ("\n>>> len(l1) = %s" % len(l1))

    l1.incPtr()

    print ("""
        l1.incPtr()
""")
    for e in l1:
        print (e)

    print ("\n>>> len(l1) = %s" % len(l1))

    l1.decPtr()
    l1.decPtr()
    l1.append('x')

    print ("""
    l1.decPtr()
    l1.decPtr()
    l1.append('x')
""")
    for e in l1:
        print (e)

    print ("\n>>> len(l1) = %s" % len(l1))

    print ("test de l'iterateur")
    i = iter(l1)
    while True:
        try:
            print(next(i))
        except StopIteration:
            break
    print("itération à l'envers")
    for i in range(-1, -1-len(l1), -1):
        print ("index:", i, "=>", l1[i])

    
if __name__ == "__main__":
    test()
