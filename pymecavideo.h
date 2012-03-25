#ifndef PYMECAVIDEO_H
#define PYMECAVIDEO_H

#include <QMainWindow>

namespace Ui {
    class PyMecaVideo;
}

class PyMecaVideo : public QMainWindow
{
    Q_OBJECT

public:
    explicit PyMecaVideo(QWidget *parent = 0);
    ~PyMecaVideo();

private:
    Ui::PyMecaVideo *ui;
};

#endif // PYMECAVIDEO_H
