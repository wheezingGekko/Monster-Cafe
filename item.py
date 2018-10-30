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
    ''' widgets "collectable" by player class '''
    STRETCH = 2

    item_name = StringProperty('')


class ItemBag(object):
    ''' container for Item class; use to be expanded later '''
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