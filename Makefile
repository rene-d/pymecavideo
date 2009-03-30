DESTDIR = 
NOT_INSTALLED = essai_label.py extrait_video.py reencode_video.py
HELPFILES = $(shell ls help | grep -E 'xhtml$$|css$$|png$$')

all:	Ui_pymecavideo.py Ui_preferences.py  helpfiles languages

languages:
	lrelease lang/*.ts

helpfiles:
	@$(MAKE) -C help

Ui_%.py: %.ui
	pyuic4 $< > $@

pymecavideo.1: manpage.xml
	xsltproc --nonet /usr/share/sgml/docbook/stylesheet/xsl/nwalsh/manpages/docbook.xsl manpage.xml

clean:
	rm -rf build
	rm -f video_*.jpg *~ Ui_* *.pyc *.txt *.1
	rm -f $(NOT_INSTALLED)
	make -C help clean

install-for-debian: all
	python setup.py install --root=$(DESTDIR) 
	# don't compile now: Debian will make it in the postinst stage.
	install -m 755 pymecavideo $(DESTDIR)/usr/bin
	mkdir -p $(DESTDIR)/usr/share/man/man1
	gzip -c9 pymecavideo.1 > $(DESTDIR)/usr/share/man/man1/pymecavideo.1.gz
	mkdir -p $(DESTDIR)/usr/share/doc/python-mecavideo/html
	for f in $(HELPFILES); do \
	  cp help/$$f $(DESTDIR)/usr/share/doc/python-mecavideo/html; \
	done
	install -m 0644 icones/pymecavideo.xpm icones/pymecavideo-64x64.xpm \
	  $(DESTDIR)/usr/share/pixmaps
	install -m 0644 pymecavideo.desktop $(DESTDIR)/usr/share/applications
	install -m 0644 pymecavideo.svg icones/pymecavideo.png \
	  $(DESTDIR)/usr/share/icons

install-ordinaire: all
	python setup.py install
	install -m 755 pymecavideo $(DESTDIR)/usr/bin
	mkdir -p $(DESTDIR)/usr/share/man/man1
	gzip -c9 pymecavideo.1 > $(DESTDIR)/usr/share/man/man1/pymecavideo.1.gz
	install -m 0644 icones/pymecavideo.xpm icones/pymecavideo-64x64.xpm \
	  $(DESTDIR)/usr/share/pixmaps
	install -m 0644 pymecavideo.desktop $(DESTDIR)/usr/share/applications
	install -m 0644 pymecavideo.svg icones/pymecavideo.png \
	  $(DESTDIR)/usr/share/icons

.PHONY = clean all install-for-debian install-ordinaire helpfiles
