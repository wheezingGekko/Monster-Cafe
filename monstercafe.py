import kivy
kivy.require('1.10.1')

from kivy.config import Config
Config.set('graphics', 'resizable', '0')

from kivy.app import App
from kivy.core.window import Window

from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.uix.gridlayout import GridLayout

from kivy.properties import (NumericProperty, ObjectProperty, 
                             StringProperty)
from kivy.vector import Vector
from kivy.clock import Clock
from kivy.event import *

import math
import random
from functools import partial

from characterlib import PlayerCharacter, NonPlayerCharacterImage
from dialogueboxes import (DialogueBox, ItemObtainedAlert, 
                           CharacterSpeechBox)
from item import Item

# TODO  Changing Window size messes up gridlayout for floor
#
# TODO  Consider whether to make the Floor class into one function
#
# TODO  Consider to create a tileset rather than dynamically generating it
#
# TODO  Adjust how sprinting works


class Floor(GridLayout):
    ''' class handling dynamically generated floor-tiles '''
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
    storeFloor = ObjectProperty(None)

    MOVEMENT_KEYS = ['left', 'right', 'up', 'down']
    DISMISS_KEY = 'enter'
    INTERACT_KEY = 'e'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self._keyboard = Window.request_keyboard(
            self._keyboard_closed, self, 'text')
        if self._keyboard.widget:
            pass
        self._keyboard.bind(on_key_down=self._on_keyboard_down)
        self._keyboard.bind(on_key_up=self._on_keyboard_up)

        self.player = PlayerCharacter()
        self.item_alert = ItemObtainedAlert()
        self.speech_box = CharacterSpeechBox()
        self.interact_function = ""

        self.register_event_type("on_item_obtained")


    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None


    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        if isinstance(self.children[0], DialogueBox):
            if keycode[1] == self.DISMISS_KEY:
                self.remove_widget(self.children[0])
        else:
            if keycode[1] in self.MOVEMENT_KEYS:
                self._handle_move_key(keycode[1], modifiers)
            if (keycode[1] == self.INTERACT_KEY
                    and self.interact_function != ""):
                self.interact_function()
        return True


    def _on_keyboard_up(self, keyboard, keycode):
        # if the player lets go of a movement, the animation goes to the
        # idle animation
        if (keycode[1] in self.MOVEMENT_KEYS 
                and not isinstance(self.children[0], ItemObtainedAlert)):
            self.player.image.idle()       


    def _handle_move_key(self, key, modifiers=None):
        up = (self.player.image.top - self.player.image.top_pad 
              + self.player.image.MOVEMENT_SPEED)
        down = self.player.image.y - self.player.image.MOVEMENT_SPEED 
        left = (self.player.image.x + self.player.image.left_pad 
                - self.player.image.MOVEMENT_SPEED)
        right = (self.player.image.right - self.player.image.right_pad
                 + self.player.image.MOVEMENT_SPEED)

        if key == "down" and down >= 0:
            move = (0, -1)
        elif key == "up" and up <= self.height:
            move = (0, 1)
        elif key == "left" and left >= 0:
            move = (-1, 0)
        elif key == "right" and right <= self.width:
            move = (1, 0)
        else:
            move = (0, 0)

        if modifiers is not None:
            if "shift" in modifiers:
                move = self.player.image.sprint(move)
        
        self.player.image.move(move)
        self._on_collision(move)


    def _on_collision(self, move):
        ''' checks if there is collision between the player widget and
        any other widget
        '''
        for w in self.children:
            if isinstance(w, Item):
                if self.player.image.is_overlapping(w):
                    self.dispatch('on_item_obtained', w)
            if isinstance(w, NonPlayerCharacterImage):
                if w.is_overlapping(self.player.image):
                    self.update_text_box(w)
                    self.interact_function = self.show_text_box
                    break
            else:
                self.interact_function = ""


    def on_item_obtained(self, w):
        pass


    def on_item_obtained_cb(self, dt, w):
        ''' callback when an item has been obtained by the player '''
        self.player.add_item(w)
        self.remove_widget(w)
        self.add_widget(self.item_alert)
        self.item_alert.update_text(w.name)

    
    def update_text_box(self, w):
        ''' updates text of the dialogue box '''
        self.speech_box.update_text(w.name, "Hey there!")


    def show_text_box(self):
        ''' displays dialogue of character on screen '''
        self.add_widget(self.speech_box)


    def _bind(self):
        ''' bind self and children to respective dispatchers '''
        self.bind(on_item_obtained=self.on_item_obtained_cb)
        

    def build(self):
        # randomly adds NPC everywhere
        for i in range(10):
            n = NonPlayerCharacterImage(
                name="big_demon" + str(i), image_name="big_demon")
            #n = Item("apple", item_name="Apple")
            self.add_widget(n)
            self._randomly_place(self.children[0])

        self.add_widget(self.player.image)

        for w in self.children:
            try:
                w.build()
            except AttributeError:
                continue

        self._bind()


    def _randomly_place(self, w):
        s = Window.size
        w.x = random.randint(0, s[0] - w.right)
        w.y = random.randint(0, s[1] - w.top)


    def update_image(self, dt):
        for w in self.children:
            try:
                w.update_image()
            except AttributeError:
                continue
    

    def update_movement(self, dt):
        for w in self.children:
            if isinstance(w, NonPlayerCharacterImage):
                if not self.player.image.is_overlapping(w):
                    w.update_movement()


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