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
import os
import sys



_ = gettext.gettext

class Dappy():
    canvas = None

    filename = None
    path = None
    FileHandler = None
    primary = None
    secondary = None


    def __init__(self, path, image_filename=None):

        # Initialize canvas
        self.canvas = Canvas()
        self.FileHandler = FileIO()

        # Load image information
        if image_filename != None:
            info = self.FileHandler.read(os.path.abspath(image_filename))
            self.set_current_info(info)
        else:
            self.filename = None
            self.path = path

        # Initialize colors
        self.primary = RGBAColor(0, 0, 0, 1)
        self.secondary = RGBAColor(1, 1, 1, 1)
        self.canvas.bg_col = self.secondary.get_rgba()

        # Defining tools
        self.TOOLS = {"draw-rounded-rectangle" : tools.RoundedRectangleTool(self.canvas),
                      "draw-rectangle"  : tools.RectangleTool(self.canvas),
                      "straight-line"   : tools.StraightLineTool(self.canvas),
                      "pencil"          : tools.PencilTool(self.canvas),
                      "paintbrush"      : tools.PaintbrushTool(self.canvas),
                      "bucket-fill"     : tools.BucketFillTool(self.canvas),
                      "eraser"          : tools.EraserTool(self.canvas),
                      "draw-ellipse"    : tools.EllipseTool(self.canvas),
                      "color-picker"    : tools.ColorPickerTool(self.canvas),
                      "rect-select"     : tools.RectangleSelectTool(self.canvas),
                      "airbrush"        : tools.AirBrushTool(self.canvas)}

        self.canvas.clear_overlay()
        self.canvas.print_tool()

    def change_tool(self, toolname):
        self.canvas.set_active_tool(self.TOOLS[toolname])


    def set_primary_color(self, c):
        self.primary = c
        for tool in self.TOOLS.values():
            tool.set_primary_color(c)


    def set_secondary_color(self, c):
        self.secondary = c
        for tool in self.TOOLS.values():
            tool.set_secondary_color(c)
        self.canvas.bg_col = self.secondary.get_rgba()


    def get_primary_color(self):
        return self.primary


    def get_secondary_color(self):
        return self.secondary


    def set_current_info(self, image_info):
        if image_info == None:
            return

        canonical_filename = image_info[0]
        self.canvas.set_image(image_info[1])
        self.fix_image_info(canonical_filename)


    def fix_image_info(self, canonical_filename):
        if canonical_filename == None:
            return

        self.filename = os.path.basename(canonical_filename)
        self.path = os.path.dirname(canonical_filename)


if __name__ == "__main__":

    filename = None
    if len(sys.argv) == 2:
        filename = sys.argv[1]

    default_path = os.getcwd()
    os.chdir(os.path.dirname(os.path.realpath(__file__)))
    sys.path.insert(0, 'lib')
    from dappygui import GUI
    from canvas import Canvas
    from file_io import FileIO
    from colors import RGBAColor
    import tools
    app = Dappy(default_path, filename)
    gui = GUI(app)

    gtk.main()
