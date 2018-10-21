import kivy
kivy.require('1.10.1')

from kivy.config import Config
Config.set('graphics', 'resizable', '0')

from kivy.app import App
from kivy.core.window import Window

from kivy.uix.widget import Widget
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image

from kivy.properties import NumericProperty, ObjectProperty, StringProperty
from kivy.vector import Vector
from kivy.clock import Clock

import math
import random
import enum


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


class LoopingImage(OverlappingImage):
    ''' Class of animations composed by looping images '''

    CYCLE_LENGTH = 4

    image_name = StringProperty('')
    image_num = NumericProperty(0)


    def updateImage(self):
        ''' moves image to next image state via number suffixes of the file '''
        self.image_num = (self.image_num + 1) % self.CYCLE_LENGTH


class Character(LoopingImage):

    DESIRED_WIDTH = 150
    MOVEMENT_SPEED = 5

    image_state = StringProperty('')


    def __init__(self, **kwargs):
        super(Character, self).__init__(**kwargs)


    def _get_transparency(self):
        left_transparency = self._find_left_transparency_size()
        right_transparency = self._find_right_transparency_size()

        stretch = self.DESIRED_WIDTH/self._coreimage.width

        left_transparency *= stretch
        right_transparency *= stretch

        return left_transparency, right_transparency


    def _find_left_transparency_size(self):
        true_left = self._coreimage.width
        for y in range(self._coreimage.height):
            for x in range(self._coreimage.width):
                if (self._coreimage.read_pixel(x, y)[-1] != 0
                        and x < true_left):
                    true_left = x
                    continue
        return true_left


    def _find_right_transparency_size(self):
        true_right = -1
        for y in range(self._coreimage.height):
            for x in range(self._coreimage.width - 1, -1, -1):
                if (self._coreimage.read_pixel(x, y)[-1] != 0
                        and x > true_right):
                    true_right = x
                    continue
        return self._coreimage.width - true_right


    def build(self):
        l_transparency, r_transparency = self._get_transparency()
        self.stretched_left = l_transparency
        self.stretched_right = r_transparency


    def idle(self):
        self.image_state = "idle"


    def move(self,  offset): 
        self.image_state = "run"
        self.pos = (self.MOVEMENT_SPEED * Vector(offset)) + self.pos 


class NonPlayerCharacter(Character):


    def setPatrol(self, movementList):
        self.MOVEMENT_LIST = movementList
        self._move_index = 1
        self._x, self._y = 0, 0


    def updateMovement(self):
        if (self._x == 0 and self._y == 0):
            self._x = self.MOVEMENT_LIST[self._move_index][0]
            self._y = self.MOVEMENT_LIST[self._move_index][1]
            self._move_index = (self._move_index + 1) % len(self.MOVEMENT_LIST)
             
        self._moveTowardGoal()


    def _moveTowardGoal(self):
        x_move, y_move = 0, 0

        # if the remaining movement is positive, then the movement toward
        # the respective axis is positive (right, up)
        # if the remaining movement is negative, then the movement toward
        # the respective axis is negative (left, down)
        if self._x != 0:
            x_move = self._x / abs(self._x)
        if self._y != 0:
            y_move = self._y / abs(self._y)

        # we subtract from the amount of movement we have left
        self._x -= x_move
        self._y -= y_move

        # then we move using the calculated movement
        self.move(Vector(x_move, y_move))


class PlayerCharacter(Character):
    pass


class Floor(GridLayout):
    
    TILE_SIZE = 32

    def __init__(self, **kwargs):
        super(Floor, self).__init__(**kwargs)


    # TODO: Note that if the window stretches, it messes things up. Maybe force a certain size?
    # builds a floor with randomized tiles
    def build(self):
        s = Window.size
        self.cols = math.ceil(s[0]/self.TILE_SIZE)
        self.rows = math.ceil(s[1]/self.TILE_SIZE)

        for i in range(self.cols * self.rows):
            i = Image(source="Images\\bg\\floor_" + str(random.randint(1,8)) + ".png")
            i.allow_stretch = True
            self.add_widget(i)


class ImageCycleExample(Widget):
    monsterImage = ObjectProperty(None)
    otherMonsterImage = ObjectProperty(None)
    storeFloor = ObjectProperty(None)

    OTHER_MONSTER_MOVEMENT = [[50, 0], [-50, 0]]

    def __init__(self, **kwargs):
        super(ImageCycleExample, self).__init__(**kwargs)

        self._keyboard = Window.request_keyboard(
            self._keyboard_closed, self, 'text')
        if self._keyboard.widget:
            pass
        self._keyboard.bind(on_key_down=self._on_keyboard_down)
        self._keyboard.bind(on_key_up=self._on_keyboard_up)


    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None


    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        # TODO// Create a function that checks if the movement is allowed using vectors
        up = self.monsterImage.y - self.monsterImage.MOVEMENT_SPEED
        down = self.monsterImage.top + self.monsterImage.MOVEMENT_SPEED
        left = (self.monsterImage.x
                + self.monsterImage.stretched_left 
                - self.monsterImage.MOVEMENT_SPEED)
        right = (self.monsterImage.right
                 - self.monsterImage.stretched_right 
                 + self.monsterImage.MOVEMENT_SPEED)

        if keycode[1] == "down" and up >= 0:
            self.monsterImage.move((0,-1))
        elif keycode[1] == "up" and down <= self.height:
            self.monsterImage.move((0, 1))
        elif keycode[1] == "left" and left >= 0:
            self.monsterImage.move((-1, 0))
        elif keycode[1] == "right" and right <= self.width:
            self.monsterImage.move((1, 0))
        return True


    def _on_keyboard_up(self, keyboard, keycode):
        if (keycode[1] == "down" or keycode[1] == "up" or
            keycode[1] == "left" or keycode[1] == "right"):
                self.monsterImage.idle()       


    def build(self):
        self.monsterImage.build()
        self.otherMonsterImage.build()
        self.storeFloor.build()
        self.otherMonsterImage.setPatrol(self.OTHER_MONSTER_MOVEMENT)


    def updateImage(self, dt):
        self.monsterImage.updateImage()
        self.otherMonsterImage.updateImage()
    

    def updateMovement(self, dt):
        if not self.monsterImage.is_overlapping(self.otherMonsterImage):
            self.otherMonsterImage.updateMovement()


class ImageCycleApp(App):

    IMAGE_UPDATE_SPEED = 10.0/60.0
    MOVEMENT_UPDATE_SPEED = 5.0/60.0

    def build(self):
        example = ImageCycleExample()
        example.build()
        Clock.schedule_interval(example.updateImage, self.IMAGE_UPDATE_SPEED)
        Clock.schedule_interval(example.updateMovement, self.MOVEMENT_UPDATE_SPEED)
        return example

if __name__ == '__main__':
    ImageCycleApp().run()