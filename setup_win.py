#!/usr/bin/python
# -*- coding: utf-8 -*-

##################################################################################################
#
#    Script pour générer un pack avec executable :
#    c:\python27\python setup_win.py build
#
##################################################################################################

from __future__ import print_function
import sys, os
from glob import glob
from cx_Freeze import setup, Executable
import version

python_dir = os.path.dirname(sys.executable)
    
## Remove the build folder, a bit slower but ensures that build contains the latest
import shutil
shutil.rmtree("build", ignore_errors=True)

# Inculsion des fichiers de données
#################################################################################################
includefiles = ['../AUTHORS', '../COPYING', '../README.fr', 
                os.path.join(python_dir, "python3.dll"), 
                os.path.join(python_dir, "vcruntime140.dll"),
                ('../data', "data")]



# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {'build_exe': 'build',
                     'include_msvcr': True,
                     'add_to_path': True,
                     "packages": ["os", "cv2"], 
                     "includes": ["PyQt5"],
                     "optimize" : 1,
                     "excludes": ["tkinter",
                                  '_gtkagg', '_tkagg', 'bsddb', 'curses', 'pywin.debugger',
                                  'pywin.debugger.dbgcon', 'pywin.dialogs', 'tcl',
                                  'Tkconstants', 'pydoc', 'doctest', 'test', 'sqlite3',
                                  "matplotlib", 
                                  "PIL", "scipy", "email"
                                  ],
                     "include_files": includefiles

                                      }

# GUI applications require a different base on Windows (the default is for a
# console application).
base = None
if sys.platform == "win32":
    base = "Win32GUI"


if __name__ == '__main__':
    cible = Executable(
        script = "pymecavideo.py",
        base = base,
        icon = os.path.join("", '../data/icones/icone_pymecavideo.ico'),
        initScript = None
        )
    
    print ("version", version.Version.__str__())
    setup(  name = "pymecavideo",
            version = "6.5.0.0",
            author = 'Jean-Baptiste Butet ; Georges Khaznadar',
            description = "pymecavideo",
            long_description = "",
            options = {"build_exe": build_exe_options},
    #        include-msvcr = True,
            executables = [cible])
