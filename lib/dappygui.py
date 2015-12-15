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
import gtk
import gettext

from colors import ColorCell

_ = gettext.gettext

class senstivity_data:

    def __init__(self,action,sensitive):
        self.action = action
        self.sensitive = sensitive

class GUI():
    DAPPY = None
    builder = None
    block_tool_event = None

    def __init__(self, dappy):
        self.DAPPY = dappy

        self.DAPPY.canvas.connect("color_pick_event", self.color_changed)
        self.DAPPY.canvas.connect("change_sensitivty", self.set_sensitivity)
        self.builder = gtk.Builder()
        self.builder.add_from_file("GUI/dappy.xml")
        #os.path.join(os.path.dirname( os.path.realpath( __file__ ) ) + "glade" + os.sep + "dappy.xml")

        # Get the window properly
        self.window = self.builder.get_object("main-window")
        self.window.connect("delete_event",self.quit)

        # Initialize canvas
        viewport = self.builder.get_object("viewport-for-canvas")
        viewport.add(self.DAPPY.canvas)

        # Get the toolbar and set it not to show text
        self.toolbar = self.builder.get_object("toolbar")
        self.toolbar.set_style(gtk.TOOLBAR_ICONS)

        # Initialize palette
        self.__init_colors(self.builder.get_object("colors-grid"))

        # Initialize working colors
        self.primary = ColorCell()
        self.primary.set_color(self.DAPPY.canvas.primary)
        self.primary.connect("color-changed-event", self.color_changed)
        primary_frame = self.builder.get_object("primary-color")
        primary_frame.add(self.primary)
        self.secondary = ColorCell()
        self.secondary.set_color(self.DAPPY.canvas.secondary)
        self.secondary.connect("color-changed-event", self.color_changed)
        secondary_frame = self.builder.get_object("secondary-color")
        secondary_frame.add(self.secondary)
        self.swap_cols = self.builder.get_object("swap-colors")
        self.swap_cols.connect("button-press-event", self.color_changed)

        # Fix alpha sliders
        self.primary_a_slide = self.builder.get_object("primary-color-alpha")
        self.primary_a_slide.set_value(self.primary_a_slide.get_value())
        self.secondary_a_slide = self.builder.get_object("secondary-color-alpha")
        self.secondary_a_slide.set_value(self.secondary_a_slide.get_value())

        #toolbar handels
        self.fig_tb = self.builder.get_object("figure-toolbar")
        self.airb_tb = self.builder.get_object("airbrush-toolbar")
        self.sel_tb = self.builder.get_object("select-toolbar")
        self.misc_tb = self.builder.get_object("misc-toolbar")

        #Fix spinners
        fig_lw = self.builder.get_object("figure-line-width")
        fig_lw .set_value(fig_lw .get_value())
        self.DAPPY.canvas.figure_linewidth=fig_lw.get_value()
        self.fig_cr = self.builder.get_object("figure-corner-radius")
        self.fig_cr .set_value(self.fig_cr .get_value())
        self.DAPPY.canvas.figure_corner_radius=self.fig_cr.get_value()
        self.airb_w = self.builder.get_object("airbrush-width")
        self.airb_w .set_value(self.airb_w .get_value())
        self.DAPPY.canvas.airbrush_width=self.airb_w.get_value()

        # Connecting signals properly...
        self.builder.connect_signals(self)

        # Show the window
        self.window.show_all()

        # Set the first tool to use...
        self.curr_tool = self.builder.get_object("btn-tool-paintbrush")
        self.block_tool_event = False
        self.active_tool_button = None
        self.curr_tool.set_active(True)

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

        # The other colors
        for i in range(rows):
            for j in range(2, columns):
                color_frame = colors[i*columns + j]
                colorcell = ColorCell(360*(j-2)/(columns-2), 1.0-0.7*i, 1.0,1.0,True)
                colorcell.connect("color-changed-event", self.color_changed)
                color_frame.add(colorcell)

    def quit(self, window,event=-100):
        q=False
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
            self.primary.modify_color()
            c = widget.get_color()
            self.primary.set_color_vals(c)
        elif widget==self.secondary:
            self.secondary.modify_color()
            c = widget.get_color()
            self.secondary.set_color_vals(c)
        elif widget==self.swap_cols:
            c_temp = self.primary.get_color()
            self.primary.set_color_vals(self.secondary.get_color())
            self.primary_a_slide.set_value(self.primary.color.get_alpha())
            self.secondary.set_color_vals(c_temp)
            self.secondary_a_slide.set_value(self.secondary.color.get_alpha())
        else:
            c = widget.get_color()
            if event.type==gtk.gdk.MOTION_NOTIFY:
                button = widget.active_tool.m_button
            else:
                button = event.button
            if button == 1:
                c.set_alpha(self.primary_a_slide.get_value())
                self.primary.set_color_vals(c)
            elif button == 3:
                c.set_alpha(self.secondary_a_slide.get_value())
                self.secondary.set_color_vals(c)

    def change_tool_gui(self, newtool):
        if not self.block_tool_event:
            if newtool.get_active():
                self.curr_tool = newtool
                prevtool = self.active_tool_button
                if newtool != prevtool:
                    toolname =  gtk.Buildable.get_name(newtool).replace("btn-tool-", "")
                    self.active_tool_button = newtool
                    if prevtool != None:
                        self.block_tool_event = True
                        prevtool.set_active(False)
                        self.block_tool_event = False
                    self.DAPPY.canvas.set_active_tool(toolname)
                    self.change_2nd_toolbar(toolname)
            else:
                self.block_tool_event = True
                newtool.set_active(True)
                self.block_tool_event = False

    def change_alpha_slider(self, slider):
        if slider == self.primary_a_slide:
            self.primary.set_alpha(slider.get_value())
        else:
            self.secondary.set_alpha(slider.get_value())

    def change_figure_linewidth(self, widget):
        self.DAPPY.canvas.figure_linewidth= widget.get_value()
        self.curr_tool.grab_focus()

    def change_figure_corner_radius(self, widget):
        self.DAPPY.canvas.figure_corner_radius= widget.get_value()
        self.curr_tool.grab_focus()

    def change_airbrush_width(self, widget):
        self.DAPPY.canvas.airbrush_width= widget.get_value()
        self.curr_tool.grab_focus()

    def set_sensitivity(self,widget,event):
        if event.action == "undo":
            self.builder.get_object("undo-button").set_sensitive(event.sensitive)
            self.builder.get_object("menu-undo").set_sensitive(event.sensitive)
        elif event.action == "redo":
            self.builder.get_object("redo-button").set_sensitive(event.sensitive)
            self.builder.get_object("menu-redo").set_sensitive(event.sensitive)
        elif event.action =="crop":
            self.builder.get_object("crop-button").set_sensitive(event.sensitive)
        else:
            print('Button %s unknown')%event.action

    def change_2nd_toolbar(self,tool):
        if tool=="draw-rounded-rectangle" or tool=="draw-ellipse" or tool=="draw-rectangle":
            self.fig_tb.show_all()
            self.airb_tb.hide_all()
            self.sel_tb.hide_all()
            self.misc_tb.hide_all()
            if tool=="draw-rounded-rectangle":
                self.fig_cr.set_sensitive(True)
            else:
                self.fig_cr.set_sensitive(False)
        elif tool=="airbrush":
            self.fig_tb.hide_all()
            self.airb_tb.show_all()
            self.sel_tb.hide_all()
            self.misc_tb.hide_all()
        elif tool=="rect-select":
            self.fig_tb.hide_all()
            self.airb_tb.hide_all()
            self.sel_tb.show_all()
            self.misc_tb.hide_all()
        else:
            self.fig_tb.hide_all()
            self.airb_tb.hide_all()
            self.sel_tb.hide_all()
            self.misc_tb.show_all()

    def set_figure_fill(self,widget):
        if widget.get_active():
            fill_name =  gtk.Buildable.get_name(widget).replace("figure-", "").replace("-fill", "")
            if fill_name == "secondary":
                self.DAPPY.canvas.fig_fill_type=0
            elif fill_name == "primary":
                self.DAPPY.canvas.fig_fill_type=1
            elif fill_name == "no":
                self.DAPPY.canvas.fig_fill_type=2

    def new(self, widget):
        n=False
        if self.DAPPY.canvas.is_modified():
            warning = gtk.MessageDialog(self.window, gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_QUESTION, gtk.BUTTONS_OK_CANCEL, "Your canvas has been modified. Are you sure you want to close it without saving?")
            a = warning.run()
            warning.destroy()
            if a==-5:
                n=True
        else:
            n=True
        if n:
            self.primary_a_slide.set_value(1.0)
            self.secondary_a_slide.set_value(1.0)
            self.primary.set_rgba(0, 0, 0, 1)
            self.secondary.set_rgba(1, 1, 1, 1)
            self.DAPPY.canvas.clear_overlay()
            self.DAPPY.canvas.delete()
            self.DAPPY.canvas.clear_undo_buffer()
            self.DAPPY.filename = None
            self.DAPPY.canvas.modified=False

    def open(self, widget):
        info = self.DAPPY.FileHandler.open(self.DAPPY.path)
        self.DAPPY.set_current_info(info)

    def save(self, widget):
        canonical_filename = self.DAPPY.FileHandler.save(self.DAPPY.canvas.get_image(), self.DAPPY.path, self.DAPPY.filename)
        self.DAPPY.fix_image_info(canonical_filename)

    def save_as(self, widget):
        canonical_filename = self.DAPPY.FileHandler.save_as(self.DAPPY.canvas.get_image(), self.DAPPY.path, self.DAPPY.filename)
        self.DAPPY.fix_image_info(canonical_filename)

    def cut(self, widget):
        self.DAPPY.canvas.copy(True)

    def copy(self, widget):
        self.DAPPY.canvas.copy(False)

    def paste(self, widget):
        self.DAPPY.canvas.paste()

    def redo(self, widget):
        self.DAPPY.canvas.redo()

    def undo(self, widget):
        self.DAPPY.canvas.undo()

    def delete(self, widget):
        self.DAPPY.canvas.delete()

    def crop(self,widget):
        self.DAPPY.canvas.crop()
