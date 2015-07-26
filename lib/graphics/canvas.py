import cairo
import gtk
import math

from lib.tools.generic import *

class Canvas(gtk.DrawingArea):
    TRANSPARENT_IMAGE = 0
    OPAQUE_IMAGE = 1

    DEFAULT_CURSOR = gtk.gdk.Cursor(gtk.gdk.ARROW)
    active_tool = None
    printing_tool = False
    image_type = 0

    def __init__(self):
        # Initializing superclass
        super(Canvas, self).__init__()

        # Registering events
        self.add_events(gtk.gdk.BUTTON_PRESS_MASK | gtk.gdk.BUTTON_RELEASE_MASK | gtk.gdk.BUTTON1_MOTION_MASK | gtk.gdk.DRAG_MOTION | gtk.gdk.POINTER_MOTION_MASK)
        self.connect("button-press-event", self.button_pressed)
        self.connect("button-release-event", self.button_released)
        self.connect("motion-notify-event", self.move_event)
        self.connect("expose-event", self.expose)
        self.connect("motion-notify-event", self.motion_event)

        self.set_size(550, 412)
        self.image = cairo.ImageSurface.create_from_png("examples/flower.png")
        self.ALPHA_PATTERN = cairo.SurfacePattern(cairo.ImageSurface.create_from_png("pixmaps/alpha-pattern.png"))
        self.ALPHA_PATTERN.set_extend(cairo.EXTEND_REPEAT)

        # Basic tools
        self.DUMMY_TOOL = Tool(self)
        self.active_tool = self.DUMMY_TOOL

        # Final canvas
        self.CANVAS = cairo.ImageSurface(cairo.FORMAT_ARGB32, self.width, self.height)


    def reset(self, context):
        # Clipping to draw area
        context.rectangle(0, 0, self.width, self.height)
        context.clip()


    def set_size(self, width, height):
        self.width = max(width, 1)
        self.height = max(height, 1)
        self.set_size_request(self.width, self.height)


    def get_width(self):
        return self.width


    def get_height(self):
        return self.height


    def set_active_tool(self, tool):
        self.active_tool = tool


    def expose(self, widget, event):
        context = widget.window.cairo_create()

        self.draw(context)


    def button_pressed(self, widget, event):
        self.active_tool.begin(event.x, event.y)


    def button_released(self, widget, event):
        self.active_tool.end(event.x, event.y)
        self.swap_buffers()
        self.active_tool.commit()


    def move_event(self, widget, event):
        context = widget.window.cairo_create()
        self.active_tool.move(event.x, event.y)
        self.swap_buffers()


    def motion_event(self, widget, event):
        self.active_tool.select()
        if event.x > self.width or event.y > self.height:
            self.window.set_cursor(self.DEFAULT_CURSOR)


    def print_tool(self):
        aux = cairo.ImageSurface(cairo.FORMAT_ARGB32, self.width, self.height)
        context = cairo.Context(aux)
        self.printing_tool = True
        self.draw(context)
        self.CANVAS = aux
        self.printing_tool = False


    def draw(self, context):
        # Clipping area
        self.reset(context)

        # Drawing the background
        if not self.printing_tool:
            self.__draw_background(context)

        if self.image_type == self.OPAQUE_IMAGE and self.printing_tool:
            self.__draw_background(context)

        # Draw the result
        self.reset(context)

        source = context.get_source()
        context.set_source_surface(self.CANVAS)
        context.paint()
        context.set_source(source)

        self.active_tool.draw(context)


    def __draw_background(self, context):
        context.rectangle(0, 0, self.width, self.height)
        if self.image_type == self.TRANSPARENT_IMAGE:
            context.set_source(self.ALPHA_PATTERN)
            context.paint()
        else:
            context.set_source_rgb(1, 1, 1)
            context.fill()


    def swap_buffers(self):
        rect = gtk.gdk.Rectangle(0, 0, self.width, self.height)
        self.window.invalidate_rect(rect, True)


    def get_image(self):
        return self.CANVAS


    def set_image(self, surface):
        self.CANVAS = surface
        self.set_size(surface.get_width(), surface.get_height())


    def set_image_type(self, image_type):
        self.image_type = image_type
