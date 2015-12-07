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
import cairo
import gobject
import math

from rgbacolor import RGBAColor

class ColorCell(gtk.DrawingArea):
    WIDTH = 25
    HEIGHT = 20
    ASS = 7

    def __init__(self, red=0, green=0, blue=0, alpha=1):
        super(ColorCell, self).__init__()
        self.set_size_request(self.WIDTH, self.HEIGHT)

        self.gloss = cairo.ImageSurface.create_from_png("GUI/glossy-color.png")
        self.color = RGBAColor(red, green, blue, alpha)

        self.add_events(gtk.gdk.BUTTON_PRESS_MASK | gtk.gdk.SCROLL)
        self.connect("button-press-event", self.clicked)
        self.connect("expose-event", self.expose)


    def expose(self, widget, event):
        context = widget.window.cairo_create()

        context.rectangle(0, 0, self.WIDTH, self.HEIGHT)
        context.clip()

        context.rectangle(0, 0, self.WIDTH, self.HEIGHT)
        context.set_source_rgb(0.4, 0.4, 0.4)
        context.fill()

        context.set_source_rgb(0.6, 0.6, 0.6)
        for i in range(int(self.WIDTH/self.ASS)+1):
            for j in range(int(self.HEIGHT/self.ASS)+1):
                if i%2 == 0 and j%2 == 0:
                    context.rectangle(i*self.ASS, j*self.ASS, self.ASS, self.ASS)
                    context.fill()
                elif i%2 != 0 and j%2 != 0:
                    context.rectangle(i*self.ASS, j*self.ASS, self.ASS, self.ASS)
                    context.fill()

        context.rectangle(0, 0, self.WIDTH, self.HEIGHT)
        context.set_source_rgba(self.color.get_red(), self.color.get_green(),
           self.color.get_blue(), self.color.get_alpha())
        context.fill()

        context.set_source_surface(self.gloss)
        context.paint()


    def swap_buffers(self):
        rect = gtk.gdk.Rectangle(0, 0, self.WIDTH, self.HEIGHT)
        self.window.invalidate_rect(rect, True)


    def set_color(self, color):
        self.color = color

        try:
            rect = gtk.gdk.Rectangle(0, 0, self.WIDTH, self.HEIGHT)
            self.window.invalidate_rect(rect, True)
        except:
            pass


    def get_color(self):
        return self.color.copy()


    def modify_color(self, color):
        csd = gtk.ColorSelectionDialog("Choose a color")
        csd.set_modal(True)
        cs = csd.get_color_selection()
        cs.set_property("current-color", self.color.to_gtk_color())
        ok = csd.run()
        if ok == gtk.RESPONSE_OK:
            self.set_color(RGBAColor.create_from_gtk_color(cs.get_current_color()))
        csd.destroy()


    def clicked(self, widget, event):
        if event.type == gtk.gdk._2BUTTON_PRESS:
            self.modify_color(widget)

        self.emit("color-changed-event", event)


    def to_string(self):
        return "ColorCell: " + self.color.to_string()




# Registering signals
gobject.signal_new("color-changed-event", ColorCell, gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,))
