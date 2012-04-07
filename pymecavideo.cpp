#include "pymecavideo.h"
#include "ui_pymecavideo.h"
#include <QtGui/QApplication>
#include <QtGui>
#include <QTimer>
//#include <qmat.h>
//#include <cv.h>

using namespace cv;

PyMecaVideo::PyMecaVideo(QWidget *parent) :
    QMainWindow(parent),
    ui(new Ui::PyMecaVideo)
{
    ui->setupUi(this);
    //Init Signals
    QObject::connect(ui->actionOuvrir_un_fichier, SIGNAL(triggered() ),
                     this, SLOT(fileSelect()));
    //init variables
    homeDir = QDesktopServices::HomeLocation;

}

PyMecaVideo::~PyMecaVideo()
{

    qDebug()<<"quit";
    delete ui;
}
//functions

//select and show film frame Number "number"

Mat PyMecaVideo::getMat(uint number)
{//get matrice opencv from a source
//    Mat mat;
    //if capture -> don't initalize it
    qDebug()<<"entering in getMat";
//    if (!capture)
//    {
    qDebug()<<"initalizing capture from  file "<<videoFileName ;
//    if (!capture)
//    {
//        qDebug()<<"Capture not initialsed";
//    }
//    else
//    {
//            cvReleaseCapture(&capture);
//    }
//    capture = cvCaptureFromFile(videoFileName.toStdString().c_str()); //initialize file
//    qDebug()<<QString((double)capture->video_st->codec.frame_rate);
//    if (!capture)
//    {
//        qDebug()<<"WOUH WOUH !!! no capture !!!";
//    }
//    }

    //move to frame number 'number'
    //cvSetCaptureProperty(capture, CV_CAP_PROP_POS_MSEC, 0);
    qDebug()<<"set position in film (number of frame";
    double avi_ratio = number/100.0;
    cvSetCaptureProperty(capture, CV_CAP_PROP_POS_AVI_RATIO, avi_ratio);
    qDebug()<<"@@@@@@frame RATIO given is"<<avi_ratio<<"and it is set at"<<cvGetCaptureProperty(capture, CV_CAP_PROP_POS_AVI_RATIO);

    qDebug()<<"querying frame from capture";
    acquiredImage = cvQueryFrame(capture);
    if (!acquiredImage)
    {
        qDebug()<<"WOUH WOUH !!! no frame !!!";
    }
    qDebug()<<"transform IplImage in a cv::Mat";

    mat = Mat(acquiredImage,true);
    qDebug()<<"get out of getMat()";
    return mat;
}


void PyMecaVideo::loadPicture()
{

    pictureMat = getMat(num);
    qDebug()<<"open a QMat widget";
    QMat * qmat = new QMat(pictureMat, ui->widget);
    qmat->show();
    num += 1;
}

//fileSelect is called when radioButton "directory" is checked.
void PyMecaVideo::fileSelect() {

        videoFileName = QFileDialog::getOpenFileName(this,tr("pymecavideo","Open video file",
                                QApplication::UnicodeUTF8),homeDir,tr("Video files ( *.avi *.mp4 *.ogv *.mpg *.mpeg *.ogg *.wmv *.mov)"));
        if (!videoFileName.isEmpty()){
            setCurrentDir(videoFileName); //dirName is the name of choosen directory
            statusBar()->showMessage((tr("Video File choosen "), videoFileName), 2000);
            num = 0;
            //load first picture of video
            QTimer *timer = new QTimer(this);
            QObject::connect(timer, SIGNAL(timeout()), this, SLOT(loadPicture()));
            timer->start(1000);


                     }
}

//SETCURRENTDIR set working directory and display some informations on top of Qapplication and define "curDir"
void PyMecaVideo::setCurrentDir(const QString &fileName)
{
    curDir = fileName;
    QString shownName;
    if (curDir.isEmpty())
        shownName = "untitled.txt";
    else
        shownName = strippedName(curDir);

    setWindowTitle(tr("%1[*] - %2").arg(shownName).arg(tr("Application")));

}
//stripped name is name without path : /home/truc/video.avi return video.avi
QString PyMecaVideo::strippedName(const QString &fullFileName)
{
    return QFileInfo(fullFileName).fileName();
}
