#!/usr/bin/python

# Import packages
#import pygtk
#pygtk.require("2.0")
import gtk
import gettext
import os
import sys

from lib.gui.painthongui import GUI
from lib.graphics.fancycanvas import FancyCanvas
from lib.io.generic import ImageFile
from lib.tools.figures import *
from lib.tools.free import *
from lib.tools.generic import *
from lib.tools.lines import *
from lib.tools.spots import *

_ = gettext.gettext

class Painthon():
    CANVAS = None
    READWRITE = None

    filename = None
    path = None

    primary = None
    secondary = None

    def __init__(self, path, image_filename=None):

        # Initialize canvas
        self.CANVAS = FancyCanvas()
        self.CANVAS.set_image_type(FancyCanvas.OPAQUE_IMAGE)

        # Initialize readers/writers
        self.READWRITE = ImageFile()

        # Load image information
        if image_filename != None:
            info = self.READWRITE.read(os.path.abspath(image_filename))
            self.__set_current_info(info)
        else:
            self.filename = None
            self.path = path

        # Initialize colors
        self.primary = RGBAColor(0, 0, 0, 1)
        self.secondary = RGBAColor(1, 1, 1, 1)

        # Defining tools
        self.TOOLS = {"draw-rounded-rectangle" : RoundedRectangleTool(self.CANVAS),
                      "draw-rectangle"  : RectangleTool(self.CANVAS),
                      "straight-line"   : StraightLineTool(self.CANVAS),
                      "pencil"          : PencilTool(self.CANVAS),
                      "paintbrush"      : PaintbrushTool(self.CANVAS),
                      "bucket-fill"     : BucketFillTool(self.CANVAS),
                      "eraser"          : EraserTool(self.CANVAS),
                      "color-picker"    : ColorPickerTool(self.CANVAS),
                      "draw-ellipse"    : EllipseTool(self.CANVAS) }


    def quit(self, main_window):
        if self.is_modified():
            warning = gtk.MessageDialog(main_window, gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_WARNING, gtk.BUTTONS_OK, "TODO")
            a = warning.run()
            warning.destroy()
        gtk.main_quit()


    def change_tool(self, toolname):
        self.CANVAS.set_active_tool(self.TOOLS[toolname])


    def set_primary_color(self, c):
        self.primary = c
        for tool in self.TOOLS.values():
            tool.set_primary_color(c)


    def set_secondary_color(self, c):
        self.secondary = c
        for tool in self.TOOLS.values():
            tool.set_secondary_color(c)


    def get_primary_color(self):
        return self.primary


    def get_secondary_color(self):
        return self.secondary


    def new(self):
        print "new"


    def open(self):
        info = self.READWRITE.open(self.path)
        self.__set_current_info(info)


    def save(self):
        canonical_filename = self.READWRITE.save(self.CANVAS.get_image(), self.path, self.filename)
        self.__fix_image_info(canonical_filename)


    def save_as(self):
        canonical_filename = self.READWRITE.save_as(self.CANVAS.get_image(), self.path, self.filename)
        self.__fix_image_info(canonical_filename)


    def __set_current_info(self, image_info):
        if image_info == None:
            return

        canonical_filename = image_info[0]
        self.CANVAS.set_image(image_info[1])
        self.CANVAS.set_image_type(image_info[2])
        self.__fix_image_info(canonical_filename)


    def __fix_image_info(self, canonical_filename):
        if canonical_filename == None:
            return

        self.filename = os.path.basename(canonical_filename)
        self.path = os.path.dirname(canonical_filename)


    def cut(self):
        print "cut"


    def copy(self):
        print "copy"


    def paste(self):
        print "paste"


    def redo(self):
        print "redo"


    def undo(self):
        print "undo"


    def is_modified(self):
        # TODO: return the proper result... ;-)
        return False

    def get_canvas(self):
        return self.CANVAS



if __name__ == "__main__":
    
    filename = None
    if len(sys.argv) == 2:
        filename = sys.argv[1]
    
    print filename
    default_path = os.getcwd()
    os.chdir(os.path.dirname(os.path.realpath(__file__)))

    app = Painthon(default_path, filename)
    gui = GUI(app)

    gtk.main()
