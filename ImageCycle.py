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
    
    '''
    checks if the image is within another image horizontally
    '''
    def _in_widget_horizontal(self, widget):
        return (widget.x <= self.x < widget.right or widget.x <= self.right < widget.right)

    '''
    checks if the image is within the other image horizontally
    '''
    def _in_widget_vertical(self, widget):
        return (widget.y <= self.y < widget.top or widget.y <= self.top < widget.top)

    '''
    calculates a range based on the desired axis (x or y)
    '''
    def _calculate_range(self, widget, axis, mini, maxa):
        self_hv = getattr(self, axis)
        self_core_hv = getattr(self._coreimage, axis)
        widget_hv = getattr(widget, axis)
        widget_core_hv = getattr(self._coreimage, axis)

        self_min = getattr(self, mini)
        self_max = getattr(self, maxa)
        widget_min = getattr(widget, mini)
        widget_max = getattr(widget, maxa)

        axis_padding = (self_hv - self_core_hv)/2
        axis_range = [math.ceil(widget_core_hv/2)]
        start = -1
        step = 0

        if self_min < widget_min:
            start = self_max - widget_min
            end = -1
            step = -1
        elif self_min > widget_min:
            start = 0
            end = widget_max - self_min
            step = 1

        # if the image isn't exactly on top of the other vertically
        # or horizontally, then we remove the padding
        if start > -1:
            if start > 0:
                start -= axis_padding
            if end > -1:
                end -= axis_padding
            axis_range = range(math.ceil(start), math.ceil(end), step)

        return axis_range, step

    '''
    note: what if overlapping over multiple things?
    '''
    def is_overlapping(self, widget):

        if (self._in_widget_horizontal(widget) and self._in_widget_vertical(widget)):

            # reading the _coreimage is essentially the image itself on the file, which doesn't
            # regard the stretches we did on top of the image
            # that is why we have to consider the padding when we search for the actual "pixel" of the image
            
            if (self.x == widget.x and self.y == widget.y):
                return True

            h_range, h_step = self._calculate_range(widget, 'width', 'x', 'right')
            v_range, v_step = self._calculate_range(widget, 'height', 'y', 'top')
             
            for h in h_range:
                self_h_pixel, widget_h_pixel = h, h

                 # coming from the right, the widget's desired pixel is on the right
                if h_step == 1:
                    widget_h_pixel = widget._coreimage.width - h
                # coming from the left, the instance's desired pixel is on the right
                elif h_step == -1:
                    self_h_pixel = self._coreimage.width - h

                if (widget_h_pixel >= widget._coreimage.width 
                        or widget_h_pixel < 0 
                        or self_h_pixel >= self._coreimage.width 
                        or self_h_pixel < 0):
                    continue

                for v in v_range:
                    self_v_pixel, widget_v_pixel = v, v

                    # coming from above
                    if v_step == 1:
                        widget_v_pixel = widget._coreimage.height - v
                    # coming from below
                    elif v_step == -1:
                        self_v_pixel = self._coreimage.height - v
                    
                    if (widget_v_pixel >= widget._coreimage.height 
                            or widget_v_pixel < 0 
                            or self_v_pixel >= self._coreimage.height 
                            or self_v_pixel < 0):
                        continue

                    if (self._coreimage.read_pixel(self_h_pixel, self_v_pixel)[-1] != 0 
                            and widget._coreimage.read_pixel(widget_h_pixel, widget_v_pixel)[-1] != 0):
                        return True
        return False

class AnimatedImage(OverlappingImage):
    '''
    Class handling images that are manually animated, either with looping
    images or with x- y- axis movement.
    '''

    MOVEMENT_SPEED = 5
    CYCLE_LENGTH = 4

    image_name = StringProperty('')
    image_state = StringProperty('')
    image_num = NumericProperty(0)

    # image stretched because of how tiny the sprites are
    def __init__(self, **kwargs):
        super(AnimatedImage, self).__init__(**kwargs)
        self.image_state = "idle"
        self.width = 150
        self.size_hint_y = None
        self.allow_stretch = True
        self.keep_ratio = True
        self.keep_data = True

    def idle(self):
        self.image_state = "idle"

    def move(self,  offset): 
        self.image_state = "run"
        self.pos = (self.MOVEMENT_SPEED * Vector(offset)) + self.pos 

    def updateImage(self):
        self.image_num = (self.image_num + 1) % self.CYCLE_LENGTH

class WalkingCharacter(AnimatedImage):

    def __init__(self, **kwargs):
        super(WalkingCharacter, self).__init__(**kwargs)

    def setPatrol(self, movementList):
        self.MOVEMENT_LIST = movementList
        self._current_goal = 1
        self._current_movement = [0, 0]

    def updateMovement(self):
        if (self._current_movement[0] == 0 and self._current_movement[1] == 0):
            self._current_movement[0] = self.MOVEMENT_LIST[self._current_goal][0]
            self._current_movement[1] = self.MOVEMENT_LIST[self._current_goal][1]
            self._current_goal = (self._current_goal + 1) % len(self.MOVEMENT_LIST)
             
        self._moveTowardGoal()

    def _moveTowardGoal(self):
        move_vector = Vector(0, 0)

        x_move, y_move = 0, 0

        # if the expected movement is leftward (-x), move to the left
        if self._current_movement[0] < 0:
            x_move = -1
        # if the expected movement is rightward (+x), move to the right
        elif self._current_movement[0] > 0:
            x_move = 1

        # if the expected movement is downward (-y), move down
        if self._current_movement[1] < 0:
            y_move = -1
        # if the expected movement is upward (+y), move up
        elif self._current_movement[1] > 0:
            y_move = 1

        # we subtract from the amount of movement we have left
        self._current_movement[0] -= x_move
        self._current_movement[1] -= y_move

        # then we make the expected movement
        move_vector += Vector(x_move, y_move)

        self.move(move_vector)


# trying to overlay counters on to floor
class Counter(FloatLayout):
    
    def __init__(self, **kwargs):
        super(Counter,self).__init__(**kwargs)
        
    def build(self):
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
        if keycode[1] == "down" and (self.monsterImage.y - self.monsterImage.MOVEMENT_SPEED) >= 0:
            self.monsterImage.move((0,-1))
        elif keycode[1] == "up" and (self.monsterImage.top + self.monsterImage.MOVEMENT_SPEED) <= self.height:
            self.monsterImage.move((0, 1))
        elif keycode[1] == "left" and (self.monsterImage.x - self.monsterImage.MOVEMENT_SPEED) >= 0:
            self.monsterImage.move((-1, 0))
        elif keycode[1] == "right" and (self.monsterImage.right + self.monsterImage.MOVEMENT_SPEED) <= self.width:
            self.monsterImage.move((1, 0))
        return True

    def _on_keyboard_up(self, keyboard, keycode):
        if (keycode[1] == "down" or keycode[1] == "up" or
            keycode[1] == "left" or keycode[1] == "right"):
                self.monsterImage.idle()       

    #def _on_update_texture(self, instance, value):
        #self.monsterImage.texture = value

    def build(self):
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