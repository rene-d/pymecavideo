#include "pymecavideo.h"
#include "ui_pymecavideo.h"
#include <QtGui/QApplication>
#include <QCoreApplication>

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

    //init variables
    homeDir = QDesktopServices::HomeLocation;

    Media=new Phonon::MediaObject(this);

    //connections
   connect(ui->actionOuvrir_un_fichier, SIGNAL(triggered() ),
                 this, SLOT(fileSelect()));
   connect(ui->PlayPauseButton, SIGNAL(clicked()), this, SLOT(playpause()));
   connect(ui->pushButtonMajor, SIGNAL(clicked()), this, SLOT(FPFforward()));
   connect(ui->pushButtonMinor, SIGNAL(clicked()), this, SLOT(FPFbackward()));
   connect(ui->ScaleButton, SIGNAL(clicked()), this, SLOT(defineScale()));

}

void PyMecaVideo::defineScale()
{
    QPixmap  snapshot=  QPixmap(QPixmap::grabWindow(ui->widget->winId()));

    Video->hide();

    ScaleLabel * scalelabel = new ScaleLabel(ui->widget);
    scalelabel->setPix(snapshot);
    scalelabel->raise();
    scalelabel->show();


}

void PyMecaVideo::playpause()
{

    if(pause)
    {
//        PlayPauseButton->setIcon(QIcon(":/icons/Play"));
        Media->play();
        pause = false;

    }
    else if(!pause)
    {
//        PlayPauseButton->setIcon(QIcon(":/icons/Pause"));
        Media->pause();
        pause = true;
    }
}


void PyMecaVideo::FPFbackward()
{
    if(!pause)
    {
        Media->pause();
        pause=true;
    }
    else
    {}

    timeline=Media->totalTime();
    newtimestamp=Media->currentTime()-40;//Video with frame rate 25fps

    if (newtimestamp<0)
    {
    }
    else
    {
        Media->seek(newtimestamp);
    }

}

void PyMecaVideo::FPFforward()
{

    if(!pause)
    {
        Media->pause();
    }
    else
    {}

    timeline=Media->totalTime();
    newtimestamp=Media->currentTime()+40;//Video with frame rate 25fps

    if (newtimestamp>timeline)
    {
    }
    else
    {
        Media->seek(newtimestamp);
    }

}

PyMecaVideo::~PyMecaVideo()
{

    qDebug()<<"quit";
    delete ui;
}


//select and show film

void PyMecaVideo::loadPicture()
{

            Video=new Phonon::VideoWidget(ui->widget);
            Video->setMouseTracking(true);

            //use of opencv to compute fps
            CvCapture *capture = cvCaptureFromFile(videoFileName.toStdString().c_str());
            fps = cvGetCaptureProperty(capture,CV_CAP_PROP_FPS);
            qDebug()<<"video framerate : fps"<<fps;
            cvReleaseCapture( &capture );


            Media->setCurrentSource(videoFileName);
            ui->seekSlider->setMediaObject(Media);
            Information=new Phonon::MediaObject(this);
            Audio=new Phonon::AudioOutput(Phonon::VideoCategory);//need to get videowidget working

            Phonon::createPath(Media,Video);

            Video->setSizePolicy(QSizePolicy::Expanding,QSizePolicy::Expanding);
            Video->setScaleMode(Phonon::VideoWidget::ScaleAndCrop);
            Video->setAspectRatio(Phonon::VideoWidget::AspectRatioWidget);
            Video->installEventFilter(this);

            Video->show();
            Media->play();
            Media->pause();
            pause = true;
            enableButton();


}

void PyMecaVideo::enableButton()
{
    ui->PlayPauseButton->setEnabled(true);
    ui->pushButtonMajor->setEnabled(true);
    ui->pushButtonMinor->setEnabled(true);
    ui->seekSlider->setEnabled(true);

}


void PyMecaVideo::fileSelect() {

    if (Media->hasVideo())
    {
        Media->clearQueue();


    }

    videoFileName = QFileDialog::getOpenFileName(this,tr("pymecavideo","Open video file",
                            QApplication::UnicodeUTF8),homeDir,tr("Video files ( *.avi *.mp4 *.ogv *.mpg *.mpeg *.ogg *.wmv *.mov)"));
    if (!videoFileName.isEmpty()){
        setCurrentDir(videoFileName); //dirName is the name of choosen directory
        statusBar()->showMessage((tr("Video File choosen "), videoFileName), 2000);
        frameNumber = 0;
        //load first picture of video
        loadPicture();
        ui->ScaleButton->setEnabled(true);

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
