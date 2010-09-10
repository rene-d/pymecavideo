# -*- coding: utf-8 -*-
##installation script-
import subprocess, os
cmd2 = subprocess.Popen(["python","setup.py","install"],stdout=subprocess.PIPE)
cmd2.poll()
cmd2.wait()
output=cmd2.stdout.readlines()
for ligne in output :
    if "site-packages" in ligne :
        liste = ligne.split()
        for i in liste : 
            if "site-packages" in i :
                chemin_l = os.path.split(i)
                for j in chemin_l:
                    if "site-packages" in j:
                        install_dir = j
                        print "pymecavideo installé à", install_dir
if install_dir :
    print "OK"
    cmd3 = subprocess.Popen(["cp","-Rp","data",os.path.join(install_dir,"pymecavideo")],stdout=subprocess.PIPE)
    cmd3.poll()
    cmd3.wait()
    print cmd3.stdout.readlines()
    cmd4 = subprocess.Popen(["chmod","755",os.path.join(install_dir,"pymecavideo/data")],stdout=subprocess.PIPE)
    cmd4.poll()
    cmd4.wait()
    print cmd4.stdout.readlines()
    