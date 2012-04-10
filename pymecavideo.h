#ifndef PYMECAVIDEO_H
#define PYMECAVIDEO_H

#include <QMainWindow>
#include <QPixmap>
#include <QDir>
#include <stdio.h>
#include <qmat.h>
#include <QPushButton>
#include <phonon/mediaobject.h>
#include <phonon/videoplayer.h>
#include <phonon/videowidget.h>
#include <phonon/seekslider.h>
#include <phonon/audiooutput.h>
#include <scalelabel.h>

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
    void FPFforward();
    void FPFbackward();
    void defineScale();
    void enableButton();
    void ticked(qint64);
    void updatePicture();


private:
    Ui::PyMecaVideo *ui;
    QString videoFileName;
    void setCurrentDir(const QString &fileName);

    CvCapture *capture ;
    double fps;
    double TimePerFrame;

    Mat getMat(uint);
    QString strippedName(const QString &fullFileName);
    QString curDir;
    QDir Dir;
    QString homeDir;
    QString scale_in_pixel;
    QPixmap  snapshot;
    QImage * frame;
    Phonon::VideoWidget *Video;

    Phonon::SeekSlider *SliderPiste;
    Phonon::MediaObject *Media;
    Phonon::MediaObject *Information;
    Phonon::AudioOutput *Audio;
    ScaleLabel *scalelabel;
    bool pause;
    bool scale_defined;







//    QPushButton *OpenFile;
//    QPushButton *PlayPauseButton;
//    QPushButton *StopButton;
//    QPushButton *FastForwardButton;
//    QPushButton *FastBackwardButton;
//    QPushButton *FPFForwardButton;
//    QPushButton *FPFBackwardButton;
//    Phonon::MediaObject m;
//    QPushButton *metadatareaderbutton;
//    Phonon::VideoPlayer *player;
int timeline;
 int newtimestamp;

//    CvCapture* capture;
//    IplImage* acquiredImage;
//    Mat mat;
//    Mat pictureMat;
//    QMat qmat;
    uint frameNumber;

signals:
    void frameChanged();

};

#endif // PYMECAVIDEO_H
