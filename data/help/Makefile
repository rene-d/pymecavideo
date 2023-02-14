SOURCES=$(shell ls *.xml)
SOURCES_W32 = $(shell ls *.svg) # image sources (width 32 px)
GENERATED_W32 = $(patsubst %.svg, %-w32.png, $(SOURCES_W32)) # generated images
TARGETS=$(SOURCES:.xml=.xhtml) 

all: $(TARGETS) images help-fr.html

%.html: %.md
	pandoc --css help-style.css --css static/jquery-ui/themes/base/jquery-ui.css --standalone $< -o $@

images: $(GENERATED_W32)

%-w32.png: %.svg
	if [ -x /usr/bin/rsvg-convert ]; then \
	  rsvg-convert -w 32 $< -o $@; \
	else \
	  inkscape --export-png=$@ --export-width=32 $<; \
	fi


%.xhtml : %.xml
	@echo "$<   => $@"
	@xsltproc --nonet /usr/share/xml/docbook/stylesheet/nwalsh/xhtml/docbook.xsl $< > $@
	@sed 's%</head>%<link rel="stylesheet" type="text/css" href="help.css" /></head>%' $@ > $@.tmp && mv $@.tmp $@

clean:
	rm -f *~ *.xhtml
	rm -f $(GENERATED_W32)

