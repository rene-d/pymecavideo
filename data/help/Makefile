SOURCES=$(shell ls *.xml)
TARGETS=$(SOURCES:.xml=.xhtml)

all: $(TARGETS)

%.xhtml : %.xml
	@echo "$<   => $@"
	@xsltproc --nonet /usr/share/xml/docbook/stylesheet/nwalsh/xhtml/docbook.xsl $< > $@
	@sed 's%</head>%<link rel="stylesheet" type="text/css" href="help.css" /></head>%' $@ > $@.tmp && mv $@.tmp $@

clean:
	rm -f *~ *.xhtml

