/*
@_PROJET_  "sources utils"
@_AUTEUR_  "PITETRE"
@_VERSION_ "1.0"
*/

#include "qmat.h"
#include <QtGui>

using namespace std;
using namespace cv;

        /// QMat


    QMat::QMat(QWidget *parent) : QWidget(parent)
    {   qDebug()<<"init QMat widget 1";
        _Label = new QLabel(this);
        setLabel();
    }

    QMat::QMat(Mat newMat, QWidget *parent) : QWidget(parent), _mat(newMat)
    {   qDebug()<<"init QMat widget 1";
        _Label = new QLabel(this);
        setLabel();
    }

    QMat::QMat(Mat (*mat_function)(), int waitTime, QWidget *parent) : QWidget(parent), _function(mat_function)
    {   qDebug()<<"init QMat widget 1";
        _timer = new QTimer(this);
        _timer->start(waitTime);
        _mat = _function();
        _Label = new QLabel(this);
        connect(_timer, SIGNAL(timeout()), this, SLOT(getFunctionMat()));
        setLabel();
    }

    void QMat::setWaitingTime(int newt)
    {
        _timer->start(newt);
    }

    void QMat::getFunctionMat()
    {
        _mat = _function();
        emit matChanged();
        setLabel();
    }

    void QMat::setMat(cv::Mat newMat)
    {
        _mat = newMat;
        setLabel();
    }

    void QMat::setFunction(cv::Mat (*new_function)())
    {
        _function = new_function;
    }

    void QMat::setLabel()
    {
        if(_mat.cols*_mat.rows)
        {
            Mat rgb;
            QPixmap p;
            cvtColor(_mat, rgb, (-2*_mat.channels()+10));
            p.convertFromImage(QImage(rgb.data, rgb.cols, rgb.rows, QImage::Format_RGB888));
            _Label->setPixmap(p);
            resize(_mat.cols, _mat.rows);
        }
    }
