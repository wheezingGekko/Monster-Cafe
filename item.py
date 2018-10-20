import kivy
kivy.require('1.10.1')

from kivy.app import App
from kivy.core.window import Window

from kivy.uix.widget import Widget
from kivy.uix.image import Image

from kivy.properties import ObjectProperty, StringProperty
from kivy.clock import Clock

class AnimatedItem(Image):
    CYCLE_SPEED = 5
    CYCLE_LENGTH = 10
    UP = 1
    DOWN = -1

    item_name = StringProperty('')

    # image stretched because of how tiny the sprites are
    def __init__(self, **kwargs):
        super(AnimatedItem, self).__init__(**kwargs)
        self.image_num = 0
        self.movement_direction = self.UP

    def update(self):
        self.image_num = (self.image_num + 1) % self.CYCLE_LENGTH

        if self.image_num == 0:
            self.movement_direction = -self.movement_direction

        self.y += self.movement_direction

class AnimatedItemBG(Widget):
    aApple = ObjectProperty(None)

    def update(self, dt):
        self.aApple.update()

class BouncingImageApp(App):
    def build(self):
        itemExample = AnimatedItemBG()
        Clock.schedule_interval(itemExample.update, 2.0/60.0)
        return itemExample

if __name__ == '__main__':
    BouncingImageApp().run()

