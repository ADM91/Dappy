import cairo
import math
from generic import DragAndDropTool

class RectangleTool(DragAndDropTool):
    name = 'RoundedRectangle';
    def draw(self, context):
        if self.mode == self.READY:
            return

        w = self.final_x - self.initial_x
        h = self.final_y - self.initial_y
        context.rectangle(self.initial_x, self.initial_y, w, h)
        self.use_secondary_color(context)
        context.fill_preserve()
        self.use_primary_color(context)
        context.stroke()


class RoundedRectangleTool(DragAndDropTool):
    name = 'RoundedRectangle';
    def draw(self, context):
        if self.mode == self.READY:
            return

        w = self.final_x - self.initial_x
        h = self.final_y - self.initial_y
        context.rectangle(self.initial_x, self.initial_y, w, h)
        self.use_secondary_color(context)
        context.fill_preserve()
        self.use_primary_color(context)
        context.save()
        context.set_line_width(5)
        context.set_line_join(cairo.LINE_JOIN_ROUND)
        context.stroke()
        context.restore()


class EllipseTool(DragAndDropTool):
    name = 'Ellipse';
    def draw(self, context):
        if self.mode == self.READY:
            return

        w = self.final_x - self.initial_x
        h = self.final_y - self.initial_y
        context.save()
        context.translate(self.initial_x + w/2., self.initial_y + h/2.)
        try:
            # This statements throw an exception, but they do not affect the tool's
            # behaviour. Thus, I hide them from the user.
            context.scale(w/2., h/2.)
            context.arc(0., 0., 1., 0., 2 * math.pi)
            self.use_secondary_color(context)
            context.fill_preserve()
            context.restore()
            self.use_primary_color(context)
            context.set_antialias(cairo.ANTIALIAS_NONE)
            context.stroke()
        except cairo.Error:
            pass
