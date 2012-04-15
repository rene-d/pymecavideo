# -*- coding: utf-8 -*-

licence={}
licence['en']="""
    pymecavideo version %s:

    a program to track moving points in a video frameset
    
    Copyright (C) 2007-2008 Jean-Baptiste Butet <ashashiwa@gmail.com>
    
    Copyright (C) 2007-2008 Georges Khaznadar <georgesk@ofset.org>

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

licence['fr']=u"""
    pymecavideo version %s :

    un programme pour tracer les trajectoires des points dans une vidéo.
    
    Copyright (C) 2007-2008 Jean-Baptiste Butet <ashashiwa@gmail.com>
    
    Copyright (C) 2007-2008 Georges Khaznadar <georgesk@ofset.org>
    
    Ce projet est un logiciel libre : vous pouvez le redistribuer, le modifier selon les terme de la GPL (GNU Public License) dans les termes de la Free Software Foundation concernant la version 3 ou plus de la dite licence.
    
    Ce programme est fait avec l'espoir qu'il sera utile mais SANS AUCUNE GARANTIE. Lisez la licence pour plus de détails.
    
    <http://www.gnu.org/licenses/>.
"""
#
# Le module de gestion des erreurs n'est chargé que si on execute le fichier .exe ou si on est sous Linux
#
import sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import subprocess,time

from subprocess import Popen, PIPE, STDOUT

class MyReaderThread(QThread):
    """Read stdout"""
    def __init__(self,parent,app,stdout_file):
        QThread.__init__(self,parent)
        self.stdout_file = stdout_file
        self.stdout = []
        self.pct=0
        self.exit=False
        self.parent = parent
        self.app = app

    def run(self):
        

            
            while not self.exit:
                stdout_file = open(self.stdout_file, 'r')       
                self.stdout = stdout_file.readlines()
                try:
                    if self.pct == '99':
                        #print "EXIT"
                        self.exit=True

                    pct__=self.stdout[-1].split('\r')[-2]
                    self.pct = pct__.split()[3].replace('%','').replace(')','').replace('(','')
                    
                    #pct = self.stdout[-1].split()[3].replace('%','').replace(')','').replace('(','')
                    time.sleep(0.1)

                     
                    if self.pct>0 : 
                        self.parent.value_ = int(self.pct)
                        
                        self.app.emit(SIGNAL('updateProgressBar()'))
                        
                    
                except IndexError : 
                    #
                    if self.exit==True: #at the end of encoding
                        pass
                        #print "indexError"
                        
                        
                except TypeError :
                    print "typerreor"
                finally :
                    stdout_file.close()
            self.parent.value_ = 100
            self.app.emit(SIGNAL('updateProgressBar()'))

            self.quit()

class MyEncodeThread(QThread):
    """mon Thread"""
    def __init__(self,parent,app,cmd,dest):
        QThread.__init__(self,parent)
        self.cmd = cmd
        self.dest=dest
        self.app = app
        


    def run(self):
        #ls = Popen(self.cmd.split(), stdout=PIPE, stderr=STDOUT)
        #stdout, stderr = ls.communicate()
        #print stdout, stderr
        stdout_file = open(self.app.stdout_file, 'w+')
        ls = Popen(self.cmd.split(), stdout=stdout_file, stderr=STDOUT)
        ls.communicate()
        self.quit()


class QMessageBoxEncode(QProgressDialog):
    def __init__(self,app,dest):
        """this qmessagebox is shown when video is not opencv comptible. Then it launch a conversion in a thread"""
        QProgressDialog.__init__(self,app)
        self.setLabelText("La vidéo n'est pas compatible avec Pymecavideo.\nPymecavideo l'encode dans un autre format.\n Ceci peut prendre un peu de temps");
        self.setCancelButtonText(QString())
        self.setMaximum(100)
        self.setMinimum(0)
        self.app = app
        self.dest = dest
        self.value_=0
        cmd="mencoder %s -nosound -ovc lavc -o %s " %(self.app.filename,dest)

        myencodethread=MyEncodeThread(self,app,cmd,self.dest)
        myreadthread = MyReaderThread(self,app,self.app.stdout_file)
        myreadthread.start()

        myencodethread.start()

        self.show()
    
    def updateProgressBar(self):

        self.setValue(self.value_)
        if self.value_==100:
            self.app.openTheFile(self.dest)


        

