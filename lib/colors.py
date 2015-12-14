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
from utils import Callable

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

    def modify_color(self, color):
        csd = gtk.ColorSelectionDialog("Choose a color")
        csd.set_modal(True)
        cs = csd.get_color_selection()
        cs.set_property("current-color", self.color.to_gtk_color())
        ok = csd.run()
        if ok == gtk.RESPONSE_OK:
            self.set_color_vals(RGBAColor.create_from_gtk_color(cs.get_current_color()))
        csd.destroy()

    def clicked(self, widget, event):
        if event.type == gtk.gdk._2BUTTON_PRESS:
            self.modify_color(widget)
        self.emit("color-changed-event", event)

    def to_string(self):
        return "ColorCell: " + self.color.to_string()

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

    def get_rgba(self):
        return self.red, self.green, self.blue, self.alpha

    def set_rgba(self, red, green, blue, alpha):
        self.set_red(red)
        self.set_green(green)
        self.set_blue(blue)
        self.set_alpha(alpha)

    def get_rgb(self):
        return self.red, self.green, self.blue

    def set_rgb(self, red, green, blue):
        self.set_rgba(red, green, blue, 1.0)

    def set_color_vals(self,color):
        self.red = color.get_red()
        self.green = color.get_green()
        self.blue = color.get_blue()
        self.alpha = color.get_alpha()

    def to_string(self):
        return "(" + str(self.red) + ", " + str(self.green) + ", " + str(self.blue) + ", " + str(self.alpha) + ")"

    def copy(self):
        return RGBAColor(self.red, self.green, self.blue, self.alpha)

    def to_gtk_color(self):
        # TODO: use proper values
        return gtk.gdk.color_parse("#f00")

    def create_from_gtk_color(gtk_color):
        string = gtk_color.to_string()

        red = int(string[1:5], 16) / 65535.0
        green = int(string[5:9], 16) / 65535.0
        blue = int(string[9:13], 16) / 65535.0

        return RGBAColor(red, green, blue)
    create_from_gtk_color = Callable(create_from_gtk_color)

    def color_parse(color):
        return RGBAColor.create_from_gtk_color(gtk.gdk.color_parse(color))
    color_parse = Callable(color_parse)

class HSVGenerator:
    def get_hsv_color(self, hue, sat, val):
        hue = hue % 360

        min = 1.0-sat
        max = val
        interval = max - min

        red = min + self.__get_red(hue) * interval
        green = min + self.__get_green(hue) * interval
        blue = min + self.__get_blue(hue) * interval

        red = '%x'%(self.__toByte(red))
        green = '%x'%(self.__toByte(green))
        blue = '%x'%(self.__toByte(blue))

        if len(red) == 1:
            red = '0'+red
        if len(green) == 1:
            green = '0'+green
        if len(blue) == 1:
            blue = '0'+blue

        return gtk.gdk.color_parse("#"+red+green+blue)


    def __get_red(self, hue):
        #
        if 0 <= hue < 60:
            return 1.0
        #
        if 60 <= hue < 120:
            return self.__decrease(hue%60)
        #
        if 120 <= hue < 180:
            return 0.0
        #
        if 180 <= hue < 240:
            return 0.0
        #
        if 240 <= hue < 300:
            return self.__increase(hue%60)
        #
        if 300 <= hue < 360:
            return 1.0
        # This should never happen
        return 0.0


    def __get_green(self, hue):
        #
        if 0 <= hue < 60:
            return self.__increase(hue%60)
        #
        if 60 <= hue < 120:
            return 1.0
        #
        if 120 <= hue < 180:
            return 1.0
        #
        if 180 <= hue < 240:
            return self.__decrease(hue%60)
        #
        if 240 <= hue < 300:
            return 0.0
        #
        if 300 <= hue < 360:
            return 0.0
        # This should never happen
        return 0.0


    def __get_blue(self, hue):
        #
        if 0 <= hue < 60:
            return 0.0
        #
        if 60 <= hue < 120:
            return 0.0
        #
        if 120 <= hue < 180:
            return self.__increase(hue%60)
        #
        if 180 <= hue < 240:
            return 1.0
        #
        if 240 <= hue < 300:
            return 1.0
        #
        if 300 <= hue < 360:
            return self.__decrease(hue%60)
        # This should never happen
        return 0.0


    def __increase(self, hue):
        return hue/60.0

    def __decrease(self, hue):
        return 1 - hue/60.0

    def __toByte(self, dbl, min=0.0, max=1.0):
        value = (dbl - min) / (max - min)
        value = round(value * 255)
        return math.floor(value)

# Registering signals
gobject.signal_new("color-changed-event", ColorCell, gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,))
