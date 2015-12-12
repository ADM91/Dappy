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
import gettext
import gtk

_ = gettext.gettext

class ReaderWriter:
    FILTER = None
    IMGTYPE = None
    patterns = None

    def get_filter(self):
        return self.FILTER

    def get_imgtype(self):
        return self.IMGTYPE

    def read(self, canonical_filename): pass
    def write(self, image, canonical_filename): pass



class PNGReaderWriter(ReaderWriter):
    def __init__(self):
        self.FILTER = gtk.FileFilter()
        self.FILTER.set_name("PNG - Portable Network Graphics")
        self.FILTER.add_mime_type("image/png")
        self.IMGTYPE = "png"
        self.patterns = ('.png','.PNG',)
        for pat in self.patterns:
            self.FILTER.add_pattern("*"+pat)


    def read(self, canonical_filename):
        return (canonical_filename,
           cairo.ImageSurface.create_from_png(canonical_filename))


    def write(self, image, canonical_filename):
        image.write_to_png(canonical_filename)



class JPEGReaderWriter(ReaderWriter):
    def __init__(self):
        self.FILTER = gtk.FileFilter()
        self.FILTER.set_name("JPG - Portable Network Graphics")
        self.FILTER.add_mime_type("image/jpeg")
        self.IMGTYPE = "jpeg"
        self.patterns = (".jpg",'.jpeg')
        for pat in self.patterns:
            self.FILTER.add_pattern("*"+pat)


    def read(self, canonical_filename):
        return (canonical_filename,
           cairo.ImageSurface.create_from_png(canonical_filename))


    def write(self, image, canonical_filename):
        image.write_to_png(canonical_filename)
