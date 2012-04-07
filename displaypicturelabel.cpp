#include "displaypicturelabel.h"
#include "qlabel.h"
#include "qpoint.h"


DisplayPictureLabel::DisplayPictureLabel(QLabel *parent) :
    QLabel(parent)
{//In this label, Picture selected is shown. Some interaction are enabled.
    this->setMouseTracking(true);
    QPoint mousePosition = QPoint(0,0);

    grabPosition = false;
}
//void DisplayPictureLabel::demo() :
//{
//    //mouse move and clicks released are returned
//}
void DisplayPictureLabel::mouseMoveEvent(QMouseEvent* event)
{   if (grabPosition)
    {
    qDebug()<<QString::number(event->pos().x());
    qDebug()<<QString::number(event->pos().y());
    mousePosition =  event->pos();
    }
}

void DisplayPictureLabel::mouseReleaseEvent(QMouseEvent* event)
{   if (grabPosition)
    {
    qDebug()<<"Mouse released on X at"<<QString::number(event->pos().x());
    qDebug()<<"Mouse released on Y at"<<QString::number(event->pos().y());
    mousePositionOnClick =  event->pos();
    grabPosition = false; //once clic is done, need to define another action
    }
}

