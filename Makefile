DESTDIR =
HELPFILES = $(shell ls data/help/help-*.xhtml data/help/*.png)
MAN_LANG = fr

all: manpage
	for d in help lang src; do DESTDIR=$(DESTDIR) $(MAKE) -C $$d $@ ; done

manpage: pymecavideo.1 cadreur.1
	for l in $(MAN_LANG); do \
	  for p in pymecavideo cadreur; do \
	    $(MAKE) $$p.$$l.1; \
	  done; \
	done

%.1 : %.xml
	xsltproc --nonet /usr/share/sgml/docbook/stylesheet/xsl/nwalsh/manpages/docbook.xsl $<

pymecavideo.1: manpage.xml
	xsltproc --nonet /usr/share/sgml/docbook/stylesheet/xsl/nwalsh/manpages/docbook.xsl manpage.xml

clean:
	rm -rf build
	rm -f video_*.jpg *~ src/Ui_* src/*.pyc *.txt *.1 data/lang/*.qm
	make -C data/help clean

install-for-debian: all install-bin install-man install-help install-media fix-install
	cp src/testfilm.py $(DESTDIR)/usr/share/python-mecavideo

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
	mkdir -p $(DESTDIR)/usr/share/doc/python-mecavideo/html
	for f in $(HELPFILES); do \
	  cp $$f $(DESTDIR)/usr/share/doc/python-mecavideo/html; \
	done

install-media:
	install -m 0644 data/icones/pymecavideo.xpm data/icones/pymecavideo-48.png \
	  $(DESTDIR)/usr/share/pixmaps
	install -m 0644 pymecavideo.desktop $(DESTDIR)/usr/share/applications
	install -m 0644 data/icones/pymecavideo.svg data/icones/pymecavideo.png \
	  $(DESTDIR)/usr/share/icons
	for d in data/icones data/video data/lang; do \
	  cp -a $$d $(DESTDIR)/usr/share/python-mecavideo ; \
	done

fix-install:
	find $(DESTDIR)/usr/share/python-mecavideo -name COPYING -exec rm {} \;
	find $(DESTDIR)/usr/share/python-mecavideo -type f -exec chmod 644 {} \;

.PHONY: clean all install-for-debian install-bin install-man install-help install-media fix-install helpfiles
