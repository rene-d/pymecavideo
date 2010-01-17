# -*- coding: utf-8 -*-
### setup.py ###

from distutils.core import setup

setup (name='pymecavideo',
      version='4.0',
      description=u"pymecavideo permet de tracer des trajectoires issues de videos et d'en exporter les resultats",
      author='Jean-Baptiste BUTET, Georges KHAZNADAR',
      author_email='ashashiwa@gmail.com, georgesk@ofset.org',
      url='http://outilsphysiques.tuxfamily.org/pmwiki.php/Oppl/Pymecavideo',
      license='GPLv3',
      packages=['pymecavideo'],
      package_dir={'pymecavideo': '.'},
      package_data={'pymecavideo': ['icones/*', 'video/*.avi', 'lang/*.ts', 'lang/*.qm']}#, 'help/*']},
      #data_files=[('share/pymecavideo', ['test.html'])]
)
