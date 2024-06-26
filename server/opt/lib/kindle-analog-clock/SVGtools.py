#!/usr/bin/env python3
# encoding=utf-8
# -*- coding: utf-8 -*-

class format:
    def __init__(self, encoding, height, width, font, _svg):
        self.encoding = encoding
        self.height = height
        self.width = width
        self.font = font
        self._svg = _svg
        
    def svg(self):
        a = f'''<?xml version="1.0" encoding="{self.encoding}"?>
<svg xmlns="http://www.w3.org/2000/svg" height="{self.height}" width="{self.width}" version="1.1" xmlns:xlink="http://www.w3.org/1999/xlink">
<g font-family="{self.font}">
{self._svg}
</g></svg>\n'''
        return a

# Reguler font
class text:
    def __init__(self, anchor, fontsize, x, y, v, stroke=None):
        self.anchor = anchor
        self.fontsize = fontsize
        self.x = x
        self.y = y
        self.v = v
        self.stroke = stroke

    def svg(self):
        if not self.stroke == None:
            return '<text style="text-anchor:{};" font-size="{}px" x="{}" y="{}" stroke="{}" fill="{}">{}</text>\n'.\
                   format(self.anchor, self.fontsize, self.x, self.y, self.stroke, self.stroke, self.v)
        else:
            return '<text style="text-anchor:{};" font-size="{}px" x="{}" y="{}">{}</text>\n'.\
                   format(self.anchor, self.fontsize, self.x, self.y, self.v)

# Bold font
class text2:
    def __init__(self, anchor, fontweight, fontsize, x, y, v):
        self.anchor = anchor
        self.fontweight = fontweight
        self.fontsize = fontsize
        self.x = x
        self.y = y
        self.v = v

    def svg(self):
        return '<text style="text-anchor:{};" font-weight="{}" font-size="{}px" x="{}" y="{}">{}</text>\n'.\
               format(self.anchor, self.fontweight, self.fontsize, self.x, self.y, self.v)


class circle:
    def __init__(self, cx, cy, r, stroke, width, fill='none'):
        self.cx = cx
        self.cy = cy
        self.r = r
        self.stroke = stroke
        self.width = width
        self.fill = fill

    def svg(self):
        return '<circle cx="{}" cy="{}" r="{}" stroke="{}" stroke-width="{}" fill="{}"/>\n'.\
               format(self.cx, self.cy, self.r, self.stroke, self.width, self.fill)


class line:
    def __init__(self, x1, x2, y1, y2, style):
        self.x1 = x1
        self.x2 = x2
        self.y1 = y1
        self.y2 = y2
        self.style = style

    def svg(self):
        return '<line x1="{}" x2="{}" y1="{}" y2="{}" style="{}"/>\n'.\
                format(self.x1, self.x2, self.y1, self.y2, self.style)


class transform:
    def __init__(self, matrix, obj):
        self.matrix = matrix
        self.obj = obj

    def svg(self):
        return f'<g transform="matrix{self.matrix}">{self.obj}</g>\n'


class polyline:
    def __init__(self, points, style):
        self.points = points
        self.style = style

    def svg(self):
        return f'<polyline points="{self.points}" style="{self.style}"/>\n'


class rect:
    def __init__(self, x, y, width, height, style):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.style = style

    def svg(self):
        return '<rect x="{}" y="{}" width="{}" height="{}" style="{}"/>\n'.format(self.x, self.y, self.width, self.height, self.style)


class path:
    def __init__(self, d, style):
        self.d = d
        self.style = style

    def svg(self):
        return '<path d="{}" style="{}"/>\n'.format(self.d, self.style)

