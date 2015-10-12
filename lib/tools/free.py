#    This file is part of Dappy - Draw And Paint in Python
#    Copyright (C) 2015 Julian Stirling
#    
#    Dappy was forked from Painthon, listed on Google code as GPL v2, 
#    copyright holder unknown.
#    
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#    
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>


import cairo
from generic import DragAndDropTool

class PencilTool(DragAndDropTool):
    points = None
    name = 'Pencil'

    def begin(self, x, y,button):
        self.m_button=button
        DragAndDropTool.begin(self, x, y,button)
        self.points = list()


    def move(self, x, y):
        if self.mode == self.DRAWING:
            self.points.insert(len(self.points), (x, y))


    def end(self, x, y):
        self.points.insert(len(self.points), (x, y))


    def draw(self, context):
        if self.mode == self.READY:
            return

        context.save()
        context.set_antialias(cairo.ANTIALIAS_NONE)
        context.set_line_cap(cairo.LINE_CAP_ROUND)
        context.set_line_join(cairo.LINE_JOIN_ROUND)
        context.move_to(self.initial_x, self.initial_y)
        
        if self.m_button==3:
            self.use_secondary_color(context)
        else:
            self.use_primary_color(context)
        
        for point in self.points:
            context.line_to(point[0], point[1])
        context.stroke()

        context.restore()



class EraserTool(PencilTool):
    name = 'Eraser';
    def draw(self, context):
        if self.mode == self.READY:
            return

        context.save()

        context.set_antialias(cairo.ANTIALIAS_NONE)
        context.set_line_cap(cairo.LINE_CAP_SQUARE)
        context.set_line_join(cairo.LINE_JOIN_MITER)
        context.move_to(self.initial_x, self.initial_y)
        context.set_line_width(8)
        if self.m_button==3:
            self.use_primary_color(context)
        else:
            self.use_secondary_color(context)
        for point in self.points:
            context.line_to(point[0], point[1])
        context.set_operator(cairo.OPERATOR_SOURCE)
        context.stroke()

        context.restore()


class PaintbrushTool(PencilTool):
    name = 'PaintBrush';
    def draw(self, context):
        if self.mode == self.READY:
            return

        context.save()

        context.set_line_cap(cairo.LINE_CAP_ROUND)
        context.set_line_join(cairo.LINE_JOIN_ROUND)
        context.move_to(self.initial_x, self.initial_y)
        context.set_line_width(8)
        if self.m_button==3:
            self.use_secondary_color(context)
        else:
            self.use_primary_color(context)
        for point in self.points:
            context.line_to(point[0], point[1])
        context.stroke()

        context.restore()
