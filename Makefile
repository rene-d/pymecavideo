#############################################################################
# Makefile for building: pymecavideo
# Generated by qmake (2.01a) (Qt 4.7.3) on: sam. avr. 7 19:09:52 2012
# Project:  pymecavideo.pro
# Template: app
# Command: /usr/bin/qmake -o Makefile pymecavideo.pro
#############################################################################

####### Compiler, tools and options

CC            = gcc
CXX           = g++
DEFINES       = -DQT_NO_DEBUG -DQT_PHONON_LIB -DQT_GUI_LIB -DQT_CORE_LIB -DQT_SHARED
CFLAGS        = -pipe -O2 -g -pipe -Wformat -Werror=format-security -Wp,-D_FORTIFY_SOURCE=2 -fstack-protector --param=ssp-buffer-size=4 -fomit-frame-pointer -march=i586 -mtune=generic -fasynchronous-unwind-tables -DPIC -fPIC -O2 -g -pipe -Wformat -Werror=format-security -Wp,-D_FORTIFY_SOURCE=2 -fstack-protector --param=ssp-buffer-size=4 -fomit-frame-pointer -march=i586 -mtune=generic -fasynchronous-unwind-tables -DPIC -fPIC -I/usr/include/opencv -Wall -W -D_REENTRANT $(DEFINES)
CXXFLAGS      = -pipe -O2 -g -pipe -Wformat -Werror=format-security -Wp,-D_FORTIFY_SOURCE=2 -fstack-protector --param=ssp-buffer-size=4 -fomit-frame-pointer -march=i586 -mtune=generic -fasynchronous-unwind-tables -DPIC -fPIC -O2 -g -pipe -Wformat -Werror=format-security -Wp,-D_FORTIFY_SOURCE=2 -fstack-protector --param=ssp-buffer-size=4 -fomit-frame-pointer -march=i586 -mtune=generic -fasynchronous-unwind-tables -DPIC -fPIC -I/usr/include/opencv -Wall -W -D_REENTRANT $(DEFINES)
INCPATH       = -I/usr/lib/qt4/mkspecs/linux-g++ -I. -I/usr/lib/qt4/include/QtCore -I/usr/lib/qt4/include/QtGui -I/usr/lib/qt4/include/phonon -I/usr/lib/qt4/include -I/usr/lib/qt4/include/phonon_compat -I. -I.
LINK          = g++
LFLAGS        = -Wl,--as-needed -Wl,--no-undefined -Wl,-z,relro -Wl,-O1 -Wl,--build-id -Wl,--enable-new-dtags -Wl,-O1
LIBS          = $(SUBLIBS)  -L/usr/lib -lopencv_core -lopencv_imgproc -lopencv_highgui -lopencv_ml -lopencv_video -lopencv_features2d -lopencv_calib3d -lopencv_objdetect -lopencv_contrib -lopencv_legacy -lopencv_flann -lphonon -lQtGui -L/usr/lib -lQtCore -lpthread 
AR            = ar cqs
RANLIB        = 
QMAKE         = /usr/bin/qmake
TAR           = tar -cf
COMPRESS      = gzip -9f
COPY          = cp -f
SED           = sed
COPY_FILE     = $(COPY)
COPY_DIR      = $(COPY) -r
STRIP         = 
INSTALL_FILE  = install -m 644 -p
INSTALL_DIR   = $(COPY_DIR)
INSTALL_PROGRAM = install -m 755 -p
DEL_FILE      = rm -f
SYMLINK       = ln -f -s
DEL_DIR       = rmdir
MOVE          = mv -f
CHK_DIR_EXISTS= test -d
MKDIR         = mkdir -p

####### Output directory

OBJECTS_DIR   = ./

####### Files

SOURCES       = main.cpp \
		pymecavideo.cpp \
		displaypicturelabel.cpp \
		zoom.cpp \
		scalelabel.cpp \
		qmat.cpp moc_pymecavideo.cpp \
		moc_displaypicturelabel.cpp \
		moc_zoom.cpp \
		moc_scalelabel.cpp \
		moc_qmat.cpp
OBJECTS       = main.o \
		pymecavideo.o \
		displaypicturelabel.o \
		zoom.o \
		scalelabel.o \
		qmat.o \
		moc_pymecavideo.o \
		moc_displaypicturelabel.o \
		moc_zoom.o \
		moc_scalelabel.o \
		moc_qmat.o
DIST          = /usr/lib/qt4/mkspecs/common/g++.conf \
		/usr/lib/qt4/mkspecs/common/unix.conf \
		/usr/lib/qt4/mkspecs/common/linux.conf \
		/usr/lib/qt4/mkspecs/qconfig.pri \
		/usr/lib/qt4/mkspecs/modules/qt_phonon.pri \
		/usr/lib/qt4/mkspecs/modules/qt_webkit_version.pri \
		/usr/lib/qt4/mkspecs/features/qt_functions.prf \
		/usr/lib/qt4/mkspecs/features/qt_config.prf \
		/usr/lib/qt4/mkspecs/features/exclusive_builds.prf \
		/usr/lib/qt4/mkspecs/features/default_pre.prf \
		/usr/lib/qt4/mkspecs/features/release.prf \
		/usr/lib/qt4/mkspecs/features/default_post.prf \
		/usr/lib/qt4/mkspecs/features/link_pkgconfig.prf \
		/usr/lib/qt4/mkspecs/features/warn_on.prf \
		/usr/lib/qt4/mkspecs/features/qt.prf \
		/usr/lib/qt4/mkspecs/features/unix/thread.prf \
		/usr/lib/qt4/mkspecs/features/moc.prf \
		/usr/lib/qt4/mkspecs/features/resources.prf \
		/usr/lib/qt4/mkspecs/features/uic.prf \
		/usr/lib/qt4/mkspecs/features/yacc.prf \
		/usr/lib/qt4/mkspecs/features/lex.prf \
		/usr/lib/qt4/mkspecs/features/include_source_dir.prf \
		pymecavideo.pro
QMAKE_TARGET  = pymecavideo
DESTDIR       = 
TARGET        = pymecavideo

first: all
####### Implicit rules

.SUFFIXES: .o .c .cpp .cc .cxx .C

.cpp.o:
	$(CXX) -c $(CXXFLAGS) $(INCPATH) -o "$@" "$<"

.cc.o:
	$(CXX) -c $(CXXFLAGS) $(INCPATH) -o "$@" "$<"

.cxx.o:
	$(CXX) -c $(CXXFLAGS) $(INCPATH) -o "$@" "$<"

.C.o:
	$(CXX) -c $(CXXFLAGS) $(INCPATH) -o "$@" "$<"

.c.o:
	$(CC) -c $(CFLAGS) $(INCPATH) -o "$@" "$<"

####### Build rules

all: Makefile $(TARGET)

$(TARGET): ui_pymecavideo.h $(OBJECTS)  
	$(LINK) $(LFLAGS) -o $(TARGET) $(OBJECTS) $(OBJCOMP) $(LIBS)

Makefile: pymecavideo.pro  /usr/lib/qt4/mkspecs/linux-g++/qmake.conf /usr/lib/qt4/mkspecs/common/g++.conf \
		/usr/lib/qt4/mkspecs/common/unix.conf \
		/usr/lib/qt4/mkspecs/common/linux.conf \
		/usr/lib/qt4/mkspecs/qconfig.pri \
		/usr/lib/qt4/mkspecs/modules/qt_phonon.pri \
		/usr/lib/qt4/mkspecs/modules/qt_webkit_version.pri \
		/usr/lib/qt4/mkspecs/features/qt_functions.prf \
		/usr/lib/qt4/mkspecs/features/qt_config.prf \
		/usr/lib/qt4/mkspecs/features/exclusive_builds.prf \
		/usr/lib/qt4/mkspecs/features/default_pre.prf \
		/usr/lib/qt4/mkspecs/features/release.prf \
		/usr/lib/qt4/mkspecs/features/default_post.prf \
		/usr/lib/qt4/mkspecs/features/link_pkgconfig.prf \
		/usr/lib/qt4/mkspecs/features/warn_on.prf \
		/usr/lib/qt4/mkspecs/features/qt.prf \
		/usr/lib/qt4/mkspecs/features/unix/thread.prf \
		/usr/lib/qt4/mkspecs/features/moc.prf \
		/usr/lib/qt4/mkspecs/features/resources.prf \
		/usr/lib/qt4/mkspecs/features/uic.prf \
		/usr/lib/qt4/mkspecs/features/yacc.prf \
		/usr/lib/qt4/mkspecs/features/lex.prf \
		/usr/lib/qt4/mkspecs/features/include_source_dir.prf \
		/usr/lib/libQtGui.prl \
		/usr/lib/libQtCore.prl
	$(QMAKE) -o Makefile pymecavideo.pro
/usr/lib/qt4/mkspecs/common/g++.conf:
/usr/lib/qt4/mkspecs/common/unix.conf:
/usr/lib/qt4/mkspecs/common/linux.conf:
/usr/lib/qt4/mkspecs/qconfig.pri:
/usr/lib/qt4/mkspecs/modules/qt_phonon.pri:
/usr/lib/qt4/mkspecs/modules/qt_webkit_version.pri:
/usr/lib/qt4/mkspecs/features/qt_functions.prf:
/usr/lib/qt4/mkspecs/features/qt_config.prf:
/usr/lib/qt4/mkspecs/features/exclusive_builds.prf:
/usr/lib/qt4/mkspecs/features/default_pre.prf:
/usr/lib/qt4/mkspecs/features/release.prf:
/usr/lib/qt4/mkspecs/features/default_post.prf:
/usr/lib/qt4/mkspecs/features/link_pkgconfig.prf:
/usr/lib/qt4/mkspecs/features/warn_on.prf:
/usr/lib/qt4/mkspecs/features/qt.prf:
/usr/lib/qt4/mkspecs/features/unix/thread.prf:
/usr/lib/qt4/mkspecs/features/moc.prf:
/usr/lib/qt4/mkspecs/features/resources.prf:
/usr/lib/qt4/mkspecs/features/uic.prf:
/usr/lib/qt4/mkspecs/features/yacc.prf:
/usr/lib/qt4/mkspecs/features/lex.prf:
/usr/lib/qt4/mkspecs/features/include_source_dir.prf:
/usr/lib/libQtGui.prl:
/usr/lib/libQtCore.prl:
qmake:  FORCE
	@$(QMAKE) -o Makefile pymecavideo.pro

dist: 
	@$(CHK_DIR_EXISTS) .tmp/pymecavideo1.0.0 || $(MKDIR) .tmp/pymecavideo1.0.0 
	$(COPY_FILE) --parents $(SOURCES) $(DIST) .tmp/pymecavideo1.0.0/ && $(COPY_FILE) --parents pymecavideo.h displaypicturelabel.h zoom.h scalelabel.h qmat.h .tmp/pymecavideo1.0.0/ && $(COPY_FILE) --parents main.cpp pymecavideo.cpp displaypicturelabel.cpp zoom.cpp scalelabel.cpp qmat.cpp .tmp/pymecavideo1.0.0/ && $(COPY_FILE) --parents pymecavideo.ui .tmp/pymecavideo1.0.0/ && (cd `dirname .tmp/pymecavideo1.0.0` && $(TAR) pymecavideo1.0.0.tar pymecavideo1.0.0 && $(COMPRESS) pymecavideo1.0.0.tar) && $(MOVE) `dirname .tmp/pymecavideo1.0.0`/pymecavideo1.0.0.tar.gz . && $(DEL_FILE) -r .tmp/pymecavideo1.0.0


clean:compiler_clean 
	-$(DEL_FILE) $(OBJECTS)
	-$(DEL_FILE) *~ core *.core


####### Sub-libraries

distclean: clean
	-$(DEL_FILE) $(TARGET) 
	-$(DEL_FILE) Makefile


check: first

mocclean: compiler_moc_header_clean compiler_moc_source_clean

mocables: compiler_moc_header_make_all compiler_moc_source_make_all

compiler_moc_header_make_all: moc_pymecavideo.cpp moc_displaypicturelabel.cpp moc_zoom.cpp moc_scalelabel.cpp moc_qmat.cpp
compiler_moc_header_clean:
	-$(DEL_FILE) moc_pymecavideo.cpp moc_displaypicturelabel.cpp moc_zoom.cpp moc_scalelabel.cpp moc_qmat.cpp
moc_pymecavideo.cpp: qmat.h \
		pymecavideo.h
	/usr/lib/qt4/bin/moc $(DEFINES) $(INCPATH) pymecavideo.h -o moc_pymecavideo.cpp

moc_displaypicturelabel.cpp: displaypicturelabel.h
	/usr/lib/qt4/bin/moc $(DEFINES) $(INCPATH) displaypicturelabel.h -o moc_displaypicturelabel.cpp

moc_zoom.cpp: zoom.h
	/usr/lib/qt4/bin/moc $(DEFINES) $(INCPATH) zoom.h -o moc_zoom.cpp

moc_scalelabel.cpp: scalelabel.h
	/usr/lib/qt4/bin/moc $(DEFINES) $(INCPATH) scalelabel.h -o moc_scalelabel.cpp

moc_qmat.cpp: qmat.h
	/usr/lib/qt4/bin/moc $(DEFINES) $(INCPATH) qmat.h -o moc_qmat.cpp

compiler_rcc_make_all:
compiler_rcc_clean:
compiler_image_collection_make_all: qmake_image_collection.cpp
compiler_image_collection_clean:
	-$(DEL_FILE) qmake_image_collection.cpp
compiler_moc_source_make_all:
compiler_moc_source_clean:
compiler_uic_make_all: ui_pymecavideo.h
compiler_uic_clean:
	-$(DEL_FILE) ui_pymecavideo.h
ui_pymecavideo.h: pymecavideo.ui
	/usr/lib/qt4/bin/uic pymecavideo.ui -o ui_pymecavideo.h

compiler_yacc_decl_make_all:
compiler_yacc_decl_clean:
compiler_yacc_impl_make_all:
compiler_yacc_impl_clean:
compiler_lex_make_all:
compiler_lex_clean:
compiler_clean: compiler_moc_header_clean compiler_uic_clean 

####### Compile

main.o: main.cpp pymecavideo.h \
		qmat.h
	$(CXX) -c $(CXXFLAGS) $(INCPATH) -o main.o main.cpp

pymecavideo.o: pymecavideo.cpp pymecavideo.h \
		qmat.h \
		ui_pymecavideo.h
	$(CXX) -c $(CXXFLAGS) $(INCPATH) -o pymecavideo.o pymecavideo.cpp

displaypicturelabel.o: displaypicturelabel.cpp displaypicturelabel.h
	$(CXX) -c $(CXXFLAGS) $(INCPATH) -o displaypicturelabel.o displaypicturelabel.cpp

zoom.o: zoom.cpp zoom.h
	$(CXX) -c $(CXXFLAGS) $(INCPATH) -o zoom.o zoom.cpp

scalelabel.o: scalelabel.cpp scalelabel.h
	$(CXX) -c $(CXXFLAGS) $(INCPATH) -o scalelabel.o scalelabel.cpp

qmat.o: qmat.cpp qmat.h
	$(CXX) -c $(CXXFLAGS) $(INCPATH) -o qmat.o qmat.cpp

moc_pymecavideo.o: moc_pymecavideo.cpp 
	$(CXX) -c $(CXXFLAGS) $(INCPATH) -o moc_pymecavideo.o moc_pymecavideo.cpp

moc_displaypicturelabel.o: moc_displaypicturelabel.cpp 
	$(CXX) -c $(CXXFLAGS) $(INCPATH) -o moc_displaypicturelabel.o moc_displaypicturelabel.cpp

moc_zoom.o: moc_zoom.cpp 
	$(CXX) -c $(CXXFLAGS) $(INCPATH) -o moc_zoom.o moc_zoom.cpp

moc_scalelabel.o: moc_scalelabel.cpp 
	$(CXX) -c $(CXXFLAGS) $(INCPATH) -o moc_scalelabel.o moc_scalelabel.cpp

moc_qmat.o: moc_qmat.cpp 
	$(CXX) -c $(CXXFLAGS) $(INCPATH) -o moc_qmat.o moc_qmat.cpp

####### Install

install:   FORCE

uninstall:   FORCE

FORCE:

