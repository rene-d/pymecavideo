#ifndef DISPLAYPICTURELABEL_H
#define DISPLAYPICTURELABEL_H

#include <QLabel>
#include <QtGui>

class DisplayPictureLabel : public QLabel
{
    Q_OBJECT
public:
    explicit DisplayPictureLabel(QLabel *parent = 0);
    bool grabPosition;
    QPoint mousePosition;
    QPoint mousePositionOnClick;
signals:

public slots:

private:
//    void paintEvent (QPaintEvent *event);
//    QPainter painter(this);
    void mouseMoveEvent (QMouseEvent *event);
    void mouseReleaseEvent (QMouseEvent *event);

};

#endif // DISPLAYPICTURELABEL_H
