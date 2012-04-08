#ifndef PYMECAVIDEO_H
#define PYMECAVIDEO_H

#include <QMainWindow>
#include <QDir>
#include <stdio.h>
#include <qmat.h>
#include <QPushButton>
#include <phonon/mediaobject.h>
#include <phonon/videoplayer.h>


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
    void loadPicture();
    void playpause();
    void stop();
    void fastforward();
    void fastbackward();
    void FPFforward();
    void FPFbackward();

private:
    Ui::PyMecaVideo *ui;
    QString videoFileName;
    void setCurrentDir(const QString &fileName);

    Mat getMat(uint);
    QString strippedName(const QString &fullFileName);
    QString curDir;
    QDir Dir;
    QString homeDir;
    QPushButton *OpenFile;
    QPushButton *PlayPauseButton;
    QPushButton *StopButton;
    QPushButton *FastForwardButton;
    QPushButton *FastBackwardButton;
    QPushButton *FPFForwardButton;
    QPushButton *FPFBackwardButton;
    Phonon::MediaObject m;
    QPushButton *metadatareaderbutton;
    Phonon::VideoPlayer *player;
int timeline;
 int newtimestamp;

//    CvCapture* capture;
//    IplImage* acquiredImage;
//    Mat mat;
//    Mat pictureMat;
//    QMat qmat;
    uint frameNumber;



};

#endif // PYMECAVIDEO_H
