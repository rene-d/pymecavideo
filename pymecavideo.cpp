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
    QObject::connect(ui->actionOuvrir_un_fichier, SIGNAL(triggered() ),
                     this, SLOT(fileSelect()));
    //init variables
    homeDir = QDesktopServices::HomeLocation;

    //Video player creation
//       Phonon::VideoPlayer * player=new Phonon::VideoPlayer(Phonon::VideoCategory,ui->widget);
//       player->setSizePolicy(QSizePolicy::Expanding,QSizePolicy::Expanding);

//       PlayPauseButton=new QPushButton("play-pause",ui->frame);
//       StopButton=new QPushButton("stop",ui->frame);
//       FastForwardButton=new QPushButton(">>",ui->frame);
//       FastBackwardButton=new QPushButton("<<",ui->frame);
//       FPFForwardButton=new QPushButton("+1 Img",ui->frame);
//       FPFBackwardButton=new QPushButton("-1 Img",ui->frame);
//       QHBoxLayout *LayoutBoutonsPlayer=new QHBoxLayout(ui->frame);
//           LayoutBoutonsPlayer->addWidget(FastBackwardButton);
//           LayoutBoutonsPlayer->addWidget(FPFBackwardButton);
//           LayoutBoutonsPlayer->addWidget(PlayPauseButton);
//           LayoutBoutonsPlayer->addWidget(StopButton);
//           LayoutBoutonsPlayer->addWidget(FPFForwardButton);
//           LayoutBoutonsPlayer->addWidget(FastForwardButton);

           connect(ui->PlayPauseButton, SIGNAL(clicked()), this, SLOT(playpause()));
//           connect(StopButton, SIGNAL(clicked()), this, SLOT(stop()));
//           connect(FastForwardButton, SIGNAL(clicked()), this, SLOT(fastforward()));
//           connect(FastBackwardButton, SIGNAL(clicked()), this, SLOT(fastbackward()));
           connect(ui->pushButtonMajor, SIGNAL(clicked()), this, SLOT(FPFforward()));
           connect(ui->pushButtonMinor, SIGNAL(clicked()), this, SLOT(FPFbackward()));
           connect(ui->ScaleButton, SIGNAL(clicked()), this, SLOT(defineScale()));

}

void PyMecaVideo::defineScale()
{
    QPixmap  snapshot=  QPixmap(QPixmap::grabWindow(ui->widget->winId()));
    qDebug() << "snapshot captured?" << !snapshot.isNull();
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
//        ui->PlayPauseButton->setCheckable(false);
//        ui->PlayPauseButton->setChecked(false);
        Media->play();
        pause = false;

    }
    else if(!pause)
    {
//        PlayPauseButton->setIcon(QIcon(":/icons/Pause"));
//        PlayPauseButton->setCheckable(true);
//        PlayPauseButton->setChecked(true);
        Media->pause();
        pause = true;
    }
}

//void PyMecaVideo::stop()
//{
//    PlayPauseButton->setIcon(QIcon(":/icons/Play"));
//    player->stop();
//}

//void PyMecaVideo::fastforward()
//{
//    timeline=player->totalTime();


//    newtimestamp=player->currentTime()+timeline/10;
//    //QMessageBox::information(0,"Titre de la fenêtre",QString::number(newtimestamp));

//    if (newtimestamp>timeline)
//    {
//        player->stop();
//    }
//    else
//    {
//        player->seek(newtimestamp);
//    }
//}

//void PyMecaVideo::fastbackward()
//{
//    timeline=player->totalTime();


//    newtimestamp=player->currentTime()-timeline/10;
//    //QMessageBox::information(0,"Titre de la fenêtre",QString::number(newtimestamp));

//    if (newtimestamp<0)
//    {
//        player->seek(0);
//    }
//    else
//    {
//        player->seek(newtimestamp);
//    }
//}

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

    //QMessageBox::information(0,"Titre de la fenêtre",QString::number(timeline));
    //QMessageBox::information(0,"Titre de la fenêtre",QString::number(newtimestamp));
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
//functions

//select and show film frame Number "number"


void PyMecaVideo::loadPicture()
{   qDebug()<<"1";
//    Phonon::MediaObject *media = new Phonon::MediaObject(this);
//    Phonon::VideoPlayer *player = new Phonon::VideoPlayer(Phonon::VideoCategory, ui->widget);

//    media->setCurrentSource(videoFileName);
//    qDebug()<<"2";
//    connect(player, SIGNAL(finished()), player, SLOT(deleteLater()));
//    qDebug()<<"3";

    qDebug()<<"4";


//    m.setCurrentSource(videoFileName);
//    Phonon::createPath(m,player);
//        qDebug()<<"3";
//        player->play(Phonon::MediaSource(m.currentSource()));
            qDebug()<<"2";
//    player->load(videoFileName);

//    player->show();

//    qDebug()<<ui->seekSlider->mediaObject()<<player->mediaObject();
            Video=new Phonon::VideoWidget(ui->widget);
            Video->setMouseTracking(true);
//            /*SliderVolume*/=new Phonon::VolumeSlider;
//            SliderPiste=new Phonon::SeekSlider(ui->frame);
//            ui->seekSlider->show();
            Media=new Phonon::MediaObject(this);
            Media->setCurrentSource(videoFileName);
            ui->seekSlider->setMediaObject(Media);
            Information=new Phonon::MediaObject(this);
            Audio=new Phonon::AudioOutput(Phonon::VideoCategory);

            //je pense que c'est ce qu'il te faut des patch
//            Phonon::createPath(Media,Audio);//le média a l'audio
            Phonon::createPath(Media,Video); //le media a la video//

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

}

//fileSelect is called when radioButton "directory" is checked.
void PyMecaVideo::fileSelect() {

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
