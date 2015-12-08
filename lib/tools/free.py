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
import struct
from ctypes import create_string_buffer

class PencilTool(DragAndDropTool):
    points = None
    name = 'Pencil'

    def begin(self, x, y,button):
        DragAndDropTool.begin(self, x, y,button)
        self.points = list()
        self.points.insert(len(self.points), (x, y))

    def move(self, x, y):
        if self.mode == self.DRAWING:
            self.points.insert(len(self.points), (x, y))

    def end(self, x, y):
        self.points.insert(len(self.points), (x, y))

    def draw(self, context):
        if self.mode == self.READY:
            return

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

class EraserTool(PencilTool):
    name = 'Eraser'

    def begin(self, x, y,button):
        super(EraserTool, self).begin(x, y,button)
        #start line
        self.points.insert(len(self.points), (x, y+4))
        self.points.insert(len(self.points), (x, y-4))
        self.points.insert(len(self.points), (x, y))
    
    def draw(self, context):
        if self.mode == self.READY:
            return

        context.set_antialias(cairo.ANTIALIAS_NONE)
        context.set_line_cap(cairo.LINE_CAP_BUTT)
        context.set_line_join(cairo.LINE_JOIN_MITER)
        context.move_to(self.initial_x, self.initial_y)
        context.set_line_width(8)
        self.use_secondary_color(context,self.m_button)
        for point in self.points:
            context.line_to(point[0], point[1])
        context.set_operator(cairo.OPERATOR_SOURCE)
        context.stroke()

class PaintbrushTool(PencilTool):
    name = 'PaintBrush'
    def draw(self, context):
        if self.mode == self.READY:
            return

        context.set_line_cap(cairo.LINE_CAP_ROUND)
        context.set_line_join(cairo.LINE_JOIN_ROUND)
        context.move_to(self.initial_x, self.initial_y)
        context.set_line_width(8)
        self.use_primary_color(context,self.m_button)
        for point in self.points:
            context.line_to(point[0], point[1])
        context.stroke()
        
class AirBrushTool(PencilTool):
    name = 'AirBrush'
    Brush = None
    Brush_off = None
    Brush_rep = None
    scale = None

    
    def begin(self, x, y,button):
        super(AirBrushTool, self).begin(x, y,button)
        self.Brush = cairo.ImageSurface.create_from_png("Brushes/AirBrush.png")
        if button==3:
            pc=self.secondary
        else:
            pc = self.primary
        a = pc.get_alpha()
        r = pc.get_red()
        g = pc.get_green()
        b = pc.get_blue()
        Brush_w = self.Brush.get_width()
        self.Brush_off =  Brush_w/2.0
        self.Brush_rep =  Brush_w/10
        data = self.Brush.get_data()
        for n in range(Brush_w**2):
            al_bin = data[n*4+3]
            al_int = struct.unpack_from(str(1)+'B',al_bin)
            al = float(al_int[0])/255
            px = create_string_buffer(4)
            alph = al*a
            struct.pack_into(str(4)+'B',px,0,int(alph*b*255), int(alph*g*255),int(alph*r*255), int(alph*255))
            data[n*4:(n+1)*4] = px
        self.scale =  self.canvas.airbrush_width/Brush_w
        
        
    def move(self, x, y):
        if self.mode == self.DRAWING:
            xd = x-self.points[-1][0]
            yd = y-self.points[-1][1]
            dist = (((xd)**2 + (yd)**2)**0.5)/self.scale
            if dist>self.Brush_rep:
                n = int(dist/self.Brush_rep)
                xd /= n
                yd /= n
                x = self.points[-1][0]
                y = self.points[-1][1]
                self.points = list()
                for i in range(n):
                    x+=xd
                    y+=yd
                    self.points.insert(len(self.points), (x, y))
            else:
                self.points = list()
                self.points.insert(len(self.points), (x, y))    
    
    def draw(self, context):
        if self.mode == self.READY:
            return
        context.scale(self.scale,self.scale)
        for n in range(len(self.points)):
            context.set_source_surface(self.Brush, (self.points[n][0])/self.scale-self.Brush_off, (self.points[n][1])/self.scale-self.Brush_off)
            context.paint()
