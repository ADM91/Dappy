from array import array
import Image
import struct
from ctypes import create_string_buffer


from generic import Tool
from generic import DragAndDropTool
from lib.graphics.imageutils import ImageUtils

import time

class ColorPickerTool(DragAndDropTool):
    pixels = None


    def begin(self, x, y):
        self.mode = self.DRAWING
        self.pixels = ImageUtils.create_image_from_surface(self.canvas.CANVAS).load()
        print self.pixels[x, y]


    def end(self, x, y):
        self.mode = self.READY
        print self.pixels[x, y]


    def move(self, x, y):
        if self.mode == self.DRAWING:
            print self.pixels[x, y]



class BucketFillTool(Tool):
    def begin(self, x, y):
              
        self.mode = self.DRAWING
        surface = self.canvas.get_image()

        w = surface.get_width()
        h = surface.get_height()
        s = surface.get_stride()
        bpp = s/w;
        data = surface.get_data()
        
        pc = self.primary   
        act_px = int(y*s+x*bpp)      
        orr_c = data[act_px:act_px+4]
        rep_c = create_string_buffer(4)
        struct.pack_into(str(bpp)+'B',rep_c,0,int(pc.get_blue()*255), int(pc.get_green()*255),
                         int(pc.get_red()*255), int(pc.get_alpha()*255))
        

        if orr_c != rep_c[0:4]:
            pxstack = [-1] * (h*w*4)
            pxstack[0] = act_px
            readc=0
            writec=1
            while pxstack[readc]!=-1:
                act_px = pxstack[readc]
                readc+=1
                if data[act_px:act_px+4]==orr_c:
                    data[act_px:act_px+4]=rep_c
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
    
