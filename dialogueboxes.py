import kivy
kivy.require('1.10.1')

from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.graphics import RoundedRectangle, Color, Canvas

from kivy.properties import StringProperty

class ItemObtainedAlert(Widget):
    text = StringProperty('')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.w = 700
        self.h = 200
        self.pos = 50, 350
        self.text = "Default"

        with self.canvas.before:
            Color(1, 1, 1, 0.3)
            RoundedRectangle(size=(self.w, self.h), pos=self.pos)
        self.round_rect_label = Label(text="default", pos=self.pos,
            size=(self.w, self.h))
        self.add_widget(self.round_rect_label)
        self.bind(text=self.on_update_text)

    def update_text(self, new_text):
        self.text = new_text + "\n\nPress Enter to continue"


    def on_update_text(self, dt, value):
        self.round_rect_label.text = self.text