import gtk
from lib.misc.utils import Callable

class RGBAColor:

    def __init__(self, red=0, green=0, blue=0, alpha=1):
        self.set_rgba(red, green, blue, alpha)


    def get_red(self):
        return self.red


    def get_green(self):
        return self.green


    def get_blue(self):
        return self.blue


    def get_alpha(self):
        return self.alpha


    def set_red(self, red):
        self.red = max(min(red, 1), 0)


    def set_green(self, green):
        self.green = max(min(green, 1), 0)


    def set_blue(self, blue):
        self.blue = max(min(blue, 1), 0)


    def set_alpha(self, alpha):
        self.alpha = max(min(alpha, 1), 0)


    def get_rgba(self):
        return self.red, self.green, self.blue, self.alpha


    def set_rgba(self, red, green, blue, alpha):
        self.set_red(red)
        self.set_green(green)
        self.set_blue(blue)
        self.set_alpha(alpha)


    def get_rgb(self):
        return self.red, self.green, self.blue


    def set_rgb(self, red, green, blue):
        self.set_rgba(red, green, blue, 1.0)


    def to_string(self):
        return "(" + str(self.red) + ", " + str(self.green) + ", " + str(self.blue) + ", " + str(self.alpha) + ")"


    def copy(self):
        return RGBAColor(self.red, self.green, self.blue, self.alpha)


    def to_gtk_color(self):
        # TODO: use proper values
        return gtk.gdk.color_parse("#f00")


    def create_from_gtk_color(gtk_color):
        string = gtk_color.to_string()

        red = int(string[1:5], 16) / 65535.0
        green = int(string[5:9], 16) / 65535.0
        blue = int(string[9:13], 16) / 65535.0

        return RGBAColor(red, green, blue)
    create_from_gtk_color = Callable(create_from_gtk_color)


    def color_parse(color):
        return RGBAColor.create_from_gtk_color(gtk.gdk.color_parse(color))
    color_parse = Callable(color_parse)
