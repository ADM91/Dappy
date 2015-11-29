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


import gtk
from lib.graphics.rgbacolor import RGBAColor
from ctypes import create_string_buffer

# Class
# ==============================================================================
class Tool(gtk.Object):
    READY = 0
    DRAWING = 1
    EDITING = 2
    name = 'NotSet'
    Draw2Overlay = False;

    CURSOR = gtk.gdk.Cursor(gtk.gdk.ARROW)

    def __init__(self, canvas):
        self.canvas = canvas
        self.primary = RGBAColor(0, 0, 0)
        self.secondary = RGBAColor(1, 1, 1)
        self.mode = self.READY

    def move(self, x, y): pass

    def select(self):
        self.canvas.window.set_cursor(self.CURSOR)

    def begin(self, x, y,button):
        self.canvas.clear_overlay()
        self.canvas.update_undo_buffer(1)
        self.mode = self.DRAWING

    def end(self, x, y):
        self.mode = self.EDITING

    def draw(self, context): pass

    def __use_color(self, context, color):
        context.set_source_rgba(color.get_red(), color.get_green(),
           color.get_blue(), color.get_alpha())

    def __use_no_color(self, context):
        context.set_source_rgba(0,0,0,0)

    def use_primary_color(self, context, button=1):
        if button==3:
            self.__use_color(context, self.secondary)
        else:
            self.__use_color(context, self.primary)

    def use_secondary_color(self, context, button=1):
        if button==3:
            self.__use_color(context, self.primary)
        else:
            self.__use_color(context, self.secondary)
    
    def use_fill_color(self, context, button=1):
        if self.canvas.fig_fill_type==0:
            self.use_secondary_color(context, button)
        elif self.canvas.fig_fill_type==1:
            self.use_primary_color(context, button)
        else:
            self.__use_no_color(context)

    def set_primary_color(self, color):
        self.primary = color

    def set_secondary_color(self, color):
        self.secondary = color

    def commit(self):
        self.mode = self.DRAWING
        self.canvas.print_tool()
        self.mode = self.READY


# Class
# ==============================================================================
class DragAndDropTool(Tool):
    CURSOR = gtk.gdk.Cursor(gtk.gdk.CROSSHAIR)

    initial_x = 0
    initial_y = 0
    final_x = 0
    final_y = 0
    
    m_button = None

    def begin(self, x, y,button):
        Tool.begin(self, x, y,button)
        self.initial_x = x
        self.initial_y = y
        self.final_x = x
        self.final_y = y
        self.m_button=button


    def end(self, x, y):
        Tool.end(self, x, y)
        self.final_x = x
        self.final_y = y


    def move(self, x, y):
        self.final_x = x
        self.final_y = y


# Class
# ==============================================================================
class BothScalingTool(Tool):
    CURSOR = gtk.gdk.Cursor(gtk.gdk.BOTTOM_RIGHT_CORNER)
    name = 'BothScale'

    def begin(self, x, y,button):
        Tool.begin(self, x, y,button)    
    
    def move(self, x, y):
        self.canvas.set_size(int(x), int(y))


# Class
# ==============================================================================
class HorizontalScalingTool(Tool):
    CURSOR = gtk.gdk.Cursor(gtk.gdk.RIGHT_SIDE)
    name = 'HorScale'

    def begin(self, x, y,button):
        Tool.begin(self, x, y,button)

    def move(self, x, y):
        self.canvas.set_size(int(x), self.canvas.get_height())


# Class
# ==============================================================================
class VerticalScalingTool(Tool):
    CURSOR = gtk.gdk.Cursor(gtk.gdk.BOTTOM_SIDE)
    name = 'VertScale'

    def begin(self, x, y,button):
        Tool.begin(self, x, y,button)

    def move(self, x, y):
        self.canvas.set_size(self.canvas.get_width(), int(y))
