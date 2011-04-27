DESTDIR =

CXX = g++
CXXFLAGS = -O2 -g
INCLUDEPATH = $(shell pkg-config --cflags opencv) \
	      $(shell pkg-config --cflags gtk+-2.0)
LDFLAGS =  -lm $(shell pkg-config --libs opencv) \
	   $(shell pkg-config --libs gtk+-2.0)
CSOURCES = $(shell ls *.cpp)
COBJ = $(patsubst %.cpp, %.o, $(CSOURCES))

# build dependencies : libcv-dev, libcvaux-dev, libhighgui-dev, libgtk-dev

all: cadreur

clean:
	rm -f *~ Ui_*.py *.pyc cadreur *.o

install: all
	install -m 755 cadreur $(DESTDIR)/usr/bin

test: cadreur
	./cadreur ../pymecavideo-5.5/data/video/g1.avi

cadreur: $(COBJ)
	$(CXX) -o $@ $(LDFLAGS) $(COBJ)

%.o : %.cpp %.hpp
	$(CXX) -c $(CXXFLAGS) $(INCLUDEPATH) $<

Ui_essai.py: essai.ui
	pyuic4 $< > $@

.PHONY: all clean test
