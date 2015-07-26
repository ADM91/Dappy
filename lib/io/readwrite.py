import cairo
import gettext
import gtk

from lib.graphics.canvas import Canvas

_ = gettext.gettext

class ReaderWriter:
    FILTER = None
    IMGTYPE = None

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
        self.FILTER.add_pattern("*.png")

        self.IMGTYPE = "png"


    def read(self, canonical_filename):
        return (canonical_filename,
           cairo.ImageSurface.create_from_png(canonical_filename),
           Canvas.TRANSPARENT_IMAGE)


    def write(self, image, canonical_filename):
        image.write_to_png(canonical_filename)



class JPEGReaderWriter(ReaderWriter):
    def __init__(self):
        self.FILTER = gtk.FileFilter()
        self.FILTER.set_name("JPG - Portable Network Graphics")
        self.FILTER.add_mime_type("image/jpeg")
        self.FILTER.add_pattern("*.jpg")
        self.FILTER.add_pattern("*.jpeg")

        self.IMGTYPE = "jpeg"


    def read(self, canonical_filename):
        return (canonical_filename,
           cairo.ImageSurface.create_from_png(canonical_filename),
           Canvas.OPAQUE_IMAGE)


    def write(self, image, canonical_filename):
        image.write_to_png(canonical_filename)
