# -*- coding: utf-8 -*-
### setup.py ###

import src.version

from distutils.core import setup
# import py2exe
setup(name='pymecavideo',
      version="%s" % src.version.Version,
      description=u"pymecavideo permet de tracer des trajectoires issues de videos et d'en exporter les resultats",
      author='Jean-Baptiste BUTET, Georges KHAZNADAR',
      author_email='ashashiwa@gmail.com, georgesk@debian.org',
      url='http://outilsphysiques.tuxfamily.org/pmwiki.php/Oppl/Pymecavideo',
      license='GPLv3',
      packages=['pymecavideo'],
      package_dir={'pymecavideo': 'src'},
      package_data={
      'pymecavideo/data/': ['../data/icones/*', '../data/video/*.avi', '../data/lang/*.ts', '../data/lang/*.qm']}
      #, 'data/help/*']},
      #data_files=[('share/pymecavideo', ['test.html'])]
)

#setup(console=['src/pymecavideo.py'])
