SOURCES=$(shell ls *.md)
SOURCES_W32 = $(shell ls *.svg) # image sources (width 32 px)
GENERATED_W32 = $(patsubst %.svg, %-w32.png, $(SOURCES_W32)) # generated images
TARGETS=$(SOURCES:.md=.html)

all: $(TARGETS) images help-fr.html

%.html: %.md
	pandoc --css help-style.css --css static/jquery-ui/themes/base/jquery-ui.css --standalone $< -o $@

images: $(GENERATED_W32)

%-w32.png: %.svg
	  rsvg-convert -w 32 $< -o $@

clean:
	rm -f *~ *.html
	rm -f $(GENERATED_W32)

