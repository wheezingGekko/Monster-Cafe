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

class AnimatedImage(Image):
    MOVEMENT_SPEED = 5
    CYCLE_LENGTH = 4

    image_name = StringProperty('')
    image_state = StringProperty('')
    image_num = NumericProperty(0)

    orientation = 0

    # image stretched because of how tiny the sprites are
    def __init__(self, **kwargs):
        super(AnimatedImage, self).__init__(**kwargs)
        self.image_state = "idle"
        self.width = 150
        self.size_hint_y = None
        self.allow_stretch = True

    def _idle(self):
        self.image_state = "idle"

    '''
        TODO: This doesn't work, so it's not inside
    '''
    def flip(self):
        self.orientation = (self.orientation + 1) % 2
        self.texture.flip_horizontal()

    def move(self,  offset): 
        self.image_state = "run"
        self.pos = (self.MOVEMENT_SPEED * Vector(offset)) + self.pos 

    def update(self):
        self.image_num = (self.image_num + 1) % self.CYCLE_LENGTH


class WalkingCharacter(AnimatedImage):

    def __init__(self, **kwargs):
        super(WalkingCharacter, self).__init__(**kwargs)

    def setPatrol(self, movementList):
        self.MOVEMENT_LIST = movementList
        self.currentGoal = 1
        self.currentMovement = [0, 0]

    def updateCurrentMovement(self):
        self.currentMovement[0] = self.MOVEMENT_LIST[self.currentGoal][0]
        self.currentMovement[1] = self.MOVEMENT_LIST[self.currentGoal][1]

    def update(self):
        super(WalkingCharacter, self).update()
        if (self.currentMovement[0] == 0 and self.currentMovement[1] == 0):
            self.updateCurrentMovement()
            self.currentGoal = (self.currentGoal + 1) % len(self.MOVEMENT_LIST) 
            print (self.currentMovement)
        self.moveTowardGoal()

    def moveTowardGoal(self):
        moveVector = Vector(0, 0)

        xMove = 0
        yMove = 0

        # if the expected movement is leftward (-x), move to the left
        if self.currentMovement[0] < 0:
            xMove = -1
        # if the expected movement is rightward (+x), move to the right
        elif self.currentMovement[0] > 0:
            xMove = 1

        # if the expected movement is downward (-y), move down
        if self.currentMovement[1] < 0:
            yMove = -1
        # if the expected movement is upward (+y), move up
        elif self.currentMovement[1] > 0:
            yMove = 1

        # we subtract from the amount of movement we have left
        self.currentMovement[0] -= xMove
        self.currentMovement[1] -= yMove

        # then we make the expected movement
        moveVector += Vector(xMove, yMove)

        self.move(moveVector)

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
    storeCounter = ObjectProperty(None)

    OTHER_MONSTER_MOVEMENT = [[50, 0], [-50, 0]]

    def __init__(self, **kwargs):
        super(ImageCycleExample, self).__init__(**kwargs)

        self._keyboard = Window.request_keyboard(
            self._keyboard_closed, self, 'text')
        if self._keyboard.widget:
            pass
        self._keyboard.bind(on_key_down=self._on_keyboard_down)
        self._keyboard.bind(on_key_up=self._on_keyboard_up)
        #self.monsterImage.bind(texture=self._on_update_texture)

    def _keyboard_closed(self):
        print('Keyboard has closed')
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
                self.monsterImage._idle()       

    #def _on_update_texture(self, instance, value):
        #self.monsterImage.texture = value

    def build(self):
        self.storeFloor.build()
        self.otherMonsterImage.setPatrol(self.OTHER_MONSTER_MOVEMENT)
        self.storeCounter.build()

    def update(self, dt):
        self.monsterImage.update()
        self.otherMonsterImage.update()


class ImageCycleApp(App):

    def build(self):
        example = ImageCycleExample()
        example.build()
        Clock.schedule_interval(example.update, 10.0/60.0)
        return example

if __name__ == '__main__':
    ImageCycleApp().run()