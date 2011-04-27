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

#ifndef CADREUR_HPP
#define CADREUR_HPP

#include "coord.hpp"

using namespace std;

// functions of the time which give coordinates
typedef const Coord (*kineFunc) (float);

class Cadreur {
protected:
  const char *filename, * windowname;
  IplImage * img;
  CvCapture * film;
public:
  Cadreur(const char *afilename = 0);
  ~Cadreur();
  void Run();
  virtual void Loop(int max=-1);
  virtual void Restart();
  float fps();
  int count();
  int w();
  int h();
  float currentTime();
  string fourcc();
  unsigned long Wid();
};

class CadreurDynamique : public Cadreur {
protected:
  const kineFunc kine;   // the function which gives the point to track
  int bf, ef;            // begin and end frames; 
  //the end frame is beyond the last frame to watch. 
  //For example if there is one sigle frame, bf==0 and ef==1.
  int wf;                // the watched frame
  vector<Coord> * spot;  // the point to track
  Coord offset;          // the offset between spot 
  // and top-left corner of the clipping frame
  CvMat *iSub;           // a matrix to access the subImage
  CvRect roi;            // frame's rectangle of interest
public:
  CadreurDynamique(const char *afilename = 0, 
		   const kineFunc func=0,
		   int beginFrame=0,
		   int endFrame=1);
  ~CadreurDynamique();
  virtual void Loop(int max=-1); // redefined in the subclass
  virtual void Restart();        // redefined in the subclass
  bool queryFrame();     // queries a frame not necessarily beginning at zero
  void showImage();      // shows a clipped image
};

#endif // CADREUR_HPP
