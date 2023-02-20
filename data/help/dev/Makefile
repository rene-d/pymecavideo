DESTDIR =

all: reference_html.tar.gz

reference_html.tar.gz: force
	doxygen
	cd out; tar --exclude="*.md5" --exclude="*.map" -czf \
	  ../reference_html.tar.gz html

clean:
	rm -rf out/

.PHONY: all clean force
