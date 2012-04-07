#-------------------------------------------------
#
# Project created by QtCreator 2012-03-25T20:23:22
#
#-------------------------------------------------

QT       += core gui phonon

TARGET = pymecavideo
TEMPLATE = app


CONFIG += link_pkgconfig
PKGCONFIG += opencv



SOURCES += main.cpp\
        pymecavideo.cpp \
    displaypicturelabel.cpp \
    zoom.cpp \
    scalelabel.cpp \
    qmat.cpp

HEADERS  += pymecavideo.h \
    displaypicturelabel.h \
    zoom.h \
    scalelabel.h \
    qmat.h

FORMS    += pymecavideo.ui
