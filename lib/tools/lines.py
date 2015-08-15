import cairo
import math
from generic import DragAndDropTool

class StraightLineTool(DragAndDropTool):
    name = 'StraightLine';
    def draw(self, context):
        if self.mode == self.READY:
            return

        context.move_to(self.initial_x, self.initial_y)
        context.line_to(self.final_x, self.final_y)
        if self.m_button==3:
            self.use_secondary_color(context)
        else:
            self.use_primary_color(context)
        context.stroke()
