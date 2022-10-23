#!/usr/bin/python
# -*- coding: utf-8 -*-

##################################################################################################
#
#    Script pour générer un pack avec executable :
#    python setup_win.py build
#
##################################################################################################

from __future__ import print_function
import sys
import os
from glob import glob
from cx_Freeze import setup, Executable
import version

import sys


# Remove the build folder, a bit slower but ensures that build contains the latest
import shutil
shutil.rmtree("build", ignore_errors=True)

# Inculsion des fichiers de donn�es
#################################################################################################
includefiles = ['../AUTHORS', '../COPYING', '../README.fr',
                ('../data', "data"),
                #                     ('mencoder.exe', "mencoder.exe"),
                'C:/Users/jb/AppData/Local/Programs/Python/Python310/Lib/site-packages/cv2/opencv_videoio_ffmpeg460_64.dll']


# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {'build_exe': 'build',
                     "packages": ["os", "cv2", "pyqtgraph"],
                     "includes": [],
                     "optimize": 0,
                     #                     "path" : ["../packages/html5lib"],#, "../packages/xhtml2pdf",  "../packages/xhtml2pdf/w3c"],
                     #                     "zip_includes": [("../packages/html5lib/", "html5lib"),
                     #                                      ("../packages/xhtml2pdf/w3c/css.py", "xhtml2pdf/w3c/css.py")],
                     "excludes": ["tkinter",
                                  '_gtkagg', '_tkagg', 'bsddb', 'curses', 'pywin.debugger',
                                  'pywin.debugger.dbgcon', 'pywin.dialogs', 'tcl',
                                  'Tkconstants', 'pydoc', 'doctest', 'test', 'sqlite3',
                                  "matplotlib",
                                  "PIL", "scipy"

                                  ],
                     "include_files": includefiles,
                     'bin_excludes': ['libgdk-win32-2.0-0.dll', 'libgobject-2.0-0.dll', 'tcl85.dll',
                                      'tk85.dll', "UxTheme.dll", "mswsock.dll", "POWRPROF.dll"

                                      ]}

# GUI applications require a different base on Windows (the default is for a
# console application).
base = None
if sys.platform == "win32":
    base = "Win32GUI"


cible = Executable(
    script="pymecavideo.py",
    base=base,
    icon=os.path.join("", '../data/icones/icone_pymecavideo.ico'),
    initScript=None,
)

print("version", version.Version.__str__())
setup(name="pymecavideo",
      version="7.2.3",
      author='Jean-Baptiste Butet ; Georges Khaznadar',
      description=u"pymecavideo",
      options={"build_exe": build_exe_options},
      #        include-msvcr = True,
      executables=[cible])
