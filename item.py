import kivy
kivy.require('1.10.1')

from kivy.app import App
from kivy.core.window import Window

from kivy.uix.widget import Widget
from kivy.uix.image import Image

from kivy.properties import ObjectProperty, StringProperty
from kivy.clock import Clock

import random

from imagelib import OverlappingImage, FloatingImage

class Item(OverlappingImage, FloatingImage):
    CYCLE_SPEED = 5
    CYCLE_LENGTH = 10
    UP = 1
    DOWN = -1

    item_name = StringProperty('')


class ItemBag(object):

    def __init__(self):
        self.items = []


    def add_item(self, item_name):
        self.items.append(item_name)


    def delete_item(self, item_name):
        if self.has_item(item_name):
            return True
        return False

    
    def has_item(self, item_name):
        return (item_name in self.items)


    def print_items(self):
        for i in self.items:
            print (i)