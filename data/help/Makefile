SOURCES=$(shell ls *.xml)
SOURCES_W32 = win.svg tux.svg # image sources (width 32 px)
GENERATED_W32 = $(patsubst %.svg, %.png, $(SOURCES_W32)) # generated images
TARGETS=$(SOURCES:.xml=.xhtml) $(GENERATED_W32)

all: $(TARGETS)

win.png: win.svg
	inkscape --export-png=$@ --export-width=32 $<
tux.png: tux.svg
	inkscape --export-png=$@ --export-width=32 $<


%.xhtml : %.xml
	@echo "$<   => $@"
	@xsltproc --nonet /usr/share/xml/docbook/stylesheet/nwalsh/xhtml/docbook.xsl $< > $@
	@sed 's%</head>%<link rel="stylesheet" type="text/css" href="help.css" /></head>%' $@ > $@.tmp && mv $@.tmp $@

clean:
	rm -f *~ *.xhtml
	rm -f $(GENERATED_W32)

