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

class ColorCell(gtk.DrawingArea):
    WIDTH = 25
    HEIGHT = 20

    def __init__(self, red=0, green=0, blue=0, alpha=1,HSV=False):
        super(ColorCell, self).__init__()
        self.set_size_request(self.WIDTH, self.HEIGHT)

        self.gloss = cairo.ImageSurface.create_from_png("GUI/glossy-color.png")
        self.color = RGBAColor(red, green, blue, alpha)
        if HSV: #if HSV change color values: r=hue,g=sat,b=val
            self.color.set_from_hsv(red, green, blue, alpha)

        self.add_events(gtk.gdk.BUTTON_PRESS_MASK | gtk.gdk.SCROLL)
        self.connect("button-press-event", self.clicked)
        self.connect("expose-event", self.expose)

    def expose(self, widget, event):
        context = widget.window.cairo_create()
        context.rectangle(0, 0, self.WIDTH, self.HEIGHT)
        context.clip()
        self.alpha_pattern = cairo.SurfacePattern(cairo.ImageSurface.create_from_png("GUI/alpha-pattern.png"))
        self.alpha_pattern.set_extend(cairo.EXTEND_REPEAT)
        context.set_source(self.alpha_pattern)
        context.paint()
        context.rectangle(0, 0, self.WIDTH, self.HEIGHT)
        context.set_source_rgba(self.color.get_red(), self.color.get_green(),self.color.get_blue(), self.color.get_alpha())
        context.fill()
        context.set_source_surface(self.gloss)
        context.paint()

    def swap_buffers(self):
        try:
            rect = gtk.gdk.Rectangle(0, 0, self.WIDTH, self.HEIGHT)
            self.window.invalidate_rect(rect, True)
        except:
            pass

    def set_color(self, color):
        self.color = color
        self.swap_buffers()

    def set_color_vals(self,color):
        self.color.set_color_vals(color)
        self.swap_buffers()

    def set_alpha(self,alpha):
        self.color.set_alpha(alpha)
        self.swap_buffers()

    def set_rgba(self, red, green, blue, alpha):
        self.color.set_rgba(red, green, blue, alpha)
        self.swap_buffers()

    def get_color(self):
        return self.color.copy()

    def modify_color(self):
        csd = gtk.ColorSelectionDialog("Choose a color")
        csd.set_modal(True)
        cs = csd.get_color_selection()
        cs.set_property("current-color", self.color.to_gtk_color())
        ok = csd.run()
        print self
        if ok == gtk.RESPONSE_OK:
            self.color.set_from_gtk_color(cs.get_current_color())
            self.swap_buffers()
        csd.destroy()

    def clicked(self, widget, event):
        if event.type == gtk.gdk._2BUTTON_PRESS:
            self.modify_color()
            print self
            print widget
        self.emit("color-changed-event", event)

class RGBAColor:

    def __init__(self, red=0, green=0, blue=0, alpha=1):
        self.set_rgba(red, green, blue, alpha)

    def get_red(self):
        return self.red

    def get_green(self):
        return self.green

    def get_blue(self):
        return self.blue

    def get_alpha(self):
        return self.alpha

    def set_red(self, red):
        self.red = max(min(red, 1), 0)

    def set_green(self, green):
        self.green = max(min(green, 1), 0)

    def set_blue(self, blue):
        self.blue = max(min(blue, 1), 0)

    def set_alpha(self, alpha):
        self.alpha = max(min(alpha, 1), 0)

    def set_rgba(self, red, green, blue, alpha):
        self.set_red(red)
        self.set_green(green)
        self.set_blue(blue)
        self.set_alpha(alpha)

    def set_color_vals(self,color):
        self.red = color.get_red()
        self.green = color.get_green()
        self.blue = color.get_blue()
        self.alpha = color.get_alpha()

    def set_from_hsv(self,hue,sat,val,alpha=1):
        hue = float(hue % 360)
        L=val*(1.0-sat)
        H=val
        M=val*(1-sat*(abs((hue/60.0)%2.0-1)))
        if hue < 60:
            self.set_rgba(H,M,L,alpha)
        elif hue < 120:
            self.set_rgba(M,H,L,alpha)
        elif hue < 180:
            self.set_rgba(L,H,M,alpha)
        elif hue < 240:
            self.set_rgba(L,M,H,alpha)
        elif hue < 300:
            self.set_rgba(M,L,H,alpha)
        else:
            self.set_rgba(H,L,M,alpha)

    def copy(self):
        return RGBAColor(self.red, self.green, self.blue, self.alpha)

    def to_gtk_color(self):
        return gtk.gdk.Color(self.red, self.green, self.blue)

    def set_from_gtk_color(self,gtk_color):
        string = gtk_color.to_string()
        self.red = int(string[1:5], 16) / 65535.0
        self.green = int(string[5:9], 16) / 65535.0
        self.blue = int(string[9:13], 16) / 65535.0

# Registering signals
gobject.signal_new("color-changed-event", ColorCell, gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,))
