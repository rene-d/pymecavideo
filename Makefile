DESTDIR =
HELPFILES = $(shell ls data/help/help-*.xhtml data/help/*.png)
MAN_LANG = fr
PACKAGE = python3-mecavideo

all: manpage
	for d in src; do DESTDIR=$(DESTDIR) $(MAKE) -C $$d $@ ; done

manpage: pymecavideo.1
	for l in $(MAN_LANG); do $(MAKE) pymecavideo.$$l.1; done

%.1 : %.xml
	xsltproc --nonet /usr/share/sgml/docbook/stylesheet/xsl/nwalsh/manpages/docbook.xsl $<

pymecavideo.1: manpage.xml
	xsltproc --nonet /usr/share/sgml/docbook/stylesheet/xsl/nwalsh/manpages/docbook.xsl manpage.xml

clean:
	rm -rf build
	rm -f video_*.jpg *~ src/Ui_* src/*.pyc *.txt *.1 data/lang/*.qm
	make -C data/help clean

#install-for-debian: all install-bin install-man install-help install-media fix-install
#	cp src/testfilm.py $(DESTDIR)/usr/share/$(PACKAGE)

install-bin:
	install -m 755 pymecavideo $(DESTDIR)/usr/bin

install-man:
	mkdir -p $(DESTDIR)/usr/share/man/man1
	gzip -c9 pymecavideo.1 > $(DESTDIR)/usr/share/man/man1/pymecavideo.1.gz
	for l in $(MAN_LANG); do \
	  mkdir -p $(DESTDIR)/usr/share/man/$$l/man1; \
	  sed "s/pymecavideo.$$l/pymecavideo/" pymecavideo.$$l.1 | gzip -c9 > $(DESTDIR)/usr/share/man/$$l/man1/pymecavideo.1.gz; \
	done

install-help:
	mkdir -p $(DESTDIR)/usr/share/doc/$(PACKAGE)/html
	for f in $(HELPFILES); do \
	  cp $$f $(DESTDIR)/usr/share/doc/$(PACKAGE)/html; \
	done

install-media:
	install -m 0644 data/icones/pymecavideo.xpm data/icones/pymecavideo-48.png \
	  $(DESTDIR)/usr/share/pixmaps
	install -m 0644 pymecavideo.desktop $(DESTDIR)/usr/share/applications
	for i in pymecavideo curseur_cible; do \
	  install -m 0644 data/icones/$$i.svg data/icones/$$i.png \
	  $(DESTDIR)/usr/share/icons; \
	done
	for d in data/icones data/video data/lang; do \
	  cp -a $$d $(DESTDIR)/usr/share/$(PACKAGE) ; \
	done

fix-install:
	find $(DESTDIR)/usr/share/$(PACKAGE) -name COPYING -exec rm {} \;
	find $(DESTDIR)/usr/share/$(PACKAGE) -type f -exec chmod 644 {} \;

.PHONY: clean all install-for-debian install-bin install-man install-help install-media fix-install helpfiles
