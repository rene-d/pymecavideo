import os
dossier_du_build = "build"

a_enlever = {}
#rep : "lib/cv2"
#fichiers :


a_enlever["lib/cv2"] = ["opencv_videoio_ffmpeg412_64.dll", "python38.dll"]

#rep : "lib\PyQt5\Qt\bin"
#fichiers :

a_enlever["lib/PyQt5/Qt/bin"] = [
"d3dcompiler_47.dll",
"Qt5QmlModels.dll",
"libcrypto-1_1-x64.dll",
"Qt5Bluetooth.dll",
"Qt5Quick.dll",
"libeay32.dll",
"Qt5DBus.dll",
"Qt5QuickParticles.dll",
"libGLESv2.dll",
"Qt5Designer.dll",
"Qt5QuickTemplates2.dll",
"libssl-1_1-x64.dll",
"Qt5Network.dll",
"Qt5XmlPatterns.dll",
"opengl32sw.dll",
"Qt5Qml.dll",
]

#rep : "lib\PyQt5\Qt\plugins"
a_enlever["lib/PyQt5/Qt/plugins"] = [
"printsupport",
"sensorgestures",
"sqldrivers",
"webview",
"sceneparsers",
"sensors",
"texttospeech"]

#rep : "lib\PyQt5"
a_enlever ["lib/PyQt5"] = [
"qt5core.dll", 
"qt5gui.dll",
"qt5widgets.dll"]

#####a modifier
os.chdir (dossier_du_build)
for rep, dossier_fichier in a_enlever.items():
    try : 
        for fichier_ in dossier_fichier :
            os.remove(os.path.join(rep, fichier_))
    except : 
        for fichier_ in dossier_fichier :
            for fichier in os.listdir(os.path.join(rep, fichier_)) : 
                os.remove(os.path.join(rep, fichier_,fichier))
            os.rmdir(os.path.join(rep, fichier_))






