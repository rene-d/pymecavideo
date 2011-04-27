// -*- coding: utf-8 -*-
// $Id$
///////////////////////////////////////////////////////////////////////
//
// Cadreur version 1.0
//
// a program to track moving points in a video frameset
// 
// Copyright (C) 2011 Georges Khaznadar <georgesk@ofset.org>
//
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with this program.  If not, see <http://www.gnu.org/licenses/>.
//
///////////////////////////////////////////////////////////////////////

#ifndef _REENTRANT
 #define _REENTRANT
#endif

#include <iostream> 
#include <cv.h>
#include <highgui.h>
#include <gdk/gdkx.h>
#include <gtk/gtkwidget.h>
#include <algorithm>
#include <sys/types.h>
#include<fcntl.h>


#include "cadreur.hpp"

using namespace std;

Cadreur::Cadreur(const char *afilename, const char *afifoname):
  end(false), fifoname(afifoname)
{
  cerr << "GRRRR création du Cadreur" << endl;
  fifo= new ifstream(afifoname, ifstream::in);
  cerr << "GRRRR fifo ouvert" << endl;
  filename=afilename;
  if (filename){
    windowname=filename;
  } else {
    windowname="unnamed.avi";
  }
  cvNamedWindow(filename,0);
  if (filename){
    film=cvCreateFileCapture(filename);
  } else {
    film=0;
  }
}

Cadreur::~Cadreur(){
  cvDestroyWindow(windowname);
  cvReleaseImage(&img);
  cvReleaseCapture(&film);
  unlink(fifoname);
  free(fifo);
}

#define BUFLEN 128

void Cadreur::watchFifo(){
  char buffer[BUFLEN], *token;
  fifo-> readsome(buffer, BUFLEN);
  token = strtok(buffer,"\n");
  while(token){
    cerr << "read " << token << endl;
    if (strcmp(token,"stop")==0) {
      end=true;
    }
    token= strtok(NULL,"\n");
  }
}

#define ESC 1048603

void Cadreur::Run(){
  if (film){
    while (img=cvQueryFrame(film)){
      cvShowImage(filename, img);
      //int c = cvWaitKey(int(1000/fps()));
      int c = cvWaitKey(25);
      if (c == ESC) break;
    }
  }  
}

void Cadreur::Loop(int max){
  cerr << "Dans loop, film = " << film <<endl;
  if (film){
    while (! end && max != 0){
      Restart();
      if (max > 0) max --;
      while (queryFrame()){
	showImage();
	watchFifo();
	int c = cvWaitKey(100);
	if (c == ESC) {end=true; break;}
      }
    }
  }  
}

bool Cadreur::queryFrame(){
  img=cvQueryFrame(film);
  return bool(img);
}

void Cadreur::showImage(){
  cvShowImage(windowname,img);
}

void Cadreur::Restart(){
  if (film){
    cvSetCaptureProperty(film,CV_CAP_PROP_POS_FRAMES,0);
  }  
}

float Cadreur::fps(){
  return cvGetCaptureProperty(film, CV_CAP_PROP_FPS);
}

int Cadreur::count(){
  return int(cvGetCaptureProperty(film, CV_CAP_PROP_FRAME_COUNT));
}

int Cadreur::w(){
  return int(cvGetCaptureProperty(film, CV_CAP_PROP_FRAME_WIDTH));
}

int Cadreur::h(){
  return int(cvGetCaptureProperty(film, CV_CAP_PROP_FRAME_HEIGHT));
}

float Cadreur::currentTime(){
  return cvGetCaptureProperty(film, CV_CAP_PROP_POS_MSEC)/1000;
}

string Cadreur::fourcc(){
  double f=cvGetCaptureProperty(film, CV_CAP_PROP_FOURCC);
  return string((char *) (&f));
}


// XID winxid=GDK_WINDOW_XID(GTK_WIDGET(drawing)->window)

unsigned long Cadreur::Wid(){
  // get the Window Id of the toplevel window containg OpenCV's image
  return GDK_WINDOW_XID(gdk_window_get_toplevel(GTK_WIDGET(cvGetWindowHandle(windowname))->window));
}


CadreurDynamique::~CadreurDynamique() {
  delete[] spot;
  cvReleaseMat(&iSub);
}

CadreurDynamique::CadreurDynamique(const char *afilename,
				   const char* afifoname, 
				   const kineFunc func,
				   int beginFrame,
				   int endFrame) :
  Cadreur(afilename, afifoname), 
  kine(func), 
  bf(beginFrame), 
  ef(endFrame)
{
  spot=new vector<Coord>;
  vector<int> *left = new vector<int>;
  vector<int> *right = new vector<int>;
  vector<int> *top = new vector<int>;
  vector<int> *bottom = new vector<int>;
  vector<int>::iterator min;
  int minleft, minright, mintop, minbottom; // minimum margins
  // iterates the timespan of interest
  cerr << "Dans CadreurDynamique, avant de calculer le cadre" << endl;
  if (func){ // don't iterate on points if func is not defined!
    for (int i=bf; i < ef; i++){
      // fills the spot vector at each date
      float t=i/fps();
      Coord p=kine(t);
      spot->push_back(p);
      // evaluate the margin vectors
      left->push_back(p.x());
      top->push_back(p.y());
      right->push_back(w()-p.x());
      bottom->push_back(h()-p.y());
    }
    // get the minimum margins
    minleft = * min_element (left->begin(), left->end());
    minright = * min_element (right->begin(), right->end());
    mintop = * min_element (top->begin(), top->end());
    minbottom = * min_element (bottom->begin(), bottom->end());
    // evaluates the offset and the region of interest's width and height
    offset=Coord(minleft,mintop)-(*spot)[0];
    roi.width=minright-minleft;
    roi.height=minbottom-mintop;
    free(left); free(right); free(top); free(bottom);
  } else {
    for (int i=bf; i < ef; i++){
      spot->push_back(Coord(1,1));
    }
    roi.width=w()-2;
    roi.height=h()-2;
    offset=Coord(0,0);
  }
  // sample the first image, fixes possible erroneous extremities
  cerr << "Dans CadreurDynamique, le cadre est calculé" << endl;
  img=cvQueryFrame(film);
  if (bf <0) bf=0;
  if (ef > count()) ef=count();
  Restart();
  // creates the matrix of the clipped frame
  iSub = cvCreateMat(roi.width, roi.height, img->depth);
}


void CadreurDynamique::Restart(){
  if (film){
    cvSetCaptureProperty(film,CV_CAP_PROP_POS_FRAMES,bf);
    wf=bf;
  }  
}

bool CadreurDynamique::queryFrame(){
  if (wf < ef){
    img=cvQueryFrame(film);
    wf++;
    return true;
  } else {
    return false;
  }
}

void CadreurDynamique::showImage(){
  Coord p=(*spot)[wf];
  roi.x=p.x(); roi.y=p.y();
  cvGetSubRect(img,iSub,roi);
  cvShowImage(windowname,iSub);
}

const Coord pointFixe(float t);
const Coord pointFixe(float t){
  return Coord(50,50);
}

const Coord pointPasFixe(float t);
const Coord pointPasFixe(float t){
  return Coord(50+60*t,50+60*t);
}

void error(const char *msg){
  perror(msg);
  exit(1);
}

int main (int argc, char *argv[]){
  Cadreur * cadreur;
  if (argc>2){
    cadreur = new CadreurDynamique(argv[1], argv[2]);
  } else {
    cerr << "the name of an AVI file is required\n";
    return 1;
  }
  cadreur->Loop(-1);
  return 0;
}
