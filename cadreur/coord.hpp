// -*- coding: utf-8 -*-
// $Id$
///////////////////////////////////////////////////////////////////////
//
// coord.hpp is part of the package Cadreur version 1.0
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

#include <math.h>
#include <iostream> 

using namespace std;

class Coord {
protected:
  float val[2];
public:
  inline Coord(float x=0, float y=0) {
    val[0]=x; val[1]=y;
  }
  inline float norme(){
    return sqrt((*this) * (*this));
  }
  inline float x(){
    return val[0];
  }
  inline float y(){
    return val[1];
  }
  friend  Coord operator+ (const Coord p1, const Coord p2);
  friend  Coord operator- (const Coord p1, const Coord p2);
  friend  float operator* (const Coord p1, const Coord p2);
  friend  Coord operator* (const float f, const Coord p1);
  friend ostream& operator << (ostream& o, const Coord p);
};

