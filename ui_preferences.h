/********************************************************************************
** Form generated from reading ui file 'preferences.ui'
**
** Created: Tue Nov 11 13:11:37 2008
**      by: Qt User Interface Compiler version 4.4.3
**
** WARNING! All changes made in this file will be lost when recompiling ui file!
********************************************************************************/

#ifndef UI_PREFERENCES_H
#define UI_PREFERENCES_H

#include <QtCore/QVariant>
#include <QtGui/QAction>
#include <QtGui/QApplication>
#include <QtGui/QButtonGroup>
#include <QtGui/QComboBox>
#include <QtGui/QDialog>
#include <QtGui/QDialogButtonBox>
#include <QtGui/QGridLayout>
#include <QtGui/QLabel>
#include <QtGui/QLineEdit>
#include <QtGui/QSpinBox>

QT_BEGIN_NAMESPACE

class Ui_Dialog
{
public:
    QGridLayout *gridLayout;
    QLabel *label;
    QLineEdit *echelle_vEdit;
    QLabel *label_2;
    QComboBox *comboBoxProximite;
    QLabel *label_3;
    QComboBox *comboBoxVideoPLayer;
    QLabel *label_4;
    QSpinBox *spinBoxDbg;
    QDialogButtonBox *buttonBox;

    void setupUi(QDialog *Dialog)
    {
    if (Dialog->objectName().isEmpty())
        Dialog->setObjectName(QString::fromUtf8("Dialog"));
    Dialog->resize(338, 161);
    gridLayout = new QGridLayout(Dialog);
    gridLayout->setObjectName(QString::fromUtf8("gridLayout"));
    label = new QLabel(Dialog);
    label->setObjectName(QString::fromUtf8("label"));

    gridLayout->addWidget(label, 0, 0, 1, 1);

    echelle_vEdit = new QLineEdit(Dialog);
    echelle_vEdit->setObjectName(QString::fromUtf8("echelle_vEdit"));

    gridLayout->addWidget(echelle_vEdit, 0, 1, 1, 1);

    label_2 = new QLabel(Dialog);
    label_2->setObjectName(QString::fromUtf8("label_2"));

    gridLayout->addWidget(label_2, 1, 0, 1, 1);

    comboBoxProximite = new QComboBox(Dialog);
    comboBoxProximite->setObjectName(QString::fromUtf8("comboBoxProximite"));

    gridLayout->addWidget(comboBoxProximite, 1, 1, 1, 1);

    label_3 = new QLabel(Dialog);
    label_3->setObjectName(QString::fromUtf8("label_3"));

    gridLayout->addWidget(label_3, 2, 0, 1, 1);

    comboBoxVideoPLayer = new QComboBox(Dialog);
    comboBoxVideoPLayer->setObjectName(QString::fromUtf8("comboBoxVideoPLayer"));

    gridLayout->addWidget(comboBoxVideoPLayer, 2, 1, 1, 1);

    label_4 = new QLabel(Dialog);
    label_4->setObjectName(QString::fromUtf8("label_4"));

    gridLayout->addWidget(label_4, 3, 0, 1, 1);

    spinBoxDbg = new QSpinBox(Dialog);
    spinBoxDbg->setObjectName(QString::fromUtf8("spinBoxDbg"));
    spinBoxDbg->setMaximum(9);

    gridLayout->addWidget(spinBoxDbg, 3, 1, 1, 1);

    buttonBox = new QDialogButtonBox(Dialog);
    buttonBox->setObjectName(QString::fromUtf8("buttonBox"));
    buttonBox->setOrientation(Qt::Horizontal);
    buttonBox->setStandardButtons(QDialogButtonBox::Cancel|QDialogButtonBox::NoButton|QDialogButtonBox::Ok);

    gridLayout->addWidget(buttonBox, 4, 0, 1, 1);


    retranslateUi(Dialog);
    QObject::connect(buttonBox, SIGNAL(accepted()), Dialog, SLOT(accept()));
    QObject::connect(buttonBox, SIGNAL(rejected()), Dialog, SLOT(reject()));

    QMetaObject::connectSlotsByName(Dialog);
    } // setupUi

    void retranslateUi(QDialog *Dialog)
    {
    Dialog->setWindowTitle(QApplication::translate("Dialog", "Pr\303\251f\303\251rences de pyMecaVideo", 0, QApplication::UnicodeUTF8));
    label->setText(QApplication::translate("Dialog", "\303\211chelle des vitesses (px pour 1m/s)", 0, QApplication::UnicodeUTF8));
    label_2->setText(QApplication::translate("Dialog", "Vitesses affich\303\251es", 0, QApplication::UnicodeUTF8));
    label_3->setText(QApplication::translate("Dialog", "Afficheur vid\303\251o", 0, QApplication::UnicodeUTF8));
    label_4->setText(QApplication::translate("Dialog", "Niveau de verbosit\303\251 (d\303\251bogage)", 0, QApplication::UnicodeUTF8));
    Q_UNUSED(Dialog);
    } // retranslateUi

};

namespace Ui {
    class Dialog: public Ui_Dialog {};
} // namespace Ui

QT_END_NAMESPACE

#endif // UI_PREFERENCES_H
