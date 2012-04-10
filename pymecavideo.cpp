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
    Video=new Phonon::VideoWidget(ui->widget);



    //connections
   connect(ui->actionOuvrir_un_fichier, SIGNAL(triggered() ),
                 this, SLOT(fileSelect()));
   connect(ui->PlayPauseButton, SIGNAL(clicked()), this, SLOT(playpause()));
   connect(ui->pushButtonMajor, SIGNAL(clicked()), this, SLOT(FPFforward()));

   connect(ui->pushButtonMinor, SIGNAL(clicked()), this, SLOT(FPFbackward()));

   connect(ui->ScaleButton, SIGNAL(clicked()), this, SLOT(defineScale()));
   connect(Media, SIGNAL(tick(qint64)),this,SLOT(ticked(qint64)));
   connect(this, SIGNAL(frameChanged()),this,SLOT(updatePicture()));

}

void PyMecaVideo::updatePicture()
{
    //HACK HACK : it seems impossible to draw a transparent Qlabel on qvideoWidget /o\
    //when picture changed on videoWidget, pixmap is update on top level Qlabel
    QPixmap  snapshot=  QPixmap(QPixmap::grabWindow(ui->widget->winId()));
    scalelabel->setPix(snapshot);
}

void PyMecaVideo::ticked(qint64 tick)
{
    qDebug()<<"tick";
    emit frameChanged();

}

void PyMecaVideo::defineScale()
{
    QPixmap  snapshot=  QPixmap(QPixmap::grabWindow(ui->widget->winId()));
    qDebug()<<1;
    Video->hide();
    qDebug()<<2;
    ScaleLabel * scalelabel = new ScaleLabel(Video);
    scalelabel->setPix(snapshot);
    qDebug()<<3;

    qDebug()<<4;

    scale_in_pixel = QInputDialog::getText(this,
                                               tr("Définir l'échelle"),
                                               tr("Quel est la longueur connue ?"),
                                               QLineEdit::Normal, QString("1.0"));

    scalelabel->show();
    qDebug()<<5;
    qDebug()<<scale_in_pixel;
    scale_in_pixel.replace(",",".");


    while ((scale_in_pixel <= 0) or (scale_in_pixel.isNull()))
    {   scale_in_pixel = QInputDialog::getText(this,
        tr("Erreur !! Définir à nouveau l'échelle"),
        tr("Quel est la longueur connue ?"),
        QLineEdit::Normal, QString("1.0"));
    }


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
    emit frameChanged();
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
    newtimestamp=Media->currentTime()-TimePerFrame*1000;

    if (newtimestamp<0)
    {
    }
    else
    {
        Media->seek(newtimestamp);
    }
    qDebug()<<"timeline"<<Media->currentTime();
    emit frameChanged();
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
    newtimestamp=Media->currentTime()+TimePerFrame*1000;

    if (newtimestamp>timeline)
    {
    }
    else
    {
        Media->seek(newtimestamp);
    }
    qDebug()<<"timeline"<<Media->currentTime();
    emit frameChanged();
}

PyMecaVideo::~PyMecaVideo()
{

    qDebug()<<"quit";
    delete ui;
}


//select and show film

void PyMecaVideo::loadPicture()
{


            Video->setMouseTracking(true);

            //use of opencv to compute fps
            CvCapture *capture = cvCaptureFromFile(videoFileName.toStdString().c_str());
            fps = cvGetCaptureProperty(capture,CV_CAP_PROP_FPS);
            TimePerFrame = 1.0/fps;
            qDebug()<<"video framerate :"<<fps<<" fps or one frame is"<<TimePerFrame<<"long (s)";
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




            Media->seek(1);
            Video->show();
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
