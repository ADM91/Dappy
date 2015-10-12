import cairo
import gtk
import math
from canvas import Canvas
from lib.tools.generic import *
from lib.tools.figures import *

class FancyCanvas(Canvas):
    MARGIN = 0
    RSS = 0

    def __init__(self):
        # Initializing Canvas superclass
        super(FancyCanvas, self).__init__()

        # Resize Square Size
        self.RSS = 5
        # Margin (to draw shadows and resize squares)
        self.MARGIN = 20

        # Shadows to distribute around canvas (makes it more cute!)
        str = "pixmaps/bl-corner-shadow.png"
        self.BL_CORNER_SHADOW = cairo.ImageSurface.create_from_png(str)
        str = "pixmaps/tr-corner-shadow.png"
        self.TR_CORNER_SHADOW = cairo.ImageSurface.create_from_png(str)
        self.side_alpha_channels = [0.4, 0.39, 0.37, 0.32, 0.24, 0.16, 0.08, 0.04, 0.01]

        # Detecting decorations' color
        aux = gtk.Window()
        aux.realize()
        self.DECORATIONS_COLOR = aux.get_style().bg[gtk.STATE_SELECTED]

        # Basic Tools
        self.CANVAS_B_SCALER = BothScalingTool(self)
        self.CANVAS_H_SCALER = HorizontalScalingTool(self)
        self.CANVAS_V_SCALER = VerticalScalingTool(self)

        # Useful constants
        self.RIGHT_SCALING_POINT = 0
        self.CORNER_SCALING_POINT = 1
        self.BOTTOM_SCALING_POINT = 2
        self.SCALING_SIDE_POINTS_MIN_SIZE = 20

        # Previous tool (to recover from a rescale)
        self.previous_tool = self.active_tool


    def set_size(self, width, height):
        self.width = max(width, 1)
        self.height = max(height, 1)
        self.set_size_request(self.width + self.MARGIN, self.height + self.MARGIN)


    def expose(self, widget, event):
        super(FancyCanvas, self).expose(widget, event)
        # Retrieving cairo context
        context = widget.window.cairo_create()

        # Modify clipping area to draw decorations outside the canvas

        # Draw decorations
        self.__draw_shadows(context)
        self.__draw_scaling_points(context)


    def button_pressed(self, widget, event):
        self.previous_tool = self.active_tool

        # When the click is outside the canvas, a scaling point might have been
        # clicked.
        if event.x >= self.width or event.y >= self.height:
            if self.width < self.SCALING_SIDE_POINTS_MIN_SIZE and self.height < self.SCALING_SIDE_POINTS_MIN_SIZE:
                if self.__over_scaling_point(self.CORNER_SCALING_POINT, event):
                    self.active_tool = self.CANVAS_B_SCALER
                else:
                    self.active_tool = self.DUMMY_TOOL
            elif self.width < self.SCALING_SIDE_POINTS_MIN_SIZE:
                if self.__over_scaling_point(self.RIGHT_SCALING_POINT, event):
                    self.active_tool = self.CANVAS_H_SCALER
                elif self.__over_scaling_point(self.CORNER_SCALING_POINT, event):
                    self.active_tool = self.CANVAS_B_SCALER
                else:
                    self.active_tool = self.DUMMY_TOOL
            elif self.height < self.SCALING_SIDE_POINTS_MIN_SIZE:
                if self.__over_scaling_point(self.BOTTOM_SCALING_POINT, event):
                    self.active_tool = self.CANVAS_V_SCALER
                elif self.__over_scaling_point(self.CORNER_SCALING_POINT, event):
                    self.active_tool = self.CANVAS_B_SCALER
                else:
                    self.active_tool = self.DUMMY_TOOL
            else:
                if self.__over_scaling_point(self.BOTTOM_SCALING_POINT, event):
                    self.active_tool = self.CANVAS_V_SCALER
                elif self.__over_scaling_point(self.RIGHT_SCALING_POINT, event):
                    self.active_tool = self.CANVAS_H_SCALER
                elif self.__over_scaling_point(self.CORNER_SCALING_POINT, event):
                    self.active_tool = self.CANVAS_B_SCALER
                else:
                    self.active_tool = self.DUMMY_TOOL
            if self.active_tool.name != 'NotSet':
                super(FancyCanvas, self).button_pressed(widget, event)
            
        else:
            super(FancyCanvas, self).button_pressed(widget, event)


    def __over_scaling_point(self, point, event):
        if point == self.CORNER_SCALING_POINT:
            if self.width < event.x < self.width + self.RSS + 2:
                if self.height-2 < event.y < self.height + self.RSS + 3:
                    return True

        if point == self.BOTTOM_SCALING_POINT:
            if self.width/2-2 < event.x < self.width/2 + self.RSS + 2:
                if self.height < event.y < self.height + self.RSS + 3:
                    return True

        if point == self.RIGHT_SCALING_POINT:
            if self.width < event.x < self.width + self.RSS + 2:
                if self.height/2 - 2 < event.y < self.height/2 + self.RSS + 3:
                    return True

        return False



    def button_released(self, widget, event):
        super(FancyCanvas, self).button_released(widget, event)
        self.active_tool = self.previous_tool


    def motion_event(self, widget, event):
        if self.__over_scaling_point(self.CORNER_SCALING_POINT, event):
            self.CANVAS_B_SCALER.select()
        elif self.__over_scaling_point(self.RIGHT_SCALING_POINT, event):
            self.CANVAS_H_SCALER.select()
        elif self.__over_scaling_point(self.BOTTOM_SCALING_POINT, event):
            self.CANVAS_V_SCALER.select()
        else:
            super(FancyCanvas, self).motion_event(widget, event)


    def __draw_shadows(self, context):
        # Shadow displacements
        disp = 2
        csw = self.BL_CORNER_SHADOW.get_width()

        if self.width > 10:
            # Bottom left corner
            context.set_source_surface(self.BL_CORNER_SHADOW, disp, self.height)
            context.paint()

            # Bottom shadow
            context.translate(0, self.height)
            for i in range(len(self.side_alpha_channels)):
                alpha = self.side_alpha_channels[i]
                context.rectangle(disp+csw, i, self.width-disp-csw, 1)
                context.set_source_rgba(0, 0, 0, alpha)
                context.fill()
            context.translate(0, -self.height)

        if self.height > 10:
            # Top right corner
            context.set_source_surface(self.TR_CORNER_SHADOW, self.width, disp)
            context.paint()

            # Side shadow
            context.translate(self.width, 0)
            for i in range(len(self.side_alpha_channels)):
                alpha = self.side_alpha_channels[i]
                context.rectangle(i, disp+csw, 1, self.height-disp-csw)
                context.set_source_rgba(0, 0, 0, alpha)
                context.fill()
            context.translate(-self.width, 0)


    def __draw_scaling_points(self, context):
        # Set the scaling points' color

        # Right scaling point
        if self.height > self.SCALING_SIDE_POINTS_MIN_SIZE:
            self.__draw_scaling_point(context, self.width,
               int(math.floor(self.height/2)))

        # Bottom scaling point
        if self.width > self.SCALING_SIDE_POINTS_MIN_SIZE:
            self.__draw_scaling_point(context, int(math.floor(self.width/2)),
               self.height)

        # Corner scaling point
        self.__draw_scaling_point(context, self.width, self.height)


    def __draw_scaling_point(self, context, x, y):
        # Base color
        context.set_source_color(self.DECORATIONS_COLOR)
        context.rectangle(x, y, self.RSS+2, self.RSS+2)
        context.fill()

        # Darker
        context.set_source_rgba(0, 0, 0, 0.4)
        context.rectangle(x, y, self.RSS+2, self.RSS+2)
        context.fill()

        # Base color
        context.set_source_color(self.DECORATIONS_COLOR)
        context.rectangle(x, y, self.RSS+1, self.RSS+1)
        context.fill()

        # Lighter
        context.set_source_rgba(1, 1, 1, 0.4)
        context.rectangle(x, y, self.RSS+1, self.RSS+1)
        context.fill()

        # The point itself
        context.set_source_color(self.DECORATIONS_COLOR)
        context.rectangle(x+1, y+1, self.RSS, self.RSS)
        context.fill()
