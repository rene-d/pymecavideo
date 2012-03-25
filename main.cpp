#include <QtGui/QApplication>
#include "pymecavideo.h"

int main(int argc, char *argv[])
{
    QApplication a(argc, argv);
    PyMecaVideo w;
    w.show();

    return a.exec();
}
