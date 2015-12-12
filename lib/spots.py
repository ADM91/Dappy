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


import struct
from ctypes import create_string_buffer


import tools


class ColorPickerTool(tools.DragAndDropTool):
    name = 'ColorPicker';
    pixels = None;
    data = None;
    bpp= None;
    w = None;
    s = None;
    col = None;


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

class BucketFillTool(tools.Tool):
    name = 'BucketFill';
    def begin(self, x, y,button):
        
        tools.Tool.begin(self, x, y,button)
        self.mode = self.DRAWING
        surface = self.canvas.get_image()

        w = surface.get_width()
        h = surface.get_height()
        s = surface.get_stride()
        bpp = s/w
        data = surface.get_data()
        
        if button==3:
            pc=self.secondary
        else:
            pc = self.primary
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
    
