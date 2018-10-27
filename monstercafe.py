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

from characterlib import PlayerCharacter, NonPlayerCharacter
from item import Item

# TODO  Changing Window size messes up gridlayout for floor
# TODO  Adjust how sprinting works


class Floor(GridLayout):
    
    TILE_SIZE = 32

    def build(self):
        ''' creates floor based on the window size using randomized 
        tiles 
        '''
        s = Window.size
        self.cols = math.ceil(s[0]/self.TILE_SIZE)
        self.rows = math.ceil(s[1]/self.TILE_SIZE)

        for i in range(self.cols * self.rows):
            i = Image(source="Images\\bg\\floor_" 
                        + str(random.randint(1,8)) + ".png")
            i.allow_stretch = True
            self.add_widget(i)


class MonsterCafe(Widget):
    player = ObjectProperty(None)
    # otherMonsterImage = ObjectProperty(None)
    storeFloor = ObjectProperty(None)

    OTHER_MONSTER_MOVEMENT = [[50, 0], [-50, 0]]
    OOTHER_MONSTER_MOVEMENT = [[0, -50], [0, 50]]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

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
        up = (self.player.top - self.player.top_pad 
              + self.player.MOVEMENT_SPEED)
        down = self.player.y - self.player.MOVEMENT_SPEED 
        left = (self.player.x + self.player.left_pad 
                - self.player.MOVEMENT_SPEED)
        right = (self.player.right - self.player.right_pad
                 + self.player.MOVEMENT_SPEED)

        move = (0, 0)

        if keycode[1] == "down" and down >= 0:
            move = (0, -1)
        elif keycode[1] == "up" and up <= self.height:
            move = (0, 1)
        elif keycode[1] == "left" and left >= 0:
            move = (-1, 0)
        elif keycode[1] == "right" and right <= self.width:
            move = (1, 0)

        if move != (0, 0):
            if "shift" in modifiers:
                move = self.player.sprint(move)
            
            self.player.move(move)
            self._on_collision(move)

        return True


    def _on_keyboard_up(self, keyboard, keycode):
        if (keycode[1] == "down" or keycode[1] == "up" or
            keycode[1] == "left" or keycode[1] == "right"):
                self.player.idle()       


    def _on_collision(self, move):
        for w in self.children:
            if isinstance(w, Item):
                if self.player.is_overlapping(w):
                    self.player.add_item(w.item_name)
                    self.remove_widget(w)
            if isinstance(w, NonPlayerCharacter):
                pass


    def build(self):

        # randomly adds apples everywhere
        s = Window.size
        for i in range(10):
            i = Item(item_name="Apple")
            self.add_widget(i)
            last_child = self.children[0]
            last_child.x = random.randint(0, s[0] - last_child.right)
            last_child.y = random.randint(0, s[1] - last_child.top)

        for w in self.children:
            try:
                w.build()
            except AttributeError:
                continue
        
        # self.otherMonsterImage.set_patrol(self.OTHER_MONSTER_MOVEMENT)
        # self.ootherMonsterImage.set_patrol(self.OOTHER_MONSTER_MOVEMENT)


    def update_image(self, dt):
        for w in self.children:
            try:
                w.update_image()
            except AttributeError:
                continue
    

    def update_movement(self, dt):
        pass
        #for w in self.children:
            #if isinstance(w, NonPlayerCharacter):
        # if not self.player.is_overlapping(self.ootherMonsterImage):
        #     self.ootherMonsterImage.updateMovement()


class MonsterCafeApp(App):
    IMAGE_UPDATE_SPEED = 10.0/60.0
    MOVEMENT_UPDATE_SPEED = 5.0/60.0

    def build(self):
        cafe = MonsterCafe()
        cafe.build()
        Clock.schedule_interval(cafe.update_image, 
                                self.IMAGE_UPDATE_SPEED)
        Clock.schedule_interval(cafe.update_movement, 
                                self.MOVEMENT_UPDATE_SPEED)
        return cafe


if __name__ == '__main__':
    MonsterCafeApp().run()