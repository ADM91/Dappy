import cairo
import Image
from array import array

from lib.misc.utils import Callable

class ImageUtils:
    COLORMODE_RGBA = 0
    COLORMODE_BGRA = 1

    def create_image_from_surface(surface, colormode=1):
        data = surface.get_data()
        w = surface.get_width()
        h = surface.get_height()
        s = surface.get_stride()

        image = Image.frombuffer('RGBA', (w, h), data, 'raw', 'RGBA', 0, 1).copy()
        if colormode == ImageUtils.COLORMODE_RGBA:
            ImageUtils.swap_red_blue(image)

        return image
    create_image_from_surface = Callable(create_image_from_surface)


    def create_surface_from_image(image, colormode=1):
        size = image.size
        w = size[0]
        h = size[1]

        data = array('c')

        if colormode == ImageUtils.COLORMODE_RGBA:
            ImageUtils.swap_red_blue(image)

        data.fromstring(image.tostring())
        surface = cairo.ImageSurface.create_for_data(data, cairo.FORMAT_ARGB32, w, h)

        return surface
    create_surface_from_image = Callable(create_surface_from_image)


    def swap_red_blue(image):
        size = image.size
        w = size[0]
        h = size[1]

        pixels = image.load()

        for i in range(w):
            for j in range (h):
                pixel = pixels[i, j]
                pixels[i, j] = (pixel[2], pixel[1], pixel[0], pixel[3])
    swap_red_blue = Callable(swap_red_blue)
