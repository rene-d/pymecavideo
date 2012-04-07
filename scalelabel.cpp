#include "scalelabel.h"
#include "qrect.h"
#include "qlabel.h"


ScaleLabel::ScaleLabel(QLabel *parent) :
    QLabel(parent)
{
    this->setGeometry(QRect(0,0,640,480));
    this->setAutoFillBackground(false);
    this->setMouseTracking(true);
    grabScale = false;
    released = false;
//    QPoint mousePosition = new QPoint;
}

void ScaleLabel::paintEvent(QPaintEvent* event)
{
        QPainter painter(this);

        painter.begin(this);
        painter.setPen(Qt::red);
        if (grabScale)
        {
            painter.drawLine(scaleOrigin, mousePosition);
        }
        painter.end();
}


void ScaleLabel::mouseMoveEvent(QMouseEvent* event)
{   //if mouse is pressed, scale is shown

    qDebug()<<QString::number(event->pos().x());
    qDebug()<<QString::number(event->pos().y());
    mousePosition =  event->pos();


    //update picture in zoom until mouse is released
    if (!released) {
        //update zoom picture
    }

}

void ScaleLabel::mousePressEvent(QMouseEvent* event)
{
    grabScale = true;
    scaleOrigin = event->pos();

}

void ScaleLabel::mouseReleaseEvent(QMouseEvent* event)
{
    grabScale = false;
    released=false;
    scaleEnd = event->pos();

}
