import cairo
import gtk
import os
import gettext
import imghdr

from readwrite import PNGReaderWriter
from readwrite import JPEGReaderWriter

_ = gettext.gettext

class ImageFile:

    def __init__(self):
        png = PNGReaderWriter()

        self.TOOLS_BY_FILTER = { png.get_filter() : png }
        self.TOOLS_BY_IMGTYPE = { png.get_imgtype() : png }
        self.current_tool = None

    def open(self, path):
        file_dialog = gtk.FileChooserDialog(title=None,
           action=gtk.FILE_CHOOSER_ACTION_OPEN,
           buttons=(gtk.STOCK_CANCEL,
              gtk.RESPONSE_CANCEL,
              gtk.STOCK_OPEN, gtk.RESPONSE_OK)
           )

        for tool in self.TOOLS_BY_FILTER.values():
            file_dialog.add_filter(tool.get_filter())

        file_dialog.set_title(_("Open Image"))
        file_dialog.set_current_folder(path)

        response = file_dialog.run()
        if response == gtk.RESPONSE_OK:
            self.current_tool = self.TOOLS_BY_FILTER[file_dialog.get_filter()]
            result = self.current_tool.read(file_dialog.get_filename())
        else:
            result = None
        file_dialog.destroy()

        return result


    def save(self, image, path, filename=None):
        if filename == None:
            self.save_as(image, path)
        else:
            canonical_filename = path + os.sep + filename
            self.__detect_tool(filename)
            self.current_tool.write(image, canonical_filename)


    def save_as(self, image, path, filename=None):
        file_dialog = gtk.FileChooserDialog(title=None,
           action=gtk.FILE_CHOOSER_ACTION_SAVE,
           buttons=(gtk.STOCK_CANCEL,
              gtk.RESPONSE_CANCEL,
              gtk.STOCK_SAVE,
              gtk.RESPONSE_OK)
           )

        file_dialog.set_title(_("Save Image As"))
        file_dialog.set_current_folder(path)
        if filename != None:
            file_dialog.set_filename(filename)

        for tool in self.TOOLS_BY_FILTER.values():
            file_dialog.add_filter(tool.get_filter())

        response = file_dialog.run()
        if response == gtk.RESPONSE_OK:
            self.current_tool = self.TOOLS_BY_FILTER[file_dialog.get_filter()]
            self.current_tool.write(image, file_dialog.get_filename())
        file_dialog.destroy()


    def read(self, filename):
        self.__detect_tool(filename)
        return self.current_tool.read(filename)


    def __detect_tool(self, filename):
        imgtype = imghdr.what(filename)
        self.current_tool = self.TOOLS_BY_IMGTYPE[imgtype]
