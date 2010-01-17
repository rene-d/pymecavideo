/********************************************************************************
** Form generated from reading ui file 'pymecavideo.ui'
**
** Created: Tue Nov 11 13:11:37 2008
**      by: Qt User Interface Compiler version 4.4.3
**
** WARNING! All changes made in this file will be lost when recompiling ui file!
********************************************************************************/

#ifndef UI_PYMECAVIDEO_H
#define UI_PYMECAVIDEO_H

#include <QtCore/QVariant>
#include <QtGui/QAction>
#include <QtGui/QApplication>
#include <QtGui/QButtonGroup>
#include <QtGui/QComboBox>
#include <QtGui/QHBoxLayout>
#include <QtGui/QLabel>
#include <QtGui/QLineEdit>
#include <QtGui/QMainWindow>
#include <QtGui/QMenu>
#include <QtGui/QMenuBar>
#include <QtGui/QPushButton>
#include <QtGui/QSlider>
#include <QtGui/QSpacerItem>
#include <QtGui/QSpinBox>
#include <QtGui/QStatusBar>
#include <QtGui/QTabWidget>
#include <QtGui/QVBoxLayout>
#include <QtGui/QWidget>

QT_BEGIN_NAMESPACE

class Ui_pymecavideo
{
public:
    QAction *actionOuvrir_un_fichier;
    QAction *actionAvanceimage;
    QAction *actionReculeimage;
    QAction *actionQuitter;
    QAction *actionSaveData;
    QAction *action_propos;
    QAction *actionAide;
    QAction *actionExemples;
    QAction *actionRouvrirMecavideo;
    QAction *actionPreferences;
    QAction *actionCopier_dans_le_presse_papier;
    QWidget *centralwidget;
    QHBoxLayout *hboxLayout;
    QTabWidget *tabWidget;
    QWidget *tab_acq;
    QLabel *label;
    QLabel *label_infos_image;
    QSlider *horizontalSlider;
    QPushButton *Bouton_Echelle;
    QSpinBox *spinBox_image;
    QLabel *label_numero_image;
    QSpinBox *spinBox_nb_de_points;
    QLabel *label_2;
    QLineEdit *echelleEdit;
    QLabel *label_4;
    QPushButton *Bouton_lance_capture;
    QPushButton *pushButton_reinit;
    QPushButton *pushButton_defait;
    QPushButton *pushButton_refait;
    QWidget *tab_traj;
    QLabel *label_3;
    QWidget *layoutWidget;
    QHBoxLayout *hboxLayout1;
    QVBoxLayout *vboxLayout;
    QLabel *label_7;
    QComboBox *comboBox_referentiel;
    QSpacerItem *spacerItem;
    QVBoxLayout *vboxLayout1;
    QPushButton *button_video;
    QComboBox *comboBox_fps;
    QSpacerItem *spacerItem1;
    QVBoxLayout *vboxLayout2;
    QLabel *label_5;
    QHBoxLayout *hboxLayout2;
    QComboBox *echelle_v;
    QLabel *label_6;
    QWidget *tab_coord;
    QPushButton *pushButton_select_all_table;
    QMenuBar *menubar;
    QMenu *menuFichier;
    QMenu *menuAide;
    QMenu *menu_dition;
    QStatusBar *statusbar;

    void setupUi(QMainWindow *pymecavideo)
    {
    if (pymecavideo->objectName().isEmpty())
        pymecavideo->setObjectName(QString::fromUtf8("pymecavideo"));
    pymecavideo->resize(673, 675);
    actionOuvrir_un_fichier = new QAction(pymecavideo);
    actionOuvrir_un_fichier->setObjectName(QString::fromUtf8("actionOuvrir_un_fichier"));
    actionAvanceimage = new QAction(pymecavideo);
    actionAvanceimage->setObjectName(QString::fromUtf8("actionAvanceimage"));
    actionReculeimage = new QAction(pymecavideo);
    actionReculeimage->setObjectName(QString::fromUtf8("actionReculeimage"));
    actionQuitter = new QAction(pymecavideo);
    actionQuitter->setObjectName(QString::fromUtf8("actionQuitter"));
    actionSaveData = new QAction(pymecavideo);
    actionSaveData->setObjectName(QString::fromUtf8("actionSaveData"));
    action_propos = new QAction(pymecavideo);
    action_propos->setObjectName(QString::fromUtf8("action_propos"));
    actionAide = new QAction(pymecavideo);
    actionAide->setObjectName(QString::fromUtf8("actionAide"));
    actionExemples = new QAction(pymecavideo);
    actionExemples->setObjectName(QString::fromUtf8("actionExemples"));
    actionRouvrirMecavideo = new QAction(pymecavideo);
    actionRouvrirMecavideo->setObjectName(QString::fromUtf8("actionRouvrirMecavideo"));
    actionPreferences = new QAction(pymecavideo);
    actionPreferences->setObjectName(QString::fromUtf8("actionPreferences"));
    actionCopier_dans_le_presse_papier = new QAction(pymecavideo);
    actionCopier_dans_le_presse_papier->setObjectName(QString::fromUtf8("actionCopier_dans_le_presse_papier"));
    centralwidget = new QWidget(pymecavideo);
    centralwidget->setObjectName(QString::fromUtf8("centralwidget"));
    centralwidget->setGeometry(QRect(0, 22, 673, 631));
    hboxLayout = new QHBoxLayout(centralwidget);
    hboxLayout->setObjectName(QString::fromUtf8("hboxLayout"));
    tabWidget = new QTabWidget(centralwidget);
    tabWidget->setObjectName(QString::fromUtf8("tabWidget"));
    tabWidget->setAutoFillBackground(true);
    tab_acq = new QWidget();
    tab_acq->setObjectName(QString::fromUtf8("tab_acq"));
    tab_acq->setGeometry(QRect(0, 0, 651, 589));
    label = new QLabel(tab_acq);
    label->setObjectName(QString::fromUtf8("label"));
    label->setEnabled(true);
    label->setGeometry(QRect(10, 100, 640, 480));
    QPalette palette;
    QBrush brush(QColor(255, 255, 255, 255));
    brush.setStyle(Qt::SolidPattern);
    palette.setBrush(QPalette::Active, QPalette::Base, brush);
    QBrush brush1(QColor(147, 147, 147, 255));
    brush1.setStyle(Qt::SolidPattern);
    palette.setBrush(QPalette::Active, QPalette::Window, brush1);
    palette.setBrush(QPalette::Inactive, QPalette::Base, brush);
    palette.setBrush(QPalette::Inactive, QPalette::Window, brush1);
    palette.setBrush(QPalette::Disabled, QPalette::Base, brush1);
    palette.setBrush(QPalette::Disabled, QPalette::Window, brush1);
    label->setPalette(palette);
    label->setCursor(QCursor(Qt::ArrowCursor));
    label->setAutoFillBackground(true);
    label->setTextInteractionFlags(Qt::NoTextInteraction);
    label_infos_image = new QLabel(tab_acq);
    label_infos_image->setObjectName(QString::fromUtf8("label_infos_image"));
    label_infos_image->setGeometry(QRect(0, 70, 341, 20));
    label_infos_image->setAlignment(Qt::AlignCenter);
    horizontalSlider = new QSlider(tab_acq);
    horizontalSlider->setObjectName(QString::fromUtf8("horizontalSlider"));
    horizontalSlider->setGeometry(QRect(10, 50, 281, 16));
    horizontalSlider->setOrientation(Qt::Horizontal);
    Bouton_Echelle = new QPushButton(tab_acq);
    Bouton_Echelle->setObjectName(QString::fromUtf8("Bouton_Echelle"));
    Bouton_Echelle->setEnabled(false);
    Bouton_Echelle->setGeometry(QRect(140, 20, 101, 26));
    spinBox_image = new QSpinBox(tab_acq);
    spinBox_image->setObjectName(QString::fromUtf8("spinBox_image"));
    spinBox_image->setGeometry(QRect(69, 21, 51, 26));
    spinBox_image->setMinimumSize(QSize(51, 26));
    spinBox_image->setAlignment(Qt::AlignRight|Qt::AlignTrailing|Qt::AlignVCenter);
    label_numero_image = new QLabel(tab_acq);
    label_numero_image->setObjectName(QString::fromUtf8("label_numero_image"));
    label_numero_image->setGeometry(QRect(11, 21, 52, 26));
    label_numero_image->setAutoFillBackground(false);
    label_numero_image->setAlignment(Qt::AlignCenter);
    spinBox_nb_de_points = new QSpinBox(tab_acq);
    spinBox_nb_de_points->setObjectName(QString::fromUtf8("spinBox_nb_de_points"));
    spinBox_nb_de_points->setGeometry(QRect(404, 24, 51, 26));
    spinBox_nb_de_points->setAlignment(Qt::AlignRight|Qt::AlignTrailing|Qt::AlignVCenter);
    spinBox_nb_de_points->setMinimum(1);
    spinBox_nb_de_points->setMaximum(10);
    label_2 = new QLabel(tab_acq);
    label_2->setObjectName(QString::fromUtf8("label_2"));
    label_2->setGeometry(QRect(351, 1, 157, 16));
    echelleEdit = new QLineEdit(tab_acq);
    echelleEdit->setObjectName(QString::fromUtf8("echelleEdit"));
    echelleEdit->setGeometry(QRect(251, 21, 55, 26));
    echelleEdit->setMinimumSize(QSize(55, 26));
    echelleEdit->setFocusPolicy(Qt::NoFocus);
    echelleEdit->setReadOnly(true);
    label_4 = new QLabel(tab_acq);
    label_4->setObjectName(QString::fromUtf8("label_4"));
    label_4->setGeometry(QRect(312, 21, 28, 26));
    Bouton_lance_capture = new QPushButton(tab_acq);
    Bouton_lance_capture->setObjectName(QString::fromUtf8("Bouton_lance_capture"));
    Bouton_lance_capture->setGeometry(QRect(510, 20, 136, 26));
    pushButton_reinit = new QPushButton(tab_acq);
    pushButton_reinit->setObjectName(QString::fromUtf8("pushButton_reinit"));
    pushButton_reinit->setGeometry(QRect(510, 60, 131, 25));
    QPalette palette1;
    QBrush brush2(QColor(255, 0, 0, 255));
    brush2.setStyle(Qt::SolidPattern);
    palette1.setBrush(QPalette::Active, QPalette::WindowText, brush2);
    palette1.setBrush(QPalette::Active, QPalette::ButtonText, brush2);
    palette1.setBrush(QPalette::Inactive, QPalette::WindowText, brush2);
    palette1.setBrush(QPalette::Inactive, QPalette::ButtonText, brush2);
    QBrush brush3(QColor(148, 151, 153, 255));
    brush3.setStyle(Qt::SolidPattern);
    palette1.setBrush(QPalette::Disabled, QPalette::WindowText, brush3);
    QBrush brush4(QColor(138, 143, 148, 255));
    brush4.setStyle(Qt::SolidPattern);
    palette1.setBrush(QPalette::Disabled, QPalette::ButtonText, brush4);
    pushButton_reinit->setPalette(palette1);
    pushButton_defait = new QPushButton(tab_acq);
    pushButton_defait->setObjectName(QString::fromUtf8("pushButton_defait"));
    pushButton_defait->setEnabled(false);
    pushButton_defait->setGeometry(QRect(400, 60, 31, 25));
    pushButton_refait = new QPushButton(tab_acq);
    pushButton_refait->setObjectName(QString::fromUtf8("pushButton_refait"));
    pushButton_refait->setEnabled(false);
    pushButton_refait->setGeometry(QRect(430, 60, 31, 25));
    tabWidget->addTab(tab_acq, QString());
    tab_traj = new QWidget();
    tab_traj->setObjectName(QString::fromUtf8("tab_traj"));
    tab_traj->setGeometry(QRect(0, 0, 512, 307));
    label_3 = new QLabel(tab_traj);
    label_3->setObjectName(QString::fromUtf8("label_3"));
    label_3->setGeometry(QRect(10, 100, 640, 480));
    QPalette palette2;
    palette2.setBrush(QPalette::Active, QPalette::Base, brush);
    QBrush brush5(QColor(194, 197, 196, 255));
    brush5.setStyle(Qt::SolidPattern);
    palette2.setBrush(QPalette::Active, QPalette::Window, brush5);
    palette2.setBrush(QPalette::Inactive, QPalette::Base, brush);
    palette2.setBrush(QPalette::Inactive, QPalette::Window, brush5);
    palette2.setBrush(QPalette::Disabled, QPalette::Base, brush5);
    palette2.setBrush(QPalette::Disabled, QPalette::Window, brush5);
    label_3->setPalette(palette2);
    label_3->setCursor(QCursor(Qt::ArrowCursor));
    label_3->setAutoFillBackground(true);
    layoutWidget = new QWidget(tab_traj);
    layoutWidget->setObjectName(QString::fromUtf8("layoutWidget"));
    layoutWidget->setGeometry(QRect(20, 10, 585, 60));
    hboxLayout1 = new QHBoxLayout(layoutWidget);
    hboxLayout1->setObjectName(QString::fromUtf8("hboxLayout1"));
    hboxLayout1->setContentsMargins(0, 0, 0, 0);
    vboxLayout = new QVBoxLayout();
    vboxLayout->setObjectName(QString::fromUtf8("vboxLayout"));
    label_7 = new QLabel(layoutWidget);
    label_7->setObjectName(QString::fromUtf8("label_7"));

    vboxLayout->addWidget(label_7);

    comboBox_referentiel = new QComboBox(layoutWidget);
    comboBox_referentiel->setObjectName(QString::fromUtf8("comboBox_referentiel"));
    comboBox_referentiel->setMinimumSize(QSize(130, 25));

    vboxLayout->addWidget(comboBox_referentiel);


    hboxLayout1->addLayout(vboxLayout);

    spacerItem = new QSpacerItem(40, 20, QSizePolicy::Expanding, QSizePolicy::Minimum);

    hboxLayout1->addItem(spacerItem);

    vboxLayout1 = new QVBoxLayout();
    vboxLayout1->setObjectName(QString::fromUtf8("vboxLayout1"));
    button_video = new QPushButton(layoutWidget);
    button_video->setObjectName(QString::fromUtf8("button_video"));

    vboxLayout1->addWidget(button_video);

    comboBox_fps = new QComboBox(layoutWidget);
    comboBox_fps->setObjectName(QString::fromUtf8("comboBox_fps"));

    vboxLayout1->addWidget(comboBox_fps);


    hboxLayout1->addLayout(vboxLayout1);

    spacerItem1 = new QSpacerItem(40, 20, QSizePolicy::Expanding, QSizePolicy::Minimum);

    hboxLayout1->addItem(spacerItem1);

    vboxLayout2 = new QVBoxLayout();
    vboxLayout2->setObjectName(QString::fromUtf8("vboxLayout2"));
    label_5 = new QLabel(layoutWidget);
    label_5->setObjectName(QString::fromUtf8("label_5"));

    vboxLayout2->addWidget(label_5);

    hboxLayout2 = new QHBoxLayout();
    hboxLayout2->setObjectName(QString::fromUtf8("hboxLayout2"));
    echelle_v = new QComboBox(layoutWidget);
    echelle_v->setObjectName(QString::fromUtf8("echelle_v"));
    echelle_v->setMinimumSize(QSize(61, 25));
    echelle_v->setEditable(true);

    hboxLayout2->addWidget(echelle_v);

    label_6 = new QLabel(layoutWidget);
    label_6->setObjectName(QString::fromUtf8("label_6"));

    hboxLayout2->addWidget(label_6);


    vboxLayout2->addLayout(hboxLayout2);


    hboxLayout1->addLayout(vboxLayout2);

    tabWidget->addTab(tab_traj, QString());
    tab_coord = new QWidget();
    tab_coord->setObjectName(QString::fromUtf8("tab_coord"));
    tab_coord->setGeometry(QRect(0, 0, 512, 307));
    pushButton_select_all_table = new QPushButton(tab_coord);
    pushButton_select_all_table->setObjectName(QString::fromUtf8("pushButton_select_all_table"));
    pushButton_select_all_table->setGeometry(QRect(40, 40, 241, 25));
    tabWidget->addTab(tab_coord, QString());

    hboxLayout->addWidget(tabWidget);

    pymecavideo->setCentralWidget(centralwidget);
    menubar = new QMenuBar(pymecavideo);
    menubar->setObjectName(QString::fromUtf8("menubar"));
    menubar->setGeometry(QRect(0, 0, 673, 22));
    menuFichier = new QMenu(menubar);
    menuFichier->setObjectName(QString::fromUtf8("menuFichier"));
    menuAide = new QMenu(menubar);
    menuAide->setObjectName(QString::fromUtf8("menuAide"));
    menu_dition = new QMenu(menubar);
    menu_dition->setObjectName(QString::fromUtf8("menu_dition"));
    pymecavideo->setMenuBar(menubar);
    statusbar = new QStatusBar(pymecavideo);
    statusbar->setObjectName(QString::fromUtf8("statusbar"));
    statusbar->setGeometry(QRect(0, 653, 673, 22));
    pymecavideo->setStatusBar(statusbar);

    menubar->addAction(menuFichier->menuAction());
    menubar->addAction(menu_dition->menuAction());
    menubar->addAction(menuAide->menuAction());
    menuFichier->addAction(actionOuvrir_un_fichier);
    menuFichier->addAction(actionRouvrirMecavideo);
    menuFichier->addSeparator();
    menuFichier->addAction(actionCopier_dans_le_presse_papier);
    menuFichier->addAction(actionSaveData);
    menuFichier->addSeparator();
    menuFichier->addAction(actionQuitter);
    menuAide->addAction(actionAide);
    menuAide->addAction(actionExemples);
    menuAide->addSeparator();
    menuAide->addAction(action_propos);
    menu_dition->addAction(actionPreferences);

    retranslateUi(pymecavideo);

    tabWidget->setCurrentIndex(0);


    QMetaObject::connectSlotsByName(pymecavideo);
    } // setupUi

    void retranslateUi(QMainWindow *pymecavideo)
    {
    pymecavideo->setWindowTitle(QApplication::translate("pymecavideo", "PyMecaVideo, analyse m\303\251canique des vid\303\251os", 0, QApplication::UnicodeUTF8));
    actionOuvrir_un_fichier->setText(QApplication::translate("pymecavideo", "Ouvrir une vid\303\251o", 0, QApplication::UnicodeUTF8));
    actionAvanceimage->setText(QApplication::translate("pymecavideo", "avanceimage", 0, QApplication::UnicodeUTF8));
    actionReculeimage->setText(QApplication::translate("pymecavideo", "reculeimage", 0, QApplication::UnicodeUTF8));
    actionQuitter->setText(QApplication::translate("pymecavideo", "Quitter", 0, QApplication::UnicodeUTF8));
    actionSaveData->setText(QApplication::translate("pymecavideo", "Enregistrer les donn\303\251es", 0, QApplication::UnicodeUTF8));
    action_propos->setText(QApplication::translate("pymecavideo", "\303\200 propos", 0, QApplication::UnicodeUTF8));
    actionAide->setText(QApplication::translate("pymecavideo", "Aide", 0, QApplication::UnicodeUTF8));
    actionExemples->setText(QApplication::translate("pymecavideo", "Exemples ...", 0, QApplication::UnicodeUTF8));
    actionRouvrirMecavideo->setText(QApplication::translate("pymecavideo", "Rouvrir un fichier mecavid\303\251o", 0, QApplication::UnicodeUTF8));
    actionPreferences->setText(QApplication::translate("pymecavideo", "Pr\303\251f\303\251rences", 0, QApplication::UnicodeUTF8));
    actionCopier_dans_le_presse_papier->setText(QApplication::translate("pymecavideo", "copier dans le presse-papier", 0, QApplication::UnicodeUTF8));
    label->setText(QApplication::translate("pymecavideo", "Pas de vid\303\251os charg\303\251es", 0, QApplication::UnicodeUTF8));
    label_infos_image->setText(QApplication::translate("pymecavideo", "Bienvenue sur pymeca vid\303\251o, pas d'images charg\303\251e", 0, QApplication::UnicodeUTF8));
    Bouton_Echelle->setText(QApplication::translate("pymecavideo", "D\303\251finir l'\303\251chelle", 0, QApplication::UnicodeUTF8));
    label_numero_image->setText(QApplication::translate("pymecavideo", "Image n\302\260", 0, QApplication::UnicodeUTF8));
    label_2->setText(QApplication::translate("pymecavideo", "Nombre de points \303\240 \303\251tudier", 0, QApplication::UnicodeUTF8));
    echelleEdit->setText(QApplication::translate("pymecavideo", "ind\303\251f.", 0, QApplication::UnicodeUTF8));
    label_4->setText(QApplication::translate("pymecavideo", "px/m", 0, QApplication::UnicodeUTF8));
    Bouton_lance_capture->setText(QApplication::translate("pymecavideo", "D\303\251marrer l'acquisition", 0, QApplication::UnicodeUTF8));
    pushButton_reinit->setText(QApplication::translate("pymecavideo", "Tout r\303\251initialiser", 0, QApplication::UnicodeUTF8));

#ifndef QT_NO_TOOLTIP
    pushButton_defait->setToolTip(QApplication::translate("pymecavideo", "efface le point pr\303\251c\303\251dent", 0, QApplication::UnicodeUTF8));
#endif // QT_NO_TOOLTIP

    pushButton_defait->setText(QString());

#ifndef QT_NO_TOOLTIP
    pushButton_refait->setToolTip(QApplication::translate("pymecavideo", "r\303\251tablit le point suivant", 0, QApplication::UnicodeUTF8));
#endif // QT_NO_TOOLTIP

    pushButton_refait->setText(QString());
    tabWidget->setTabText(tabWidget->indexOf(tab_acq), QApplication::translate("pymecavideo", "Acquisition des donn\303\251es", 0, QApplication::UnicodeUTF8));
    label_3->setText(QString());
    label_7->setText(QApplication::translate("pymecavideo", "Origine du r\303\251f\303\251rentiel :", 0, QApplication::UnicodeUTF8));
    button_video->setText(QApplication::translate("pymecavideo", "Vid\303\251o calcul\303\251e", 0, QApplication::UnicodeUTF8));
    comboBox_fps->clear();
    comboBox_fps->insertItems(0, QStringList()
     << QApplication::translate("pymecavideo", "V. normale", 0, QApplication::UnicodeUTF8)
     << QApplication::translate("pymecavideo", "ralenti /2", 0, QApplication::UnicodeUTF8)
     << QApplication::translate("pymecavideo", "ralenti /4", 0, QApplication::UnicodeUTF8)
     << QApplication::translate("pymecavideo", "ralenti /8", 0, QApplication::UnicodeUTF8)
    );
    label_5->setText(QApplication::translate("pymecavideo", "\303\211chelle de vitesses :", 0, QApplication::UnicodeUTF8));
    label_6->setText(QApplication::translate("pymecavideo", "px pour 1 m/s", 0, QApplication::UnicodeUTF8));
    tabWidget->setTabText(tabWidget->indexOf(tab_traj), QApplication::translate("pymecavideo", "trajectoires et mesures", 0, QApplication::UnicodeUTF8));
    pushButton_select_all_table->setText(QApplication::translate("pymecavideo", "Copier les mesures dans le presse papier", 0, QApplication::UnicodeUTF8));
    tabWidget->setTabText(tabWidget->indexOf(tab_coord), QApplication::translate("pymecavideo", "Coordonn\303\251es", 0, QApplication::UnicodeUTF8));
    menuFichier->setTitle(QApplication::translate("pymecavideo", "Fichier", 0, QApplication::UnicodeUTF8));
    menuAide->setTitle(QApplication::translate("pymecavideo", "Aide", 0, QApplication::UnicodeUTF8));
    menu_dition->setTitle(QApplication::translate("pymecavideo", "\303\211dition", 0, QApplication::UnicodeUTF8));
    } // retranslateUi

};

namespace Ui {
    class pymecavideo: public Ui_pymecavideo {};
} // namespace Ui

QT_END_NAMESPACE

#endif // UI_PYMECAVIDEO_H
