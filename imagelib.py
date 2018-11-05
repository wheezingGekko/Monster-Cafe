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


    def _in_widget_horizontal(self, widget):
        ''' returns true or false if within a widget's x-axis 
        
        Keyword arguments:
        widget  -- the widget to compare to
        '''
        widget_left = widget.x + widget.left_pad
        widget_right = widget.right - widget.right_pad
        self_left = self.x + self.left_pad
        self_right = self.right - self.right_pad

        overlapping_right = widget_left <= self_left < widget_right
        overlapping_left = widget_left <= self_right < widget_right
        overlapping_on = (self_right > widget_right 
                             and self_left < widget_left)
                             
        return (overlapping_right or overlapping_left or overlapping_on)


    def _in_widget_vertical(self, widget):
        ''' returns true or false if within a widget's y-axis 

        Keyword arguments:
        widget  -- the widget to compare to
        '''
        widget_top = widget.top - widget.top_pad
        self_top = self.top - self.top_pad

        overlapping_above = widget.y <= self.y < widget_top
        overlapping_below = widget.y <= self_top < widget_top
        overlapping_on = (self.y < widget.y and self_top > widget_top)

        return (overlapping_above or overlapping_below or overlapping_on)


    def _calculate_range(self, widget, axis, mini, maxa):
        ''' In looking at overlapping images, we retrieve the overlapping
        points of the widgets. We retrieve the range of points that
        could possible contain colored pixels for both this widget
        and the other widget

        Keyword arguments:
        widget  -- the widget to compare to
        axis    -- the desired axis of comparison, eg. height or width
        mini    -- the minimum point of the axis, eg. y or x
        maxa    -- the maximum point of the axis, eg. top or right 
        '''
        # retrieve the values of _coreimage because we can only
        # retrieve pixel color from the original image
        try:
            self_axis = getattr(self, axis)
            self_core_axis = getattr(self._coreimage, axis)
            widget_core_axis = getattr(widget._coreimage, axis)

            self_min = getattr(self, mini)
            self_max = getattr(self, maxa)
            widget_min = getattr(widget, mini)
            widget_max = getattr(widget, maxa)
        except AttributeError:
            Debug.debugPrint(self, "_calculate_range", "Attribute Error")
            return None

        
        # the range must be from the other widget's innermost overlapping
        # pixel to the outermost overlapping pixel
        #       () <- this widget     [] <- the other widget
        
        # this widget is on the higher bound :: eg. [  (**]  )
        if self_min > widget_min:
            start = 0
            end = widget_max - self_min
            step = 1
        # this widget is on the lower bound  :: eg. (  [**)  ]
        elif self_min < widget_min:
            start = self_max - widget_min
            end = -1
            step = -1
        # return on the most optimal situation:
        # when the widgets' axes are directly on top of each other
        else:
            return [math.ceil(widget_core_axis/2)], 0

        # otherwise, we account for the stretch of the image when creating
        # a range of pixels to iterate over
        # removing the padding for height only works when subtracting
        if axis == "height":
            # TODO  Remove this hack
            axis_stretch = math.floor((self_axis - self_core_axis)/1.4)
            if step == -1:
                start -= axis_stretch
            if step == 1:
                end -= axis_stretch
        # otherwise, divide out the padding
        if axis == "width":
            axis_stretch = self._stretch + widget._stretch
            if step == -1:
                start /= axis_stretch
            if step == 1:
                end /= axis_stretch

        return range(math.ceil(start), math.floor(end), step), step


    def _calculate_axis_pixels(self, widget, axis, step, i):
        '''
        [  ( * ]  )
        While looking at overlapping widgets, we calculate which pixels we
        check for transparency. When widgets are overlapping, the desired 
        pixel of this widget and the other widget will be located on 
        opposite sides of its respective widget
        
        eg. if our widget is colliding with the other widget from the
            right, a pixel to the left of this widget will be on the 
            other widget's right 
        
        Keyword arguments:
        widget  -- the widget to compare to
        axis    -- the desired axis of comparison, eg. height or width
        step    -- whether we are incrementing or decrementing on the axis
        i       -- the starting point of the axis
        '''
        try:
            self_axis = getattr(self._coreimage, axis)
            widget_axis = getattr(widget._coreimage, axis)
        except AttributeError:
            Debug.debugPrint(self, "_calculate_axis_pixels", 
                             "Attribute Error")
            return None

        self_axis_pixel, widget_axis_pixel = i, i

        # if we are incrementing pixels to check for transparency, likely 
        # the other widget is on the higher bound
        if step == 1:
            widget_axis_pixel = widget_axis - widget_axis_pixel
        # if we are decrementing pixels to check for transparency, likely 
        # this widget is on the higher bound
        elif step == -1:
            self_axis_pixel = self_axis - self_axis_pixel

        # we return no pixel if it isn't within the bounds of either image's 
        # coordinates
        if (widget_axis_pixel >= widget_axis
                or widget_axis_pixel < 0 
                or self_axis_pixel >= self_axis 
                or self_axis_pixel < 0):
            return None
        
        return self_axis_pixel, widget_axis_pixel


    def build(self):
        self._init_transparency()
        self.width = self._coreimage.width * self.STRETCH
        self.height = self._coreimage.height * self.STRETCH


    def get_overlapping_pixels(self, widget):
        ''' retrieves the pixels at which the current widget and a second
        widget are overlapping

        returns None if they are not overlapping
        
        Keyword arguments:
        widget  -- the widget to compare to
        '''
        # prevent calculation if the widgets are not in the approximate
        # area of one another
        if (self._in_widget_horizontal(widget) 
                and self._in_widget_vertical(widget)):
            h_range, h_step = self._calculate_range(
                widget, 'width', 'x', 'right')
            v_range, v_step = self._calculate_range(
                widget, 'height', 'y', 'top')
             
            for h in h_range:
                # we check if the retrieved pixels in the horizontal axis
                # are within the overlapping points of both widgets
                h_pixel = self._calculate_axis_pixels(
                    widget, 'width', h_step, h)
                
                # if not, we skip these pixels
                if h_pixel is None:
                    continue

                for v in v_range:
                    # we check if the retrieved pixels in the vertical 
                    # axis are within the overlapping points of both 
                    # widgets
                    v_pixel = self._calculate_axis_pixels(
                        widget, 'height', v_step, v)

                    # if not, we skip these pixels
                    if v_pixel is None:
                        continue

                    # we check if the opposite sides of the images
                    # have colored pixels
                    if (self._coreimage.read_pixel(
                                h_pixel[0], v_pixel[0])[-1] != 0 
                            and widget._coreimage.read_pixel(
                                h_pixel[1], v_pixel[1])[-1] != 0):
                        return (h_pixel, v_pixel)
        
        return None

    
    def is_overlapping_hitbox(self, widget):
        ''' checks if it's overlapping another widget's "hitbox"
        
        Keyword arguments:
        widget  -- the widget to compare to
        '''
        if (self._in_widget_horizontal(widget) 
                and self._in_widget_vertical(widget)):
            return True

    
    def is_overlapping(self, widget):
        ''' checks if it's overlapping another widget 
        
        Keyword arguments:
        widget  -- the widget to compare to
        '''
        if self.get_overlapping_pixels(widget) is not None:
            return True
        return False

        

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