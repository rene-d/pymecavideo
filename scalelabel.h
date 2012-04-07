#ifndef SCALELABEL_H
#define SCALELABEL_H

#include <QObject>
#include <QLabel>
#include <QPainter>
#include <QWidget>
#include <QtGui>

class ScaleLabel : public QLabel
{
    Q_OBJECT
public:
    explicit ScaleLabel(QLabel *parent = 0);
    QPoint scaleOrigin;
    QPoint scaleEnd;
signals:

public slots:

private:
    void paintEvent (QPaintEvent *event);
    void mouseMoveEvent (QMouseEvent *event);
    void mouseReleaseEvent (QMouseEvent *event);
    void mousePressEvent (QMouseEvent *event);
    QPainter painter;
    bool grabScale;
    bool released;
    QPoint mousePosition;

};

#endif // SCALELABEL_H
