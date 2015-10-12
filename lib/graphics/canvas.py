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

import cairo
import gtk
import gobject


from lib.tools.generic import *
from rgbacolor import RGBAColor

class undoBuffer: 
    n_buf = 5
    cur_buf = 0
    n_buf_full = 0
    redos_allowed = 0
    Buffer = None
    width = None
    height = None
    
    def __init__(self):
        self.Buffer = [None for i in range(self.n_buf+1)]
        self.width = [0 for i in range(self.n_buf+1)]
        self.height = [0 for i in range(self.n_buf+1)]
        
    def next_buf(self):
        return (self.cur_buf+1)%(self.n_buf+1)
        
    def prev_buf(self):
        return (self.cur_buf-1)%(self.n_buf+1)
        
class senstivity_data:
    
    def __init__(self,action,sensitive):
        self.action = action
        self.sensitive = sensitive

class Canvas(gtk.DrawingArea):

    DEFAULT_CURSOR = gtk.gdk.Cursor(gtk.gdk.ARROW)
    active_tool = None
    picker_col = None
    bg_init=None
    bg_col = None
    UNDO_BUFFER = undoBuffer()
    


    def __init__(self):
        # Initializing gtk.DrawingArea superclass
        super(Canvas, self).__init__()

        # Registering events
        self.add_events(gtk.gdk.BUTTON_PRESS_MASK | gtk.gdk.BUTTON_RELEASE_MASK | gtk.gdk.BUTTON1_MOTION_MASK | gtk.gdk.DRAG_MOTION | gtk.gdk.POINTER_MOTION_MASK)
        self.connect("button-press-event", self.button_pressed)
        self.connect("button-release-event", self.button_released)
        self.connect("motion-notify-event", self.move_event)
        self.connect("expose-event", self.expose)
        self.connect("motion-notify-event", self.motion_event)

        self.set_size(550, 412)
        self.ALPHA_PATTERN = cairo.SurfacePattern(cairo.ImageSurface.create_from_png("pixmaps/alpha-pattern.png"))
        self.ALPHA_PATTERN.set_extend(cairo.EXTEND_REPEAT)
        
        self.bg_init=0
        self.bg_col = (1, 1, 1, 1);

        # Basic tools
        self.DUMMY_TOOL = Tool(self)
        self.active_tool = self.DUMMY_TOOL

        # Surface is the image in the canvas
        self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, self.width, self.height)
        #overlay is for selection boxes - etc
        self.overlay = cairo.ImageSurface(cairo.FORMAT_ARGB32, self.width, self.height)

        #clipboard        
        self.clipboard = gtk.clipboard_get(selection="CLIPBOARD")


    def set_size(self, width, height): #Not called by fancycanvas!!
        self.width = max(width, 1)
        self.height = max(height, 1)
        self.set_size_request(self.width, self.height)

    def get_width(self):
        return self.width


    def get_height(self):
        return self.height


    def set_active_tool(self, tool):
        self.active_tool = tool


    def button_pressed(self, widget, event):
        if event.type == gtk.gdk.BUTTON_PRESS:
            self.active_tool.begin(event.x, event.y,event.button)
            


    def button_released(self, widget, event):
        self.active_tool.end(event.x, event.y)
        self.swap_buffers()
        self.active_tool.commit()
        if self.active_tool.name == "ColorPicker":
            col = self.active_tool.col
            self.picker_col =  RGBAColor(col[2], col[1], col[0], col[3])
            self.emit("color_pick_event", event)
        

    def move_event(self, widget, event):
        #context = widget.window.cairo_create()
        self.active_tool.move(event.x, event.y)
        if self.active_tool.name == "ColorPicker" and  self.active_tool.mode == self.active_tool.DRAWING:
            col = self.active_tool.col
            self.picker_col =  RGBAColor(col[2], col[1], col[0], col[3])
            self.emit("color_pick_event", event)
        else:
            self.swap_buffers()
        
    def motion_event(self, widget, event):
        self.active_tool.select()
        if event.x > self.width or event.y > self.height:
            self.window.set_cursor(self.DEFAULT_CURSOR)


    def swap_buffers(self):
        rect = gtk.gdk.Rectangle(0, 0, self.width, self.height)
        self.window.invalidate_rect(rect, True) #invalidating the rectangle forces gtk to run expose.

    def expose(self, widget, event): # Run when buffers are swapped: updates screen.
        #temporary surface size of canvas
        tmp_surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, self.width, self.height)
        context = cairo.Context(tmp_surf)
        #draw to this temporary surface
        self.draw(context)
        #get widget window as context
        wincontext = widget.window.cairo_create()
        #clip to image size
        wincontext.rectangle(0, 0, self.width, self.height)
        wincontext.clip()
        #paint alpha pattern over whole clipped region
        wincontext.set_source(self.ALPHA_PATTERN)
        wincontext.paint()
        #paint 
        wincontext.set_source_surface(tmp_surf)
        wincontext.paint()
        #overlay 
        wincontext.set_source_surface(self.overlay)
        wincontext.paint()

    def print_tool(self):
        self.clear_overlay()
        #temporary surface size of canvas
        tmp_surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, self.width, self.height)
        context = cairo.Context(tmp_surf)
        #draw to temporary surface
        self.draw(context)
        self.surface = tmp_surf #surface now swapped with updated surface

    def draw(self, context):
        # Drawing the background
        self.__draw_background(context)
        #Draw the current surface over the background
        context.set_source_surface(self.surface)
        context.paint()
        #Draw any active tool if applicable.
        if self.active_tool.Draw2Overlay:
            ov_context = cairo.Context(self.overlay)
            self.active_tool.draw(ov_context)
        else:
            self.active_tool.draw(context)

    def __draw_background(self, context):
        #if the background has never been initialsed (first print) then
        #fill whole canvas, else fill new regions
        if self.bg_init==0:
            context.rectangle(0, 0, self.width, self.height)
            self.bg_init=1
        else:
            context.rectangle(self.surface.get_width(), 0, self.width-self.surface.get_width(), self.height)
            context.rectangle(0, self.surface.get_height(), self.width, self.height-self.surface.get_height())
        context.set_source_rgba(self.bg_col[0], self.bg_col[1], self.bg_col[2], self.bg_col[3])
        context.fill()
        
    def clear_overlay(self):
        #temporary surface size of canvase
        tmp_surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, self.width, self.height)
        context= cairo.Context(tmp_surf)
        #paint surface transparent
        context.rectangle(0, 0, self.width, self.height)
        context.set_source_rgba(0, 0, 0, 0)
        context.fill()
        #set as overlay
        self.overlay = tmp_surf

    def get_image(self):
        return self.surface


    def set_image(self, surface):
        self.surface = surface
        self.set_size(surface.get_width(), surface.get_height())

        
    def get_color(self):
        return self.picker_col
        
    def undo(self):    
        if self.UNDO_BUFFER.n_buf_full>0:
            self.update_undo_buffer(0)
            buf = self.UNDO_BUFFER.prev_buf()
            data = self.surface.get_data()
            w = self.surface.get_width()
            h = self.surface.get_height()
            bw = self.UNDO_BUFFER.width[buf]
            bh = self.UNDO_BUFFER.height[buf]
            if bh!=h | bw!=w:
                self.set_size(bw,bh)
                self.print_tool()
                data = self.surface.get_data()
            data[:] = self.UNDO_BUFFER.Buffer[buf][:]
            self.UNDO_BUFFER.n_buf_full -=1
            if self.UNDO_BUFFER.redos_allowed<self.UNDO_BUFFER.n_buf:
                self.UNDO_BUFFER.redos_allowed += 1
            self.UNDO_BUFFER.cur_buf = buf
            self.swap_buffers()
            self.emit("change_sensitivty", senstivity_data('redo',True))
            if self.UNDO_BUFFER.n_buf_full==0:
                self.emit("change_sensitivty", senstivity_data('undo',False))
            
    
    def redo(self):
        if self.UNDO_BUFFER.redos_allowed>0:
            buf = self.UNDO_BUFFER.next_buf()
            data = self.surface.get_data()
            w = self.surface.get_width()
            h = self.surface.get_height()
            bw = self.UNDO_BUFFER.width[buf]
            bh = self.UNDO_BUFFER.height[buf]
            if bh!=h | bw!=w:
                self.set_size(bw,bh)
                self.print_tool()
                data = self.surface.get_data()
            data[:] = self.UNDO_BUFFER.Buffer[buf][:]
            self.UNDO_BUFFER.redos_allowed -=1
            self.UNDO_BUFFER.n_buf_full +=1
            self.UNDO_BUFFER.cur_buf = buf
            self.swap_buffers()
            self.emit("change_sensitivty", senstivity_data('undo',True))
            if self.UNDO_BUFFER.redos_allowed==0:
                self.emit("change_sensitivty", senstivity_data('redo',False))
                
        
    def update_undo_buffer(self,iterate):
        w = self.surface.get_width()
        h = self.surface.get_height()
        s = self.surface.get_stride()
        data = self.surface.get_data()
        buf = self.UNDO_BUFFER.cur_buf
        self.UNDO_BUFFER.Buffer[buf] = create_string_buffer(s*h)
        self.UNDO_BUFFER.Buffer[buf][:] = data[:]    
        self.UNDO_BUFFER.width[buf] = w
        self.UNDO_BUFFER.height[buf] = h
        if iterate==1:
            self.emit("change_sensitivty", senstivity_data('undo',True))
            self.emit("change_sensitivty", senstivity_data('redo',False))
            self.UNDO_BUFFER.redos_allowed = 0
            if self.UNDO_BUFFER.n_buf_full<self.UNDO_BUFFER.n_buf:
                self.UNDO_BUFFER.n_buf_full += 1
            self.UNDO_BUFFER.cur_buf = self.UNDO_BUFFER.next_buf()
        
    def copy(self):
        data = self.surface.get_data()
        t_data=list(data)
        t_data[::4] = data[2::4]
        t_data[2::4] = data[::4]
        t_data = ''.join(t_data)
        s = self.surface.get_stride()
        w = self.surface.get_width()
        h = self.surface.get_height()
        PixBuf =  gtk.gdk.pixbuf_new_from_data(t_data,gtk.gdk.COLORSPACE_RGB, True, 8, w,h,s)
        
        self.clipboard.set_image(PixBuf)
    
    def paste(self):
        image = self.clipboard.wait_for_image();
        if image != None:
            self.set_size(max(self.width,image.get_width()), max(self.height,image.get_height()))
            self.print_tool()
            aux = cairo.ImageSurface(cairo.FORMAT_ARGB32, image.get_width(), image.get_height())
            im_data = image.get_pixels()
            # the next two semingly useless lines give the surface real pixels to be edited.
            context = cairo.Context(aux)
            context.paint() 
            #directly write to the pixels in aux
            data = aux.get_data()
            #pasted image has alpha channel
            if image.get_rowstride()==aux.get_stride():
                data[2::4] = im_data[0::4]#red
                data[0::4] = im_data[2::4] #blue
                data[1::4] = im_data[1::4] #green
                data[3::4] = im_data[3::4] #alpha
            else: #pasted data no alpha channel
                data[2::4] = im_data[0::3]#red
                data[0::4] = im_data[2::3] #blue
                data[1::4] = im_data[1::3] #green
            #use cairo to add the pasted image to the current image
            context = cairo.Context(self.surface)
            context.set_source_surface(aux, 0, 0)
            context.paint()
            self.swap_buffers()



gobject.signal_new("color_pick_event", Canvas, gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,))
# change whether GUI icons are enabled
gobject.signal_new("change_sensitivty", Canvas, gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,))