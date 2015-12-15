#    This file is part of Dappy - Draw And Paint in Python
#    Copyright (C) 2015 Julian Stirling
#
#    Dappy was forked from Painthon, listed on Google code as GPL v2,
#    copyright holder unknown.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>


import gtk
import cairo
import struct
import math
from colors import RGBAColor
from ctypes import create_string_buffer

# Class
# ==============================================================================
class Tool(gtk.Object):
    READY = 0
    DRAWING = 1
    EDITING = 2
    name = 'NotSet'
    Draw2Overlay = False
    CURSOR = None

    def __init__(self, canvas):
        self.canvas = canvas
        self.mode = self.READY
        self.set_cursor()

    def set_cursor(self):
        self.CURSOR = gtk.gdk.Cursor(gtk.gdk.ARROW)

    def set_cursor_from_file(self,name,x,y):
        px_buf = gtk.gdk.pixbuf_new_from_file(name)
        pm = gtk.gdk.Pixmap(None,1,1,1)
        self.CURSOR=gtk.gdk.Cursor(pm.get_display(),px_buf,x,y)

    def move(self, x, y): pass

    def select(self):
        self.canvas.window.set_cursor(self.CURSOR)

    def begin(self, x, y,button):
        self.canvas.clear_overlay()
        self.canvas.update_undo_buffer(1)
        self.mode = self.DRAWING

    def end(self, x, y):
        self.mode = self.EDITING

    def draw(self, context): pass

    def __use_color(self, context, color):
        context.set_source_rgba(color.get_red(), color.get_green(),
           color.get_blue(), color.get_alpha())

    def __use_no_color(self, context):
        context.set_source_rgba(0,0,0,0)

    def use_primary_color(self, context, button=1):
        if button==3:
            self.__use_color(context, self.canvas.secondary)
        else:
            self.__use_color(context, self.canvas.primary)

    def use_secondary_color(self, context, button=1):
        if button==3:
            self.__use_color(context, self.canvas.primary)
        else:
            self.__use_color(context, self.canvas.secondary)

    def use_fill_color(self, context, button=1):
        if self.canvas.fig_fill_type==0:
            self.use_secondary_color(context, button)
        elif self.canvas.fig_fill_type==1:
            self.use_primary_color(context, button)
        else:
            self.__use_no_color(context)

    def commit(self):
        self.mode = self.DRAWING
        self.canvas.print_tool()
        self.mode = self.READY


# Class
# ==============================================================================
class DragAndDropTool(Tool):
    CURSOR = None

    initial_x = 0
    initial_y = 0
    final_x = 0
    final_y = 0
    m_button = None

    def set_cursor(self):
        self.CURSOR = gtk.gdk.Cursor(gtk.gdk.CROSSHAIR)

    def begin(self, x, y,button):
        Tool.begin(self, x, y,button)
        self.initial_x = x
        self.initial_y = y
        self.final_x = x
        self.final_y = y
        self.m_button=button


    def end(self, x, y):
        Tool.end(self, x, y)
        self.final_x = x
        self.final_y = y


    def move(self, x, y):
        self.final_x = x
        self.final_y = y


# Class
# ==============================================================================
class BothScalingTool(Tool):
    CURSOR = None
    name = 'BothScale'

    def set_cursor(self):
        self.CURSOR = gtk.gdk.Cursor(gtk.gdk.BOTTOM_RIGHT_CORNER)

    def begin(self, x, y,button):
        Tool.begin(self, x, y,button)

    def move(self, x, y):
        self.canvas.set_size(int(x), int(y))


# Class
# ==============================================================================
class HorizontalScalingTool(Tool):
    CURSOR = None
    name = 'HorScale'

    def begin(self, x, y,button):
        Tool.begin(self, x, y,button)

    def set_cursor(self):
        self.CURSOR = gtk.gdk.Cursor(gtk.gdk.RIGHT_SIDE)

    def move(self, x, y):
        self.canvas.set_size(int(x), self.canvas.get_height())


# Class
# ==============================================================================
class VerticalScalingTool(Tool):
    CURSOR = None
    name = 'VertScale'

    def set_cursor(self):
        self.CURSOR = gtk.gdk.Cursor(gtk.gdk.BOTTOM_SIDE)

    def begin(self, x, y,button):
        Tool.begin(self, x, y,button)

    def move(self, x, y):
        self.canvas.set_size(self.canvas.get_width(), int(y))

class ColorPickerTool(DragAndDropTool):
    name = 'ColorPicker';
    pixels = None;
    data = None;
    bpp= None;
    w = None;
    s = None;
    col = None;

    def set_cursor(self):
        self.set_cursor_from_file('Cursors/cursor-color-picker.png',1,30)

    def begin(self, x, y,button):
        self.mode = self.DRAWING
        self.m_button=button
        surface = self.canvas.get_image()
        self.w = surface.get_width()
        self.h = surface.get_height()
        self.s = surface.get_stride()
        self.bpp = self.s/self.w
        self.data = surface.get_data()
        act_px = int(y*self.s+x*self.bpp)
        col_bin = self.data[act_px:act_px+4]
        col_int = struct.unpack_from(str(self.bpp)+'B',col_bin)
        self.col = [float(i)/255 for i in col_int]

    def end(self, x, y):
        self.mode = self.READY

    def move(self, x, y):
        if self.mode == self.DRAWING:
            if x<self.w and y<self.h and x>=0 and y>=0:
                act_px = int(y*self.s+x*self.bpp)
                col_bin = self.data[act_px:act_px+4]
                col_int = struct.unpack_from(str(self.bpp)+'B',col_bin)
                self.col = [float(i)/255 for i in col_int]


class BucketFillTool(Tool):
    name = 'BucketFill';

    def set_cursor(self):
        self.set_cursor_from_file('Cursors/cursor-bucket-fill.png',1,35)

    def begin(self, x, y,button):
        Tool.begin(self, x, y,button)
        self.mode = self.DRAWING
        surface = self.canvas.get_image()
        w = surface.get_width()
        h = surface.get_height()
        s = surface.get_stride()
        bpp = s/w
        data = surface.get_data()

        if button==3:
            pc=self.canvas.secondary
        else:
            pc = self.canvas.primary
        act_px = int(y*s+x*bpp)
        orr_c = data[act_px:act_px+bpp]
        rep_c = create_string_buffer(bpp)
        struct.pack_into(str(bpp)+'B',rep_c,0,int(pc.get_alpha()*pc.get_blue()*255), int(pc.get_alpha()*pc.get_green()*255),
                         int(pc.get_alpha()*pc.get_red()*255), int(pc.get_alpha()*255))

        if orr_c != rep_c[0:bpp]:
            pxstack = [-1] * (h*w*bpp)
            pxstack[0] = act_px
            readc=0
            writec=1
            while pxstack[readc]!=-1:
                act_px = pxstack[readc]
                readc+=1
                if data[act_px:act_px+bpp]==orr_c:
                    data[act_px:act_px+bpp]=rep_c
                    if act_px-s>=0:
                        pxstack[writec]=(act_px-s)
                        writec+=1
                    if act_px+s<s*h:
                        pxstack[writec]=(act_px+s)
                        writec+=1
                    if (act_px+bpp)%s!=0:
                        pxstack[writec]=(act_px+bpp)
                        writec+=1
                    if (act_px-bpp)%s!=s-bpp:
                        pxstack[writec]=(act_px-bpp)
                        writec+=1
        self.mode = self.READY

class PencilTool(DragAndDropTool):
    points = None
    name = 'Pencil'

    def set_cursor(self):
        self.CURSOR = gtk.gdk.Cursor(gtk.gdk.PENCIL)

    def begin(self, x, y,button):
        DragAndDropTool.begin(self, x, y,button)
        self.points = list()
        self.points.insert(len(self.points), (x, y))

    def move(self, x, y):
        if self.mode == self.DRAWING:
            self.points.insert(len(self.points), (x, y))

    def end(self, x, y):
        self.points.insert(len(self.points), (x, y))

    def draw(self, context):
        if self.mode == self.READY:
            return

        context.set_antialias(cairo.ANTIALIAS_NONE)
        context.set_line_cap(cairo.LINE_CAP_ROUND)
        context.set_line_join(cairo.LINE_JOIN_ROUND)
        context.move_to(self.initial_x, self.initial_y)
        if self.m_button==3:
            self.use_secondary_color(context)
        else:
            self.use_primary_color(context)

        for point in self.points:
            context.line_to(point[0], point[1])
        context.stroke()

class EraserTool(PencilTool):
    name = 'Eraser'

    def set_cursor(self):
        pm = gtk.gdk.Pixmap(None,10,10,1)
        bg = pm.new_gc(foreground=gtk.gdk.colormap_get_system().alloc_color('black'))
        fg = pm.new_gc(foreground=gtk.gdk.colormap_get_system().alloc_color('white'))
        pm.draw_rectangle(bg,True,0,0,10,10)
        pm.draw_rectangle(fg,False,0,0,9,9)
        self.CURSOR=gtk.gdk.Cursor(pm,pm,gtk.gdk.Color(),gtk.gdk.Color(),5,5)


    def begin(self, x, y,button):
        super(EraserTool, self).begin(x, y,button)
        #start line
        self.points.insert(len(self.points), (x, y+4))
        self.points.insert(len(self.points), (x, y-4))
        self.points.insert(len(self.points), (x, y))

    def draw(self, context):
        if self.mode == self.READY:
            return

        context.set_antialias(cairo.ANTIALIAS_NONE)
        context.set_line_cap(cairo.LINE_CAP_BUTT)
        context.set_line_join(cairo.LINE_JOIN_MITER)
        context.move_to(self.initial_x, self.initial_y)
        context.set_line_width(8)
        self.use_secondary_color(context,self.m_button)
        for point in self.points:
            context.line_to(point[0], point[1])
        context.set_operator(cairo.OPERATOR_SOURCE)
        context.stroke()

class PaintbrushTool(PencilTool):
    name = 'PaintBrush'

    def set_cursor(self):
        self.set_cursor_from_file('Cursors/cursor-paintbrush.png',18,35)

    def draw(self, context):
        if self.mode == self.READY:
            return

        context.set_line_cap(cairo.LINE_CAP_ROUND)
        context.set_line_join(cairo.LINE_JOIN_ROUND)
        context.move_to(self.initial_x, self.initial_y)
        context.set_line_width(8)
        self.use_primary_color(context,self.m_button)
        for point in self.points:
            context.line_to(point[0], point[1])
        context.stroke()

class AirBrushTool(PencilTool):
    name = 'AirBrush'
    Brush = None
    Brush_off = None
    Brush_rep = None
    scale = None

    def set_cursor(self):
        self.set_cursor_from_file('Cursors/cursor-airbrush.png',20,35)

    def begin(self, x, y,button):
        super(AirBrushTool, self).begin(x, y,button)
        self.Brush = cairo.ImageSurface.create_from_png("Brushes/AirBrush.png")
        if button==3:
            pc=self.canvas.secondary
        else:
            pc = self.canvas.primary
        a = pc.get_alpha()
        r = pc.get_red()
        g = pc.get_green()
        b = pc.get_blue()
        Brush_w = self.Brush.get_width()
        self.Brush_off =  Brush_w/2.0
        self.Brush_rep =  Brush_w/10
        data = self.Brush.get_data()
        for n in range(Brush_w**2):
            al_bin = data[n*4+3]
            al_int = struct.unpack_from(str(1)+'B',al_bin)
            al = float(al_int[0])/255
            px = create_string_buffer(4)
            alph = al*a
            struct.pack_into(str(4)+'B',px,0,int(alph*b*255), int(alph*g*255),int(alph*r*255), int(alph*255))
            data[n*4:(n+1)*4] = px
        self.scale =  self.canvas.airbrush_width/Brush_w


    def move(self, x, y):
        if self.mode == self.DRAWING:
            xd = x-self.points[-1][0]
            yd = y-self.points[-1][1]
            dist = (((xd)**2 + (yd)**2)**0.5)/self.scale
            if dist>self.Brush_rep:
                n = int(dist/self.Brush_rep)
                xd /= n
                yd /= n
                x = self.points[-1][0]
                y = self.points[-1][1]
                self.points = list()
                for i in range(n):
                    x+=xd
                    y+=yd
                    self.points.insert(len(self.points), (x, y))
            else:
                self.points = list()
                self.points.insert(len(self.points), (x, y))

    def draw(self, context):
        if self.mode == self.READY:
            return
        context.scale(self.scale,self.scale)
        for n in range(len(self.points)):
            context.set_source_surface(self.Brush, (self.points[n][0])/self.scale-self.Brush_off, (self.points[n][1])/self.scale-self.Brush_off)
            context.paint()


class StraightLineTool(DragAndDropTool):
    name = 'StraightLine';
    def draw(self, context):
        if self.mode == self.READY:
            return

        context.move_to(self.initial_x, self.initial_y)
        context.line_to(self.final_x, self.final_y)
        self.use_primary_color(context,self.m_button)
        context.stroke()


class RectangleTool(DragAndDropTool):
    name = 'Rectangle'
    def draw(self, context):
        if self.mode == self.READY:
            return

        w = self.final_x - self.initial_x
        h = self.final_y - self.initial_y
        context.rectangle(self.initial_x, self.initial_y, w, h)
        self.use_fill_color(context,self.m_button)
        context.fill_preserve()
        self.use_primary_color(context,self.m_button)
        context.set_line_width(self.canvas.figure_linewidth)
        context.stroke()


class RoundedRectangleTool(DragAndDropTool):
    name = 'RoundedRectangle'
    def draw(self, context):
        if self.mode == self.READY:
            return

        R = self.canvas.figure_corner_radius
        xfac = 1
        yfac = 1
        w = abs(self.final_x - self.initial_x)
        h = abs(self.final_y - self.initial_y)
        if self.initial_x > self.final_x:
            xfac = -1
        if self.initial_y > self.final_y:
            yfac = -1
        clk = xfac==yfac
        a=-yfac*math.pi/2.0
        R = min(R,min(w,h)/2)
        initial_xc = self.initial_x+xfac*R
        final_xc = self.final_x-xfac*R
        initial_yc = self.initial_y+yfac*R
        final_yc = self.final_y-yfac*R

        context.move_to(final_xc,self.initial_y)
        a = self.corner(context,final_xc,initial_yc,R,a,clk)
        context.line_to(self.final_x,final_yc)
        a = self.corner(context,final_xc,final_yc,R,a,clk)
        context.line_to(initial_xc,self.final_y)
        a = self.corner(context,initial_xc,final_yc,R,a,clk)
        context.line_to(self.initial_x,initial_yc)
        a = self.corner(context,initial_xc,initial_yc,R,a,clk)
        context.close_path()
        self.use_fill_color(context,self.m_button)
        context.fill_preserve()
        self.use_primary_color(context,self.m_button)
        context.save()
        context.set_line_width(self.canvas.figure_linewidth)
        context.stroke()
        context.restore()

    def corner(self,context,x,y,R,a1,clk):
        if clk:
            a = a1+math.pi/2.0
            context.arc(x,y,R,a1,a)
        else:
            a = a1-math.pi/2.0
            context.arc_negative(x,y,R,a1,a)
        return a

class EllipseTool(DragAndDropTool):
    name = 'Ellipse'
    def draw(self, context):
        if self.mode == self.READY:
            return

        w = self.final_x - self.initial_x
        h = self.final_y - self.initial_y

        if w!=0 and h !=0:
            context.save()
            context.translate(self.initial_x + w/2., self.initial_y + h/2.)
            context.scale(w/2., h/2.)
            context.arc(0., 0., 1., 0., 2 * math.pi)
            self.use_fill_color(context,self.m_button)
            context.fill_preserve()
            context.restore()
            if self.m_button==3:
                self.use_secondary_color(context)
            else:
                self.use_primary_color(context)
            #context.set_antialias(cairo.ANTIALIAS_NONE)
        else:
            self.use_primary_color(context,self.m_button)
            context.set_antialias(cairo.ANTIALIAS_NONE)
            context.move_to(self.initial_x, self.initial_y)
            context.line_to(self.final_x, self.final_y)
        context.set_line_width(self.canvas.figure_linewidth)
        context.stroke()

class RectangleSelectTool(DragAndDropTool):
    name = 'RectSelect'
    Draw2Overlay = True
    w=None
    h=None

    def begin(self, x, y,button):
        self.canvas.clear_overlay()
        #don't update undo buffer
        self.mode = self.DRAWING
        self.initial_x = x
        self.initial_y = y
        self.final_x = x
        self.final_y = y

    def draw(self,context):
        if self.mode == self.READY:
            return
        self.w = self.final_x - self.initial_x
        self.h = self.final_y - self.initial_y
        if abs(self.w)>0 and abs(self.h)>0:
            context.set_operator(cairo.OPERATOR_SOURCE)
            context.set_line_width(1)
            context.set_antialias(cairo.ANTIALIAS_NONE)
            context.rectangle(0, 0, self.canvas.width, self.canvas.height)
            context.set_source_rgba(0, 0, 0, 0)
            context.fill()
            context.set_operator(cairo.OPERATOR_OVER)
            context.rectangle(self.initial_x, self.initial_y, self.w, self.h)
            context.set_dash((5,5))
            context.set_source_rgba(0,0,1,1)
            context.stroke()
            context.rectangle(self.initial_x, self.initial_y, self.w, self.h)
            context.set_dash((5,5),5)
            context.set_source_rgba(1,1,0,1)
            context.stroke()
        else:
            self.canvas.clear_overlay()

    def commit(self):
        self.mode = self.READY
        if abs(self.w)>0 and abs(self.h)>0:
            self.canvas.set_selection(True)
            self.canvas.select_xp = [self.initial_x,self.initial_x,self.final_x,self.final_x]
            self.canvas.select_yp = [self.initial_y,self.final_y,self.initial_y,self.final_y]
        else:
            self.canvas.set_selection(False)