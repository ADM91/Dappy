import sys
import os
from ctypes import cdll
from ctypes import c_char_p
from ctypes import c_int

from lib.misc.utils import Callable

class FloodFillAlgorithm:

    def execute(x, y, image, width, height, bpc, replacement):
        ireplacement = FloodFillAlgorithm.color_to_int(replacement)

        lib=os.path.dirname(sys.argv[0]) + "/lib/c/floodfill.so"
        dll = cdll.LoadLibrary(lib)
        function = (lambda x, y, image, width, height, bpc, ireplacement: \
           dll.floodfill( \
              c_int(x), \
              c_int(y), \
              c_char_p(image), \
              c_int(width), \
              c_int(height), \
              c_int(bpc), \
              c_int(ireplacement) \
        )  )

        function(x, y, image, width, height, bpc, ireplacement)
    execute = Callable(execute)

    def color_to_int(color):
        res = 0
        res |= (color[0] & 0xff) << 24
        res |= (color[1] & 0xff) << 16
        res |= (color[2] & 0xff) << 8
        res |= (color[3] & 0xff)
        return res
    color_to_int = Callable(color_to_int)
