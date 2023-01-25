#!/usr/bin/python
# -*- coding: iso-8859-1 -*-

from glob import glob
from distutils.core import setup
import os

import PyQt6
#import matplotlib

import py2exe


# Remove the build folder, a bit slower but ensures that build contains the latest
import shutil

shutil.rmtree("build", ignore_errors=True)
shutil.rmtree("dist", ignore_errors=True)


data_files = [("Microsoft.VC90.CRT", glob(r'msvcr90.dll')),
              ("Microsoft.VC90.CRT", glob(r'Microsoft.VC90.CRT.manifest')),
              # ('C:\\Python26\\Lib\\site-packages\\opencv_ffmpeg243.dll'),

              # Il faut peut-être décommenter cette ligne pour certaines versions de pyOpenCV
              # Inutile pour la version 2.4.3 !
              #              ('C:\\OpenCV2.3\\build\\bin\\opencv_ffmpeg.dll'),
              #              ("", glob(r'ff*.exe')),

              ('imageformats', [os.path.join(os.path.dirname(PyQt6.__file__),
                                             'plugins',
                                             'imageformats',
                                             'qjpeg4.dll')])
              ]
data_files += matplotlib.get_py2exe_datafiles()

options = {"py2exe": {"compressed": 2,

                      "optimize": 2,

                      "bundle_files": 3,

                      'packages': ['win32api'],  # 'pytz',

                      "includes": ["sip",  # "matplotlib.backends",
                                   #"matplotlib.backends.backend_qt4agg"
                                   ],  # , "PyQt6.QtCore", "PyQt4.QtGui"],

                      'excludes': ['bsddb', 'curses', 'pywin.debugger',
                                   'pywin.debugger.dbgcon', 'pywin.dialogs',
                                   'pydoc', 'doctest', 'test', 'sqlite3',
                                   'Tkinter', 'Tkconstants', 'tcl',
                                   "matplotlib.backends.backend_wxagg",
                                   "matplotlib.backends.backend_wx",
                                   '_gtkagg', '_tkagg',
                                   '_wxagg', '_wx',  # '_gtkagg', #,
                                   '_agg2', '_cairo',
                                   '_cocoaagg', '_fltkagg', '_gtk', '_gtkcairo'
                                                                    'numpy', 'pylab', "wx"],

                      'dll_excludes': ['libgdk-win32-2.0-0.dll', 'libgobject-2.0-0.dll',
                                       "UxTheme.dll", "mswsock.dll", "POWRPROF.dll",
                                       "AVIFIL32.dll", 'AVICAP32.dll', 'MSACM32.dll', 'OLEPRO32.DLL',
                                       'tk85.dll', 'tcl85.dll', "wx*.*"
                                       ],

                      }}

# Adapter le chemin au PC !
icon = "D:\\Developpement\\pymecavideo_6.1\\data\\icones\\pymecavideo.ico"

setup(name='pyMecaVideo',
      version='6.1',
      description='Analyse Mécanique des videos',
      author='Jean-Baptiste Butet ; Georges Khaznadar',
      author_email='ashashiwa@gmail.com ; georgesk@debian.org',
      url='http://outilsphysiques.tuxfamily.org/pmwiki.php/Oppl/Pymecavideo',

      options=options,
      # zipfile = None,

      data_files=data_files,
      #      console=[{"script" :"pymecavideo.py",
      #                "icon_resources":[(1, icon)],
      #                #"other_resources": [(24,1,manifest)]
      #                }]
      windows=[{"script": "pymecavideo.py",
                "icon_resources": [(1, icon)],
                # "other_resources": [(24,1,manifest)]
                }]
      )

manifest = """
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<!-- Copyright (c) Microsoft Corporation.  All rights reserved. -->
<assembly xmlns="urn:schemas-microsoft-com:asm.v1" manifestVersion="1.0">
    <noInheritable/>
    <assemblyIdentity
        type="win32"
        name="Microsoft.VC90.CRT"
        version="9.0.21022.8"
        processorArchitecture="x86"
        publicKeyToken="1fc8b3b9a1e18e3b"
    />
    <file name="msvcr90.dll" /> <file name="msvcp90.dll" /> <file name="msvcm90.dll" />
</assembly>
"""
