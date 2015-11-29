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
import math
from generic import DragAndDropTool

class RectangleTool(DragAndDropTool):
    name = 'Rectangle'
    def draw(self, context):
        if self.mode == self.READY:
            return

        w = self.final_x - self.initial_x
        h = self.final_y - self.initial_y
        context.rectangle(self.initial_x, self.initial_y, w, h)
        self.use_fill_color(context,self.m_button)
        context.fill_preserve()
        self.use_primary_color(context,self.m_button)
        context.stroke()


class RoundedRectangleTool(DragAndDropTool):
    name = 'RoundedRectangle'
    def draw(self, context):
        if self.mode == self.READY:
            return

        w = self.final_x - self.initial_x
        h = self.final_y - self.initial_y
        context.rectangle(self.initial_x, self.initial_y, w, h)
        self.use_fill_color(context,self.m_button)
        context.fill_preserve()
        self.use_primary_color(context,self.m_button)
        context.save()
        context.set_line_width(5)
        context.set_line_join(cairo.LINE_JOIN_ROUND)
        context.stroke()
        context.restore()


class EllipseTool(DragAndDropTool):
    name = 'Ellipse'
    def draw(self, context):
        if self.mode == self.READY:
            return

        w = self.final_x - self.initial_x
        h = self.final_y - self.initial_y
        
        if w!=0 and h !=0:
            context.save()
            context.translate(self.initial_x + w/2., self.initial_y + h/2.)
            context.scale(w/2., h/2.)
            context.arc(0., 0., 1., 0., 2 * math.pi)
            self.use_fill_color(context,self.m_button)
            context.fill_preserve()
            context.restore()
            if self.m_button==3:
                self.use_secondary_color(context)
            else:
                self.use_primary_color(context)
            #context.set_antialias(cairo.ANTIALIAS_NONE)
        else:
            self.use_primary_color(context,self.m_button)
            context.set_antialias(cairo.ANTIALIAS_NONE)
            context.move_to(self.initial_x, self.initial_y)
            context.line_to(self.final_x, self.final_y)
        context.stroke()

class RectangleSelectTool(DragAndDropTool):
    name = 'RectSelect'
    Draw2Overlay = True;

    def begin(self, x, y,button):
        self.canvas.clear_overlay()
        #don't update undo buffer
        self.mode = self.DRAWING 
        self.initial_x = x
        self.initial_y = y
        self.final_x = x
        self.final_y = y
    
    def draw(self,context):
        if self.mode == self.READY:
            return
        context.set_operator(cairo.OPERATOR_SOURCE)
        context.set_line_width(1)
        context.set_antialias(cairo.ANTIALIAS_NONE)
        context.rectangle(0, 0, self.canvas.width, self.canvas.height)
        context.set_source_rgba(0, 0, 0, 0)
        context.fill()
        context.set_operator(cairo.OPERATOR_OVER)
        w = self.final_x - self.initial_x
        h = self.final_y - self.initial_y
        context.rectangle(self.initial_x, self.initial_y, w, h)
        context.set_dash((5,5))
        context.set_source_rgba(0,0,1,1)
        context.stroke()
        context.rectangle(self.initial_x, self.initial_y, w, h)
        context.set_dash((5,5),5)
        context.set_source_rgba(1,1,0,1)
        context.stroke()
        
    def commit(self):
        self.mode = self.READY
        self.canvas.select_active = True
        self.canvas.select_xp = [self.initial_x,self.initial_x,self.final_x,self.final_x]
        self.canvas.select_yp = [self.initial_y,self.final_y,self.initial_y,self.final_y]