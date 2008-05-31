### setup.py ###
#-*- coding: utf-8 -*-
from distutils.core import setup

setup (name='pymecavideo',
      version='1.9',
      description=u"pymecavideo permet de tracer des trajectoires issues de videos et d'en exporter les resultats",
      author='Jean-Baptiste BUTET',
      author_email='ashashiwa@gmail.com',
      url='http://lucette-serveur.hd.free.fr/trac/pymecavideo',
      license='GPLv3',
      packages=['pymecavideo'],
      package_dir={'pymecavideo': '.'},
      package_data={'pymecavideo': ['icones/*', 'video/*.avi']}#, 'help/*']},
      #data_files=[('share/pymecavideo', ['test.html'])]
)
