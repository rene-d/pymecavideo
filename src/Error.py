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

    un programme pour tracer les trajectoires des points dans une vid�o.
    
    Copyright (C) 2007-2008 Jean-Baptiste Butet <ashashiwa@gmail.com>
    
    Copyright (C) 2007-2008 Georges Khaznadar <georgesk@ofset.org>
    
    Ce projet est un logiciel libre : vous pouvez le redistribuer, le modifier selon les terme de la GPL (GNU Public License) dans les termes de la Free Software Foundation concernant la version 3 ou plus de la dite licence.
    
    Ce programme est fait avec l'espoir qu'il sera utile mais SANS AUCUNE GARANTIE. Lisez la licence pour plus de d�tails.
    
    <http://www.gnu.org/licenses/>.
"""

import sys
import globdef
import traceback


def _exceptionhook(typ, value, traceb):
    """ On catch une exception """
    frame=traceb.tb_frame
    print >>sys.stderr,"\n"
    traceback.print_tb(traceb)
    print >>sys.stderr,"\nType : ",typ,"\n"
    print >>sys.stderr,"ValueError : ",value
    sys.exit()

sys.excepthook = _exceptionhook

class RedirectErr:
    #
    # Redirige la sortie des erreurs pour envoyer l'erreur par mail
    #
    def __init__(self,stderr):
        self.stderr=stderr
        self.content=""
        self.error_occured=False
        self.file_error=None

    def write(self,text):
        #
        # A la premiere erreur, on enregistrer la fonction de sortie
        #
        if not self.error_occured:
            #
            # Premi�re erreur
            # D'abord on enregistre la fonction atexit
            import atexit
            atexit.register(SendBugReport)
            # puis on ouvre le fichier qui contient les erreurs
            self.file_error=open(globdef.ERROR_FILE,'w')
            print globdef.ERROR_FILE
            self.error_occured=True
        if self.file_error is not None:
            self.file_error.write(text)
            self.file_error.flush()

sys.stderr=RedirectErr(sys.stderr)


def SendBugReport():
    """
    Fonction qui envoie le rapport de bug par mail.
    """
    #
    # On ouvre le fichier qui contient les erreurs
    #
    import webbrowser, datetime
    from PyQt4.QtGui import QMessageBox
    from PyQt4.QtCore import QString
    print "erreur"
    message=_(u"pymecavideo à rencontré une erreur et doit être fermé.\nVoulez-vous envoyer un rapport de bug ?")
    
    dlg = QMessageBox.warning(None,QString(_(unicode("Erreur","utf8"))),
                              QString(message),
                              QMessageBox.Yes|QMessageBox.No)
    
    if dlg == QMessageBox.Yes :#YES, on envoie le mail
        #
        # D�finition du mail
        #
        e_mail="ashashiwa@gmail.com;georgesk@ofset.org;cedrick.faury@freesbee.fr"
        now = str(datetime.datetime.now())
        subject=u"pymecavideo " + globdef.VERSION
        subject+= _(u" : rapport de bug") + now
#        body="<HTML><BODY><P>"
        body =_(u"Le bug suivant s'est produit le ") + now
        body+= "%0A%0A"
#        body+=("""
#        """)
        body+=_(u"Merci de décrire ci-dessous l'opération ayant provoqué le bug :")
        body+="%0A%0A%0A=================TraceBack====================%0A"
        #
        # Parcours du fichier
        #
        file_error=open(globdef.ERROR_FILE,'r')
        for line in file_error.readlines():
            body+=line+"%0A"
        file_error.close()
        body+="%0A==============================================%0A"
        body+=_(u"L'équipe de développement de pymecavideo vous remercie pour votre participation.")
#        body+="</P></BODY></HTML>"
        file_error.close()
        to_send="""mailto:%s?subject=%s&body=%s"""%(e_mail,subject,body)
        #
        # On v�rifie si l'utilisateur travaille avec Outlook
        #
#        try:
#            outlook_app = Dispatch("Outlook.application")
#            msg = outlook.CreateItem(0)
#            msg.To = e_mail
#            msg.Subject = subject
#            msg.Body = body
#            msg.Send()
#        #
#        # Sinon on ouvre son client de messagerie normal
#        #
#        except:
        webbrowser.open("""mailto:%s?subject=%s&body=%s"""%(e_mail,subject,body))


if __name__=='__main__':
    sys.stderr = RedirectErr(sys.stderr)
    print r
    