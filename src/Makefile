DESTDIR = 
HELPFILES = $(shell ls help | grep -E 'xhtml$$|css$$|png$$')
LRELEASE = /usr/lib/qt5/bin/lrelease
SOURCES = $(shell ls *.py | grep -v Ui_)
TRANSLATIONS = $(shell find ../data/lang -name *.ts)
COMPILED_TRANSLATIONS = $(patsubst %.ts, %.qm, $(TRANSLATIONS))
GUIS = $(shell ls *.ui)
GRAPHS = $(shell ls *.dot)
GRAPHS_SVG = $(patsubst %.dot, %.svg, $(GRAPHS))
DOC_DEV = $(shell ls *.md)
DOC_DEV_HTML = $(patsubst %.md, %.html, $(DOC_DEV))

all: $(GRAPHS_SVG) $(DOC_DEV_HTML) $(COMPILED_TRANSLATIONS) helpfiles
	cd interfaces; $(MAKE) $@

%.svg : %.dot
	dot -Tsvg $< -o $@ || true

%.html : %.md $(GRAPHS_SVG)
	pandoc --standalone $< -o $@

$(TRANSLATIONS): $(SOURCES) $(GUIS)
	for t in $(TRANSLATIONS); do \
	  LC_ALL=en_US.UTF-8 pylupdate6 --ts $$t $(SOURCES) $(GUIS); \
	done

%.qm: %.ts
	lrelease ../data/lang/*.ts 2>&1 | grep -A2 "Updating"


helpfiles:
	@$(MAKE) -C ../data/help


pymecavideo.1: manpage.xml
	xsltproc --nonet /usr/share/sgml/docbook/stylesheet/xsl/nwalsh/manpages/docbook.xsl manpage.xml

clean:
	rm -rf build
	rm -f video_*.jpg *~ Ui_* *.pyc *.txt *.1 ../data/lang/*.qm *.log

install-for-debian: all install-bin install-man install-help install-media fix-install

install-bin:
	install -m 755 pymecavideo $(DESTDIR)/usr/bin

install-man:
	mkdir -p $(DESTDIR)/usr/share/man/man1
	gzip -c9 pymecavideo.1 > $(DESTDIR)/usr/share/man/man1/pymecavideo.1.gz

install-help:
	mkdir -p $(DESTDIR)/usr/share/doc/python-mecavideo/html
	for f in $(HELPFILES); do \
	  cp help/$$f $(DESTDIR)/usr/share/doc/python-mecavideo/html; \
	done

install-media:
	install -m 0644 ../data/icones/pymecavideo.xpm icones/pymecavideo-64x64.xpm \
	  $(DESTDIR)/usr/share/pixmaps
	install -m 0644 ../data/pymecavideo.desktop $(DESTDIR)/usr/share/applications
	install -m 0644 ../data/icones/pymecavideo.svg icones/pymecavideo.png \
	  $(DESTDIR)/usr/share/icons
	for d in icones video; do \
	  cp -a $$d $(DESTDIR)/usr/share/python-mecavideo ; \
	done

fix-install:
	find $(DESTDIR)/usr/share/python-mecavideo -name COPYING -exec rm {} \;
	find $(DESTDIR)/usr/share/python-mecavideo -type f -exec chmod 644 {} \;

install-ordinaire: all
	python3 setup.py install
	install -m 755 pymecavideo $(DESTDIR)/usr/bin
	mkdir -p $(DESTDIR)/usr/share/man/man1
	gzip -c9 pymecavideo.1 > $(DESTDIR)/usr/share/man/man1/pymecavideo.1.gz
	install -m 0644 ../data/icones/pymecavideo.xpm icones/pymecavideo-64x64.xpm \
	  $(DESTDIR)/usr/share/pixmaps
	install -m 0644 ../data/pymecavideo.desktop $(DESTDIR)/usr/share/applications
	install -m 0644 ../data/icones/pymecavideo.svg icones/pymecavideo.png \
	  $(DESTDIR)/usr/share/icons

.PHONY: clean all install-for-debian install-mime install-bin install-man install-help install-media fix-install install-ordinaire helpfiles
