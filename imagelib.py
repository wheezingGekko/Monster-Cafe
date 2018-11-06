import kivy
kivy.require('1.10.1')

from kivy.uix.image import Image
from kivy.properties import NumericProperty, StringProperty
from kivy.vector import Vector

import math

from debugger import Debug

# TODO  When searching for the colored pixel, use binary search algo for 
#       optimization
#
# TODO  Possibly make an all-around function encapsulating the search for
#       the non-transparent pixel beginning
#
# TODO  Increase hit-box for collision when interacting with characters vs
#       interacting with objects


class OverlappingImage(Image):
    ''' Class handling images that can sense if another image is 
    overlapping it, doing so by calculating the transparency around
    each image
    '''

    STRETCH = 1
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._stretch = self.STRETCH + 1


    def _init_transparency(self):
        ''' initializes approximates of transparent padding around image,
        accomodating for stretch 
        '''
        self.left_pad = self._find_left_pixel() * self._stretch
        self.right_pad = self._find_right_pixel() * self._stretch
        self.top_pad = self._find_top_pixel() * self._stretch


    def _find_left_pixel(self):
        ''' locate first colored pixel on image's left '''
        true_left = self._coreimage.width
        for y in range(self._coreimage.height):
            for x in range(self._coreimage.width):
                if (self._coreimage.read_pixel(x, y)[-1] > 0.5
                        and x < true_left):
                    true_left = x
                    continue
        return true_left


    def _find_right_pixel(self):
        ''' locate first colored pixel on image's right '''
        true_right = -1
        for y in range(self._coreimage.height):
            for x in range(self._coreimage.width - 1, -1, -1):
                if (self._coreimage.read_pixel(x, y)[-1] > 0.5
                        and x > true_right):
                    true_right = x
                    continue
                # we no longer iterate if we are within the image
                elif (self._coreimage.read_pixel(x, y)[-1] > 0.5
                        and x <= true_right):
                    break
        return self._coreimage.width - true_right

 
    def _find_top_pixel(self):
        ''' locate first colored pixel on image's top '''
        true_top = -1
        for x in range(self._coreimage.width):
            for y in range(self._coreimage.height - 1, -1, -1):
                if (self._coreimage.read_pixel(x, y)[-1] > 0.5
                        and y > true_top):
                    true_top = y
                    continue
                # we no longer iterate if we are within the image
                elif (self._coreimage.read_pixel(x, y)[-1] > 0.5
                        and y <= true_top):
                    break
        return self._coreimage.height - true_top


    def _in_widget_horizontal(self, widget, leeway):
        ''' returns true or false if within a widget's x-axis 
        
        Keyword arguments:
        widget  -- the widget to compare to
        '''
        widget_left = widget.x + widget.left_pad - leeway
        widget_right = widget.right - widget.right_pad + leeway
        self_left = self.x + self.left_pad - leeway
        self_right = self.right - self.right_pad + leeway

        overlapping_right = widget_left <= self_left < widget_right
        overlapping_left = widget_left <= self_right < widget_right
        overlapping_on = (self_right > widget_right 
                             and self_left < widget_left)
                             
        return (overlapping_right or overlapping_left or overlapping_on)


    def _in_widget_vertical(self, widget, leeway):
        ''' returns true or false if within a widget's y-axis 

        Keyword arguments:
        widget  -- the widget to compare to
        '''
        widget_y = widget.y - leeway
        widget_top = widget.top - widget.top_pad + leeway
        self_y = self.y - leeway
        self_top = self.top - self.top_pad + leeway

        overlapping_above = widget_y <= self_y < widget_top
        overlapping_below = widget_y <= self_top < widget_top
        overlapping_on = (self_y < widget_y and self_top > widget_top)

        return (overlapping_above or overlapping_below or overlapping_on)


    def build(self):
        self._init_transparency()
        self.width = self._coreimage.width * self.STRETCH
        self.height = self._coreimage.height * self.STRETCH

    
    def is_overlapping(self, widget, leeway=0):
        ''' checks if it's overlapping another widget's "hitbox"
        
        Keyword arguments:
        widget  -- the widget to compare to
        '''
        if (self._in_widget_horizontal(widget, leeway) 
                and self._in_widget_vertical(widget, leeway)):
            return True


class LoopingImage(Image):
    ''' Class of animations composed by looping images '''
    CYCLE_LENGTH = 4

    image_name = StringProperty('')
    image_num = NumericProperty(0)


    def update_image(self):
        ''' moves image to next image state via number suffixes of the file '''
        self.image_num = (self.image_num + 1) % self.CYCLE_LENGTH


class FloatingImage(Image):
    ''' class of images translated up or down for an amount of pixels '''
    # how fast the item will move up and down
    CYCLE_SPEED = 5
    # how many pixels the item will be displaced
    CYCLE_LENGTH = 10
    UP = 1
    DOWN = -1

    item_name = StringProperty('')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.image_num = 0
        self.movement_direction = self.UP


    def update_image(self):
        ''' float image up or down '''
        self.image_num = (self.image_num + 1) % self.CYCLE_LENGTH

        # once we reach the minimum or maximum of the float, we flip
        # the direction of the movement
        if self.image_num == 0:
            self.movement_direction = -self.movement_direction

        self.y += self.movement_direction