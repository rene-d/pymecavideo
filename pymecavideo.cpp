#include "pymecavideo.h"
#include "ui_pymecavideo.h"
#include <QtGui/QApplication>
#include <QtGui>
#include <qmat.h>
#include <cv.h>

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
    delete ui;
}
//functions

//select and show film frame Number "number"

Mat PyMecaVideo::getMat()
{//get matrice opencv from a source
    Mat mat;
    VideoCapture cam(0);
    cam >> mat;// vous pouvez ensuite executer autant de transformation que vous voulez, le tout est de renvoyer un cv::Mat
    return mat;
}

void PyMecaVideo::loadPicture(uint number)
{
    Mat mat;
    mat = getMat();
    QMat qmat(mat, ui->label);
    qmat.show();
}

//fileSelect is called when radioButton "directory" is checked.
void PyMecaVideo::fileSelect() {

        QString videoFileName = QFileDialog::getOpenFileName(this,tr("pymecavideo","Open video file",
                                QApplication::UnicodeUTF8),homeDir,tr("Video files ( *.avi *.mp4 *.ogv *.mpg *.mpeg *.ogg *.wmv *.mov)"));
        if (!videoFileName.isEmpty()){
            setCurrentDir(videoFileName); //dirName is the name of choosen directory
            statusBar()->showMessage((tr("Video File choosen "), videoFileName), 2000);
            //load first picture of video
            loadPicture(1);
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
