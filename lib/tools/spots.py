from array import array
import Image

from generic import Tool
from generic import DragAndDropTool
from lib.c.algorithms import FloodFillAlgorithm
from lib.graphics.imageutils import ImageUtils

import time

class ColorPickerTool(DragAndDropTool):
    pixels = None


    def begin(self, x, y):
        self.mode = self.DRAWING
        self.pixels = ImageUtils.create_image_from_surface(self.canvas.CANVAS).load()
        print self.pixels[x, y]


    def end(self, x, y):
        self.mode = self.READY
        print self.pixels[x, y]


    def move(self, x, y):
        if self.mode == self.DRAWING:
            print self.pixels[x, y]



class BucketFillTool(Tool):

    def begin(self, x, y):
        self.mode = self.READY
        image = ImageUtils.create_image_from_surface(self.canvas.CANVAS)

        surface = self.canvas.CANVAS
        data = image.tostring()
        w = surface.get_width()
        h = surface.get_height()
        s = surface.get_stride()

        pc = self.primary
        replacement = (int(pc.get_blue()*255), int(pc.get_green()*255),
                       int(pc.get_red()*255), int(pc.get_alpha()*255))
        FloodFillAlgorithm.execute(int(x), int(y), data, w, h, s/w, replacement)
        image = Image.frombuffer('RGBA', (w, h), data, 'raw', 'RGBA', 0, 1)

        surface = ImageUtils.create_surface_from_image(image)
        self.canvas.set_image(surface)
        self.canvas.swap_buffers()
