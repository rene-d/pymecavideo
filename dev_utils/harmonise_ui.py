#! /usr/bin/python3
# -*- coding: utf-8 -*-
"""
    harmonise_ui.py : a tool to help the development of pymecavideo
    
    pymecavideo is a program to track moving points in a video frameset
      
    Copyright (C) 2022 Georges Khaznadar <georgesk@debian.org>

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

"""
The goal of this tool is to ensure that every tooltip and every statustip
found in file f1 is copied when possible in the right place into file f2
"""

import sys, os
from xml.dom import minidom

def tooltips_dict(dom):
    """
    creates a dictionary {elt_name => tip} from dom
    @param dom a document object model
    @return a dictionary
    """
    tooltips = [ t for t in dom.getElementsByTagName("property")
                 if t.hasAttribute("name") and \
                 t.getAttribute("name")=="toolTip"]
    return {t.parentNode.getAttribute("name") : t for t in tooltips}

def statustips_dict(dom):
    """
    creates a dictionary {elt_name => tip} from dom
    @param dom a document object model
    @return a dictionary
    """
    statustips = [ t for t in dom.getElementsByTagName("property")
                 if t.hasAttribute("name") and \
                 t.getAttribute("name")=="statusTip"]
    return {t.parentNode.getAttribute("name") : t for t in statustips}

def apply_tips(t_dict, s_dict, dom):
    """
    Injecte des tooltips et des status tips dans un dom
    Pour chaque entrée dans un des dictionnaires, si un élément de même
    nom existe, on essaie d'y injecter les tips qui vont bien.

     - Un avertissement est émis en l'absence d'élément de ce nom dans la cible
     - un avertissement est émis si dans l'élément de même nom il y a déjà
       un tip avec une valeur différente

    à la fin, tous les tips possibles sont injectés dans dom

    !!! À faire : émettre les avertissement ; pour le moment il n'y en a pas !!!

    @param t_dic le dictionnaire des tooltips
    @param s_dict le dictionnaire des statustips
    @return une référence au dom
    """
    #recursive traversal of the dom
    def recursive_update(node):
        # ELEMENT_NODE is 1
        if node.nodeType != 1 :
            return
        if node.getAttribute("name") in t_dict.keys():
            node.appendChild(t_dict[node.getAttribute("name")])
        if node.getAttribute("name") in s_dict.keys():
            node.appendChild(s_dict[node.getAttribute("name")])
        for n in node.childNodes:
            recursive_update(n)
        return
    recursive_update(dom.documentElement)
    return dom
    
if __name__ == "__main__":
    f1 = sys.argv[1]
    assert (os.path.exists(f1))
    f2 = sys.argv[2]
    assert (os.path.exists(f2))
    dom1 = minidom.parse(open(f1))
    
    dom2 = minidom.parse(open(f2))
    t_dict = tooltips_dict(dom1)
    s_dict = statustips_dict(dom1)
    dom3 = apply_tips(t_dict, s_dict, dom2)
    print(dom3.toxml())
