import kivy
kivy.require('1.10.1')

from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.graphics import RoundedRectangle, Color, Canvas

from kivy.properties import StringProperty


class DialogueBox(Widget):
    ''' base class of all dialogue boxes which appear on the screen '''
    text = StringProperty('')

    ALERT_FORMAT = ""

    def __init__(self, **kwargs):
        ''' draws a transparent rounded rectangle at the top third of the
        screen, as well as text atop it. it tracks whether or not the text
        has been updated
        '''
        super().__init__(**kwargs)
        
        self.w = 700
        self.h = 200
        self.pos = 50, 350
        self.text = "Default"

        with self.canvas.before:
            Color(1, 1, 1, 0.3)
            RoundedRectangle(size=(self.w, self.h), pos=self.pos)
        self.round_rect_label = Label(text=self.text, pos=self.pos,
            size=(self.w, self.h))
        self.add_widget(self.round_rect_label)
        self.bind(text=self.on_update_text)


    def update_text(self, new_text):
        ''' changes current text in the box '''
        self.text = new_text


    def format_text(self, text):
        return text + "\n\nPress [ENTER] to close the window"


    def on_update_text(self, dt, value):
        ''' callback when the text property has been updated '''
        self.round_rect_label.text = self.format_text(self.text)


class ItemObtainedAlert(DialogueBox):
    ''' class handling dialogue boxes of items acquired '''
    def format_text(self, text):
        temp_text = "Obtained " + text + "!"
        return super().format_text(temp_text)


class CharacterSpeechBox(DialogueBox):
    ''' class handling dialogue boxes of when characters speak '''
    def update_text(self, speaker, speech):
        self.text = speaker + ": " + speech