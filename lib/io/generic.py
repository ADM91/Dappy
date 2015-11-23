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
            canonical_filename = self.save_as(image, path)
        else:
            canonical_filename = path + os.sep + filename
            self.__detect_tool(canonical_filename)
            self.current_tool.write(image, canonical_filename)
        return canonical_filename


    def save_as(self, image, path, filename=None):
        file_dialog = gtk.FileChooserDialog(title=None,
           action=gtk.FILE_CHOOSER_ACTION_SAVE,
           buttons=(gtk.STOCK_CANCEL,
              gtk.RESPONSE_CANCEL,
              gtk.STOCK_SAVE,
              gtk.RESPONSE_OK)
           )
        file_dialog.set_do_overwrite_confirmation(True)
        file_dialog.set_title(_("Save Image As"))
        if filename != None:
            canonical_filename = path + os.sep + filename
            file_dialog.set_filename(canonical_filename)
        else:
            file_dialog.set_current_folder(path)

        for tool in self.TOOLS_BY_FILTER.values():
            file_dialog.add_filter(tool.get_filter())

        response = file_dialog.run()
        if response == gtk.RESPONSE_OK:
            self.current_tool = self.TOOLS_BY_FILTER[file_dialog.get_filter()]
            filename = file_dialog.get_filename()
            if not os.path.exists(filename):
                pat_good = False
                for pat in self.current_tool.patterns:
                    if filename.endswith(pat):
                        pat_good=True
                if not pat_good:
                    filename += self.current_tool.patterns[0]
            self.current_tool.write(image, filename)
        else:
            filename = None
        file_dialog.destroy()
        return filename


    def read(self, filename):
        self.__detect_tool(filename)
        return self.current_tool.read(filename)


    def __detect_tool(self, filename):
        imgtype = imghdr.what(filename)
        self.current_tool = self.TOOLS_BY_IMGTYPE[imgtype]
