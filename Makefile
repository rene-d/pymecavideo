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


.PHONY: clean all manpages
