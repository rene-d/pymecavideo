#ifndef ZOOM_H
#define ZOOM_H

#include <QWidget>
#include <QLabel>
#include <QPainter>

class Zoom : public QLabel
{
    Q_OBJECT
public:
    explicit Zoom(QLabel *parent = 0);

signals:

public slots:

private:
    void paintEvent (QPaintEvent *event);
    QPainter painter;

};

#endif // ZOOM_H
