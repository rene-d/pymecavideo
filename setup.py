# -*- coding: utf-8 -*-
### setup.py ###

import src.version
from glob import glob
from itertools import chain
from platform import platform
import os, sys

from distutils.core import setup
# import py2exe
setup(
    name='pymecavideo',
    version="%s" % src.version.Version,
    description=u"pymecavideo permet de tracer des trajectoires issues de videos et d'en exporter les resultats",
    author='Jean-Baptiste BUTET, Georges KHAZNADAR',
    author_email='ashashiwa@gmail.com, georgesk@debian.org',
    url='http://outilsphysiques.tuxfamily.org/wiki/index.php?title=Pymecavideo',
    license='GPLv3',
    packages=['pymecavideo', 'pymecavideo.interfaces'],
    package_dir={
        'pymecavideo': 'src',
        'pymecavideo.interfaces' : 'src/interfaces',
    },
    data_files=[
        ('share/pymecavideo/data/help',
         chain(*[glob(f"data/help/*.{e}") for e in ("png", "svg", "html", "css")])
         ),
        ('share/pymecavideo/data/lang',
         chain(*[glob(f"data/lang/*.{e}") for e in ("ts", "qm")])
         ),
        ('share/pymecavideo/data/icones',
         glob("data/icones/*")
         ),
        ('share/pymecavideo/data/video',
         glob("data/video/*")
         ),
    ]
)
