import cairo
from generic import DragAndDropTool

class PencilTool(DragAndDropTool):
    points = None

    def begin(self, x, y):
        DragAndDropTool.begin(self, x, y)
        self.points = list()


    def move(self, x, y):
        if self.mode == self.DRAWING:
            self.points.insert(len(self.points), (x, y))


    def end(self, x, y):
        self.points.insert(len(self.points), (x, y))


    def draw(self, context):
        if self.mode == self.READY:
            return

        context.save()

        context.set_line_cap(cairo.LINE_CAP_ROUND)
        context.set_line_join(cairo.LINE_JOIN_ROUND)
        context.move_to(self.initial_x, self.initial_y)
        self.use_primary_color(context)
        for point in self.points:
            context.line_to(point[0], point[1])
        context.stroke()

        context.restore()



class EraserTool(PencilTool):

    def draw(self, context):
        if self.mode == self.READY:
            return

        context.save()

        context.set_line_cap(cairo.LINE_CAP_ROUND)
        context.set_line_join(cairo.LINE_JOIN_ROUND)
        context.move_to(self.initial_x, self.initial_y)
        context.set_line_width(8)
        self.use_secondary_color(context)
        for point in self.points:
            context.line_to(point[0], point[1])
        context.stroke()

        context.restore()


class PaintbrushTool(PencilTool):

    def draw(self, context):
        if self.mode == self.READY:
            return

        context.save()

        context.set_line_cap(cairo.LINE_CAP_ROUND)
        context.set_line_join(cairo.LINE_JOIN_ROUND)
        context.move_to(self.initial_x, self.initial_y)
        context.set_line_width(8)
        self.use_primary_color(context)
        for point in self.points:
            context.line_to(point[0], point[1])
        context.stroke()

        context.restore()
