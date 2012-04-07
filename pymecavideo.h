#ifndef PYMECAVIDEO_H
#define PYMECAVIDEO_H

#include <QMainWindow>
#include <QDir>
#include <stdio.h>
#include <qmat.h>

using namespace cv;

namespace Ui {
    class PyMecaVideo;
}

class PyMecaVideo : public QMainWindow
{
    Q_OBJECT

public:
    explicit PyMecaVideo(QWidget *parent = 0);
    ~PyMecaVideo();

private slots :
    void fileSelect();


private:
    Ui::PyMecaVideo *ui;
    QString videoFileName;
    void setCurrentDir(const QString &fileName);
    void loadPicture(uint);
    Mat getMat();
    QString strippedName(const QString &fullFileName);
    QString curDir;
    QDir Dir;
    QString homeDir;


};

#endif // PYMECAVIDEO_H
