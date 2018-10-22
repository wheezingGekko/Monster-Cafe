import kivy
kivy.require('1.10.1')

from kivy.config import Config
Config.set('graphics', 'resizable', '0')

from kivy.app import App
from kivy.core.window import Window

from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.uix.gridlayout import GridLayout

from kivy.properties import NumericProperty, ObjectProperty, StringProperty
from kivy.vector import Vector
from kivy.clock import Clock

import math
import random
import enum

from characterlib import PlayerCharacter, NonPlayerCharacter

class Floor(GridLayout):
    
    TILE_SIZE = 32

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


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


class MonsterCafe(Widget):
    monsterImage = ObjectProperty(None)
    otherMonsterImage = ObjectProperty(None)
    storeFloor = ObjectProperty(None)

    OTHER_MONSTER_MOVEMENT = [[50, 0], [-50, 0]]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self._keyboard = Window.request_keyboard(
            self._keyboard_closed, self, 'text')
        if self._keyboard.widget:
            pass
        self._keyboard.bind(on_key_down=self._on_keyboard_down)
        self._keyboard.bind(on_key_up=self._on_keyboard_up)

        #self.monsterImage = PlayerCharacter("big_zombie")


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
        self.otherMonsterImage.build()
        self.ootherMonsterImage.build()
        self.storeFloor.build()
        self.otherMonsterImage.setPatrol(self.OTHER_MONSTER_MOVEMENT)

        self.monsterImage.build()


    def updateImage(self, dt):
        self.monsterImage.updateImage()
        self.otherMonsterImage.updateImage()
        self.ootherMonsterImage.updateImage()
    

    def updateMovement(self, dt):
        if not self.monsterImage.is_overlapping(self.otherMonsterImage):
            self.otherMonsterImage.updateMovement()


class MonsterCafeApp(App):
    IMAGE_UPDATE_SPEED = 10.0/60.0
    MOVEMENT_UPDATE_SPEED = 5.0/60.0

    def build(self):
        cafe = MonsterCafe()
        cafe.build()
        Clock.schedule_interval(cafe.updateImage, self.IMAGE_UPDATE_SPEED)
        Clock.schedule_interval(cafe.updateMovement, self.MOVEMENT_UPDATE_SPEED)
        return cafe

if __name__ == '__main__':
    MonsterCafeApp().run()