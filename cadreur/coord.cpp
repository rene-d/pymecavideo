// -*- coding: utf-8 -*-
// $Id$
///////////////////////////////////////////////////////////////////////
//
// coord.cpp is part of the package Cadreur version 1.0
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

#include "coord.hpp"

using namespace std;

Coord operator+ (const Coord p1, const Coord p2){
  Coord result;
  result.val[0]=p1.val[0]+p2.val[0];
  result.val[1]=p1.val[1]+p2.val[1];
  return result;
}

Coord operator- (const Coord p1, const Coord p2){
  Coord result;
  result.val[0]=p1.val[0]-p2.val[0];
  result.val[1]=p1.val[1]-p2.val[1];
  return result;
}

float operator* (const Coord p1, const Coord p2){
  return p1.val[0]*p2.val[0]+p1.val[1]*p2.val[1];
}

Coord operator* (const float f, const Coord p1){
  Coord result;
  result.val[0]=f*p1.val[0];
  result.val[1]=f*p1.val[1];
  return result;
}

ostream& operator << (ostream& o, const Coord p){
  return o << "Coord(" << p.val[0] << "," << p.val[1]<<")";
}
