#!/usr/bin/python

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


# Import packages
import pygtk
pygtk.require("2.0")
import gtk
import gettext
import os

from lib.misc.hsvgenerator import HSVGenerator
from lib.graphics.colorcell import ColorCell
from lib.graphics.rgbacolor import RGBAColor

_ = gettext.gettext

class GUI():
    DAPPY = None
    builder = None

    def __init__(self, dappy):
        self.DAPPY = dappy
        
        self.DAPPY.canvas.connect("color_pick_event", self.color_changed)
        self.DAPPY.canvas.connect("change_sensitivty", self.set_sensitivity)
        self.builder = gtk.Builder()
        self.builder.add_from_file(os.path.join(os.path.dirname( os.path.realpath( __file__ ) ) + os.sep + "dappy.xml"))

        # Get the window properly
        self.window = self.builder.get_object("main-window")
        self.window.connect("delete_event",self.quit)

        # Initialize canvas
        viewport = self.builder.get_object("viewport-for-canvas")
        viewport.add(self.DAPPY.get_canvas())

        # Set the first tool to use...
        current_tool = "btn-tool-paintbrush"
        self.active_tool_button = None
        self.builder.get_object(current_tool).set_active(True)
        self.change_tool_gui(self.builder.get_object(current_tool))

        # Get the toolbar and set it not to show text
        self.toolbar = self.builder.get_object("toolbar")
        self.toolbar.set_style(gtk.TOOLBAR_ICONS)

        # Initialize palette
        self.__init_colors(self.builder.get_object("colors-grid"))

        # Initialize working colors
        self.primary = ColorCell(0, 0, 0)
        self.primary.connect("color-changed-event", self.color_changed)
        primary_frame = self.builder.get_object("primary-color")
        primary_frame.add(self.primary)
        self.secondary = ColorCell(1, 1, 1)
        self.secondary.connect("color-changed-event", self.color_changed)
        secondary_frame = self.builder.get_object("secondary-color")
        secondary_frame.add(self.secondary)

        # Fix alpha sliders
        a1 = self.builder.get_object("primary-color-alpha")
        a1.set_value(a1.get_value())
        self.MAX_ALPHA_1 = a1.get_value()
        a2 = self.builder.get_object("secondary-color-alpha")
        a2.set_value(a2.get_value())
        self.MAX_ALPHA_2 = a2.get_value()

        # Connecting signals properly...
        self.builder.connect_signals(self)

        # Show the window
        self.window.show_all()


    def __init_colors(self, colorsgrid):
        colors = colorsgrid.get_children()
        rows = colorsgrid.get_property("n-rows")
        columns = colorsgrid.get_property("n-columns")

        # Color[0][0]
        color_frame = colors[0]
        colorcell = ColorCell(0, 0, 0)
        colorcell.connect("color-changed-event", self.color_changed)
        color_frame.add(colorcell)
        # Color[0][1]
        color_frame = colors[columns]
        colorcell = ColorCell(1, 1, 1)
        colorcell.connect("color-changed-event", self.color_changed)
        color_frame.add(colorcell)

        # Color[1][0]
        color_frame = colors[1]
        colorcell = ColorCell(0.33, 0.33, 0.33)
        colorcell.connect("color-changed-event", self.color_changed)
        color_frame.add(colorcell)
        # Color[1][1]
        color_frame = colors[columns + 1]
        colorcell = ColorCell(0.66, 0.66, 0.66)
        colorcell.connect("color-changed-event", self.color_changed)
        color_frame.add(colorcell)

        hsv = HSVGenerator()

        # The other colors
        for i in range(rows):
            for j in range(2, columns):
                # Each cell is: frame{ eventbox{label} }
                color_frame = colors[i*columns + j]
                color = hsv.get_hsv_color(360*(j-2)/(columns-2), 1.0-0.7*i, 1.0)
                colorcell = ColorCell()
                colorcell.connect("color-changed-event", self.color_changed)
                colorcell.set_color(RGBAColor.create_from_gtk_color(color))
                color_frame.add(colorcell)


    def quit(self, window,event=-100):
        q=False;
        if self.DAPPY.canvas.is_modified():
            warning = gtk.MessageDialog(self.window, gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_QUESTION, gtk.BUTTONS_OK_CANCEL, "Your canvas has been modified. Are you sure you want to quit now?")
            a = warning.run()
            warning.destroy()
            if a==-5:
                q=True
        else:
            q=True
        if q:
            if event==gtk.gdk.DELETE:
                return False
            else:
                gtk.main_quit()
        else:
            return True

    def color_changed(self, widget, event):
        if widget==self.primary:
            self.primary.modify_color(widget)
            c = widget.get_color()
            self.DAPPY.set_primary_color(c)
        elif widget==self.secondary:
            self.secondary.modify_color(widget)
            c = widget.get_color()
            self.DAPPY.set_secondary_color(c)
        else:
            c = widget.get_color()
            if event.type==gtk.gdk.MOTION_NOTIFY:
                button = widget.active_tool.m_button
            else:
                button = event.button
            if button == 1:
                c.set_alpha(self.DAPPY.get_primary_color().get_alpha())
                self.DAPPY.set_primary_color(c)
                self.primary.set_color(c)
            elif button == 3:
                c.set_alpha(self.DAPPY.get_secondary_color().get_alpha())
                self.DAPPY.set_secondary_color(c)
                self.secondary.set_color(c)


    def change_tool_gui(self, newtool):
        if newtool.get_active():
            prevtool = self.active_tool_button
            if newtool != prevtool:
                self.active_tool_button = newtool
                if prevtool != None:
                    prevtool.set_active(False)
                self.DAPPY.change_tool(gtk.Buildable.get_name(newtool).replace("btn-tool-", ""))


    def change_primary_alpha(self, slider):
        c = self.DAPPY.get_primary_color()
        value = slider.get_value()/self.MAX_ALPHA_1
        c.set_alpha(value)
        self.DAPPY.set_primary_color(c)
        self.primary.set_color(c)


    def change_secondary_alpha(self, slider):
        c = self.DAPPY.get_secondary_color()
        value = slider.get_value()/self.MAX_ALPHA_2
        c.set_alpha(value)
        self.DAPPY.set_secondary_color(c)
        self.secondary.set_color(c)
        
    def set_sensitivity(self,widget,event):
        if event.action == "undo":
            ub = self.builder.get_object("undo-button")
            ub.set_sensitive(event.sensitive)
            um = self.builder.get_object("menu-undo")
            um.set_sensitive(event.sensitive)
        elif event.action == "redo":
            rb = self.builder.get_object("redo-button")
            rb.set_sensitive(event.sensitive)
            rm = self.builder.get_object("menu-redo")
            rm.set_sensitive(event.sensitive)
        else:
            print('Button %s unknown')%event.action
            
        
    def new(self, widget):
        self.DAPPY.new()


    def open(self, widget):
        self.DAPPY.open()


    def save(self, widget):
        self.DAPPY.save()


    def save_as(self, widget):
        self.DAPPY.save_as()

    def cut(self, widget):
        self.DAPPY.cut()

    def copy(self, widget):
        self.DAPPY.copy()


    def paste(self, widget):
        self.DAPPY.paste()


    def redo(self, widget):
        self.DAPPY.redo()


    def undo(self, widget):
        self.DAPPY.undo()
        
    def delete(self, widget):
        self.DAPPY.delete()
