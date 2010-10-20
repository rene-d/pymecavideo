#!/usr/bin/python
# -*- coding: iso-8859-1 -*-

from distutils.core import setup
import py2exe
import os
import PyQt4

# Remove the build folder, a bit slower but ensures that build contains the latest
import shutil
shutil.rmtree("build", ignore_errors=True)

from glob import glob
data_files = [("Microsoft.VC90.CRT", glob(r'msvcr90.dll')), 
              ("Microsoft.VC90.CRT", glob(r'Microsoft.VC90.CRT.manifest')),
#              ("", glob(r'ff*.exe')),
              
              ('imageformats', [os.path.join(os.path.dirname(PyQt4.__file__), 
                                              'plugins', 
                                              'imageformats', 
                                              'qjpeg4.dll')])
              ]


options = {    "py2exe" : { "compressed": 2,
                           
                            "optimize": 2,
                            
                            "bundle_files": 3,
                            
                            'packages' : ['win32api'], #'pytz',
                            
                            "includes": ["sip"],#, "PyQt4.QtCore", "PyQt4.QtGui"],
                            
                            'excludes' : ['_gtkagg', '_tkagg', 'bsddb', 'curses', 'pywin.debugger',
                                          'pywin.debugger.dbgcon', 'pywin.dialogs', 'tcl',
                                          'Tkconstants', 'Tkinter', 'pydoc', 'doctest', 'test', 'sqlite3'
                                          ],
                            
                            'dll_excludes' : ['libgdk-win32-2.0-0.dll', 'libgobject-2.0-0.dll', 'tcl85.dll',
                                              'tk85.dll', "UxTheme.dll", "mswsock.dll", "POWRPROF.dll" , 
                                              "AVIFIL32.dll", 'AVICAP32.dll', 'MSACM32.dll', 'OLEPRO32.DLL'],

                                   }     }

icon = "D:\\Documents\\Developpement\\pymecavideo\\data\\icones\\pymecavideo.ico"
setup(name='pyMecaVideo',
      version='5.2',
      description='Analyse Mécanique des videos',
      author='Jean-Baptiste Butet ; Georges Khaznadar',
      author_email='ashashiwa@gmail.com ; georgesk@ofset.org',
      url='http://outilsphysiques.tuxfamily.org/pmwiki.php/Oppl/Pymecavideo',

      options = options,
      #zipfile = None,

      data_files = data_files,
#      console=[{"script" :"pymecavideo.py",
#                "icon_resources":[(1, icon)],
#                #"other_resources": [(24,1,manifest)]
#                }]
      windows=[{"script" :"pymecavideo.py",
                "icon_resources":[(1, icon)],
                #"other_resources": [(24,1,manifest)]
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