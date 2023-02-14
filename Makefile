DESTDIR =
HELPFILES = $(shell ls -d data/help/help-*.html data/help/*.png data/help/*.svg data/help/*.css data/help/static)
PACKAGE = python3-mecavideo
MANPAGES_LANG_SRC = $(shell ls pymecavideo.??.xml)
MANPAGES_LANG  = $(patsubst %.xml, %.1, $(MANPAGES_LANG_SRC))

all:
	for d in src data/help; do \
	  DESTDIR=$(DESTDIR) $(MAKE) -C $$d $@ ;\
	done

manpages: pymecavideo.1  $(MANPAGES_LANG)

pymecavideo.1: manpage.xml
	xsltproc --nonet /usr/share/sgml/docbook/stylesheet/xsl/nwalsh/manpages/docbook.xsl manpage.xml

%.1 : %.xml
	xsltproc --nonet /usr/share/sgml/docbook/stylesheet/xsl/nwalsh/manpages/docbook.xsl $<

clean:
	rm -rf build
	rm -f video_*.jpg src/interfaces/Ui_* src/interfaces/*_rc.py
	rm -f data/lang/*.qm
	find . -name __pycache__ -o -name "*~" | xargs rm -rf

install-for-debian: all install-bin install-man install-help install-media fix-install

install-bin:
	install -m 755 pymecavideo $(DESTDIR)/usr/bin

install-man:
	mkdir -p $(DESTDIR)/usr/share/man/man1
	gzip -c9 pymecavideo.1 > $(DESTDIR)/usr/share/man/man1/pymecavideo.1.gz
	for f in $(MANPAGES_LANG); do \
	  lang=$$(echo $$f | sed 's/.*\.\(.*\)\..*/\1/'); \
	  mkdir -p $(DESTDIR)/usr/share/man/$$lang/man1; \
	  sed "s/pymecavideo.$$lang/pymecavideo/" pymecavideo.$$lang.1 | \
	     gzip -c9 > $(DESTDIR)/usr/share/man/$$lang/man1/pymecavideo.1.gz; \
	done

install-help:
	mkdir -p $(DESTDIR)/usr/share/doc/$(PACKAGE)/html
	for f in $(HELPFILES); do \
	  cp -a $$f $(DESTDIR)/usr/share/doc/$(PACKAGE)/html; \
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

.PHONY: clean all install-for-debian install-bin install-man install-help install-media fix-install helpfiles manpages
