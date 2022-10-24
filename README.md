**Description :**

Pymecavideo est un logiciel écrit en PyQT (4 puis 5) pour permettre le
pointage d'une vidéo, le tracé des trajectoires du point pointé et
l'export des positions (temporelles et spatiales) des points choisis.


**Installation :**

Pymecavideo nécessite 4 dépendances :
        PyQT5 : python-qt5  (-devel si vous utilisez les sources)
        OpenCV : python-opencv-headless
        pyqtgraph : python-pyqtgraph
        python-odf (ou odfpy)
        matplotlib
	
avec une installation via pip : 
pip install opencv-python-headless
pip install pyqt5
pip install python-pyqtgraph


**Contribuer :**

Pymecavideo a été en premier lieu écrit en français : le code est
documenté en français, il est internationalisé et des fichiers de
localisation existent en anglais, espagnol et catalan.

Cependant, si vous voulez contribuer et formuler des patch, merci de
mettre vos variables avec des noms français ou francisés :
    exemple : "self.calcul_precis" sera préféré à "self.accurate_compute"

La version git se trouve ici :
https://gitlab.com/oppl/pymecavideo

Toute la gestion des bugs se fait pr gitlab
https://gitlab.com/oppl/pymecavideo/issues

pour l'installer : Voir le fichier INSTALL 

Enjoy :=)

JB BUTET <ashashiwa@gmail.com>

