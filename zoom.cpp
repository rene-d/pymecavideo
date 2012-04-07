#include "zoom.h"
#include "qlabel.h"

Zoom::Zoom(QLabel *parent) :
    QLabel(parent)
{this->setGeometry(QRect(0, 0, 100, 100));
 this->setAutoFillBackground(false);
}
void Zoom::paintEvent(QPaintEvent *)
{
    painter.begin(this);
    painter.setPen(Qt::red);
    painter.drawLine(50, 0, 50, 45);
    painter.drawLine(50, 55, 50, 100);
    painter.drawLine(0, 50, 45, 50);
    painter.drawLine(55, 50, 100, 50);
    painter.drawEllipse(50,50,5,5);
    painter.end();
}
