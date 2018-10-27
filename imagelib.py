import kivy
kivy.require('1.10.1')

from kivy.uix.image import Image
from kivy.properties import NumericProperty, StringProperty

import math

from debugger import Debug

# TODO  When searching for the colored pixel, use binary search algo for 
#       optimization
#
# TODO  Possibly make an all-around function encapsulating the search for
#       the non-transparent pixel beginning


class OverlappingImage(Image):
    ''' Class handling images that can sense if another image is 
    overlapping it 
    '''

    STRETCH = 1
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


    def _init_transparency(self):
        self.left_pad = self._find_left_pixel() * self.STRETCH
        self.right_pad = self._find_right_pixel() * self.STRETCH
        self.top_pad = self._find_top_pixel() * self.STRETCH


    def _find_left_pixel(self):
        true_left = self._coreimage.width

        for y in range(self._coreimage.height):
            for x in range(self._coreimage.width):
                if (self._coreimage.read_pixel(x, y)[-1] > 0.5
                        and x < true_left):
                    true_left = x
                    continue
        return true_left


    def _find_right_pixel(self):
        true_right = -1

        for y in range(self._coreimage.height):
            for x in range(self._coreimage.width - 1, -1, -1):
                if (self._coreimage.read_pixel(x, y)[-1] > 0.5
                        and x > true_right):
                    true_right = x
                    continue
        return self._coreimage.width - true_right

 
    def _find_top_pixel(self):
        true_top = -1

        for x in range(self._coreimage.width):
            for y in range(self._coreimage.height - 1, -1, -1):
                if (self._coreimage.read_pixel(x, y)[-1] > 0.5
                        and y > true_top):
                    true_top = y
                    continue
                elif (self._coreimage.read_pixel(x, y)[-1] > 0.5
                        and y <= true_top):
                    break
        return self._coreimage.height - true_top


    def _in_widget_horizontal(self, widget):
        ''' returns true or false if within a widget's x-axis '''
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
        ''' returns true or false if within a widget's y-axis '''
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
            widget_core_axis = getattr(self._coreimage, axis)

            self_min = getattr(self, mini)
            self_max = getattr(self, maxa)
            widget_min = getattr(widget, mini)
            widget_max = getattr(widget, maxa)
        except AttributeError:
            Debug.debugPrint(self, "_calculate_range", "Attribute Error")
            return None

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
            # that the image is stretched
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
        
        return (self_axis_pixel, widget_axis_pixel)


    def build(self):
        self._init_transparency()


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


    def update_image(self):
        ''' moves image to next image state via number suffixes of the file '''
        self.image_num = (self.image_num + 1) % self.CYCLE_LENGTH


class FloatingImage(Image):

    CYCLE_SPEED = 5
    CYCLE_LENGTH = 10
    UP = 1
    DOWN = -1

    item_name = StringProperty('')

    # image stretched because of how tiny the sprites are
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.image_num = 0
        self.movement_direction = self.UP


    def update_image(self):
        self.image_num = (self.image_num + 1) % self.CYCLE_LENGTH

        if self.image_num == 0:
            self.movement_direction = -self.movement_direction

        self.y += self.movement_direction