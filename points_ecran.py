#-*- coding: utf-8 -*-

licence={}
licence['en']="""
    file points_ecran.py

    this file is part of pymecavideo, 
    a program to track moving points in a video frameset
    
    Copyright (C) 2009 Georges Khaznadar <georgesk@ofset.org>

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

class PointEcran:
    def __init__(self):
        self.dic={}
    def addPoint(self, key, point_label_trajectoire, point_label_video, point_ID,p):
        self.dic[key]=[point_label_trajectoire, point_label_video, point_ID,p]
        return self.dic[key]
    def isEmpty(self):
        return len(self.dic.keys())==0
    def pointTraj(self,key,value=None):
        if value != None:
            self.dic[key][0]=value
        return self.dic[key][0]
    def pointVid(self,key):
        return self.dic[key][1]
    def pointID(self,key):
        return self.dic[key][2]
    def pointP(self,key):
        return self.dic[key][3]
    def keys(self):
        return self.dic.keys()
    def length(self):
        return len(self.dic)
    
