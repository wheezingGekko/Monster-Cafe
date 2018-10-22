import kivy
kivy.require('1.10.1')

from kivy.uix.image import Image
from kivy.properties import NumericProperty, StringProperty

import math


class OverlappingImage(Image):
    ''' Class handling images that can sense if another image is 
    overlapping it 
    '''
    
    def _in_widget_horizontal(self, widget):
        ''' returns true or false if within a widget's x-axis' '''
        return (widget.x <= self.x < widget.right 
                or widget.x <= self.right < widget.right)


    def _in_widget_vertical(self, widget):
        ''' returns true or false if within a widget's y-axis '''
        return (widget.y <= self.y < widget.top 
                or widget.y <= self.top < widget.top)


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
        self_axis = getattr(self, axis)
        self_core_axis = getattr(self._coreimage, axis)
        widget_core_axis = getattr(self._coreimage, axis)

        self_min = getattr(self, mini)
        self_max = getattr(self, maxa)
        widget_min = getattr(widget, mini)
        widget_max = getattr(widget, maxa)

        # initial values are based on the most optimal situation:
        # when the widgets are directly on top of each other
        axis_range = [math.ceil(widget_core_axis/2)]
        step = 0

        # the range must be from the other widget's innermost overlapping
        # pixel to the outermost overlapping pixel
        # () <- this widget 
        # [] <- the other widget
        
        # this widget is on the lower bound
        # eg. (  [**)  ]
        if self_min < widget_min:
            start = self_max - widget_min
            end = -1
            step = -1
        # this widget is on the higher bound
        # eg. [  (**]  )
        elif self_min > widget_min:
            start = 0
            end = widget_max - self_min
            step = 1

        # if the image isn't exactly on top of the other vertically
        # or horizontally, then we ignore the stretching of the image
        if step != 0:
            # without dividing it by some constant, we don't recognize
            # that the image is streetched
            axis_stretch = math.floor((self_axis - self_core_axis)/1.4)
            if start > 0:
                start -= axis_stretch
            if end > -1:
                end -= axis_stretch
            axis_range = range(math.ceil(start), math.ceil(end), step)

        return axis_range, step


    def _calculate_axis_pixels(self, widget, axis, step, i):
        '''
        [  ( * ]  )
        While looking at overlapping widgets, we calculate which pixel we 
        check for transparency. When widgets are overlapping, the desired 
        pixel of this widget and the other widget will be located on 
        opposite sides of its respective widget
        
        eg. if our widget is colliding with the other widget from the
            right, a pixel to the left of this widget will be on the 
            other widget's right 
        '''
        self_axis = getattr(self._coreimage, axis)
        widget_axis = getattr(widget._coreimage, axis)

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
        
        return (self_axis_pixel, widget_axis_pixel)


    def is_overlapping(self, widget):
        ''' checks if it's overlapping another widget '''
        if (self._in_widget_horizontal(widget) and self._in_widget_vertical(widget)):
            
            if (self.x == widget.x and self.y == widget.y):
                return True

            h_range, h_step = self._calculate_range(widget, 'width', 'x', 
                                                    'right')
            v_range, v_step = self._calculate_range(widget, 'height', 'y', 
                                                    'top')
             
            for h in h_range:
                h_pixel = self._calculate_axis_pixels(widget, 'width', 
                                                      h_step, h)
                if h_pixel is None:
                    continue

                for v in v_range:
                    v_pixel = self._calculate_axis_pixels(widget, 'height', 
                                                          v_step, v)
                    if v_pixel is None:
                        continue

                    if (self._coreimage.read_pixel(
                                h_pixel[0], v_pixel[0])[-1] != 0 
                            and widget._coreimage.read_pixel(
                                h_pixel[1], v_pixel[1])[-1] != 0):
                        return True
        return False


class LoopingImage(Image):
    ''' Class of animations composed by looping images '''

    CYCLE_LENGTH = 4

    image_name = StringProperty('')
    image_num = NumericProperty(0)


    def __init__(self, **kwargs):
        super().__init__(**kwargs)


    def updateImage(self):
        ''' moves image to next image state via number suffixes of the file '''
        self.image_num = (self.image_num + 1) % self.CYCLE_LENGTH