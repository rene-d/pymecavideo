#! /usr/bin/python
from __future__ import print_function

from film import film
import os

if __name__ == '__main__':
    list_film = os.listdir(".")
    for i in list_film:
        f = film(i)
        print (i, "le film est [%s] : fps, frames = %s, %s" % (bool(f), f.fps, f.framecount))
