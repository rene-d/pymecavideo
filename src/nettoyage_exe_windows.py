import os
dossier_du_build = "build"

a_enlever = {}
#rep : "lib/cv2"
# fichiers :


a_enlever["lib/cv2"] = ["opencv_videoio_ffmpeg451_64.dll", "python39.dll"]

#rep : "lib\PyQt5\Qt\bin"
# fichiers :

a_enlever["lib/PyQt6/Qt6/bin"] = [
    "d3dcompiler_47.dll",
    "Qt6QmlModels.dll",
    "libcrypto-1_1-x64.dll",
    "Qt6Bluetooth.dll",
    "Qt6Quick.dll",
    "libeay32.dll",
    "Qt6DBus.dll",
    "Qt6QuickParticles.dll",
    "libGLESv2.dll",
    "Qt6Designer.dll",
    "Qt6QuickTemplates2.dll",
    "libssl-1_1-x64.dll",
    "Qt6Network.dll",
    "Qt6XmlPatterns.dll",
    "opengl32sw.dll",
    "Qt6Qml.dll",
    "QtWidgets.dll",
    "QtCore.dll",
    "Qt6Core.dll",
    "Qt6Pdf.dll",
    "Qt6ShaderTools.dll",
    "Qt6Quick3DRuntimeRender.dll",
]



a_enlever["lib/PyQt5/Qt5/bin"] = [
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
    "Qt5Location.dll",
]

#rep : "lib\PyQt5\Qt5\plugins"
a_enlever["lib/PyQt5/Qt5/plugins"] = [
    "printsupport",
    "sensorgestures",
    "sqldrivers",
    "webview",
    "sceneparsers",
    "sensors",
    "texttospeech"]

a_enlever["lib/PyQt5/Qt5/plugins/imageformats"] = [
    "Qt5Core.dll",
    "Qt5Gui.dll",
    "Qt5Widgets.dll",
    "Qt5Quick.dll",
    "Qt5Qml.dll",
    "Qt5Network.dll"]

a_enlever["lib/PyQt5/Qt5/plugins/platforms"] = [
    "Qt5Core.dll",
    "Qt5Gui.dll",
    "Qt5Widgets.dll",
    "Qt5Quick.dll",
    "Qt5Qml.dll",
    "Qt5Network.dll"]

a_enlever["lib/PyQt5/Qt5/plugins/style"] = [
    "Qt5Core.dll",
    "Qt5Gui.dll",
    "Qt5Widgets.dll",
    "Qt5Quick.dll",
    "Qt5Qml.dll",
    "Qt5Network.dll"]

#rep : "lib\PyQt6"
a_enlever["lib/PyQt6"] = [
    "python310.dll",
    # "qt5gui.dll",
    # "qt5widgets.dll"
    ]
    
#rep : "lib\numpy\core"
a_enlever["lib/numpy/core"] = [
    "python310.dll"]
 
a_enlever["lib/numpy/fft"] = [
    "python310.dll"]
a_enlever["lib/numpy/linalg"] = [
    "python310.dll"]
a_enlever["lib/numpy/random"] = [
    "python310.dll"]
a_enlever["lib/pandas/_libs"] = [
    "python310.dll"]
a_enlever["lib/pandas/_libs/tslibs"] = [
    "python310.dll"]
a_enlever["lib/pandas/_libs/window"] = [
    "python310.dll"]
a_enlever["lib/pandas/io/sas"] = [
    "python310.dll"]
a_enlever["lib"] = [
    "python310.dll"]

# a modifier
os.chdir(dossier_du_build)
for rep, dossier_fichier in a_enlever.items():

    for fichier_ in dossier_fichier:
        print(f"effacement de {fichier_}, dans {rep}")
        try:
            os.remove(os.path.join(rep, fichier_))

        except FileNotFoundError :
            print("%s non trouvé. Déjà effacé ?"%(os.path.join(rep, fichier_)))
        except: #c'est un dossier
            print("c'est un dossier")
            for fichier_ in dossier_fichier:
                for fichier in os.listdir(os.path.join(rep, fichier_)):
                    os.remove(os.path.join(rep, fichier_, fichier))
                os.rmdir(os.path.join(rep, fichier_))
