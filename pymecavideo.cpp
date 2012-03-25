#include "pymecavideo.h"
#include "ui_pymecavideo.h"

PyMecaVideo::PyMecaVideo(QWidget *parent) :
    QMainWindow(parent),
    ui(new Ui::PyMecaVideo)
{
    ui->setupUi(this);
}

PyMecaVideo::~PyMecaVideo()
{
    delete ui;
}
