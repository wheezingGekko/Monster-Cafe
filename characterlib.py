import kivy
kivy.require('1.10.1')

from kivy.vector import Vector
from kivy.properties import StringProperty

from imagelib import LoopingImage, OverlappingImage
from item import ItemBag

class Character(LoopingImage, OverlappingImage):
    STRETCH = 4
    MOVEMENT_SPEED = 5
    MOVE_INCREASE = 3

    image_state = StringProperty('')


    def __init__(self, **kwargs):
        super().__init__(**kwargs)


    def build(self):
        super().build()
        self.width = self._coreimage.width * self.STRETCH


    def idle(self):
        self.image_state = "idle"


    def move(self,  offset): 
        self.image_state = "run"
        self.pos = (self.MOVEMENT_SPEED * Vector(offset)) + self.pos


    def sprint(self, offset):
        new_offset = Vector(offset) * self.MOVE_INCREASE
        return new_offset


class NonPlayerCharacter(Character):


    def set_patrol(self, movementList):
        self.MOVEMENT_LIST = movementList
        self._move_index = 1
        self._x, self._y = 0, 0


    def update_movement(self):
        if (self._x == 0 and self._y == 0):
            self._x = self.MOVEMENT_LIST[self._move_index][0]
            self._y = self.MOVEMENT_LIST[self._move_index][1]
            self._move_index = (self._move_index + 1) % len(self.MOVEMENT_LIST)
        self._move_toward_goal()


    def _move_toward_goal(self):
        x_move, y_move = 0, 0

        # if the remaining movement is positive, then the movement toward
        # the respective axis is positive (right, up)
        # if the remaining movement is negative, then the movement toward
        # the respective axis is negative (left, down)
        if self._x != 0:
            x_move = self._x / abs(self._x)
        if self._y != 0:
            y_move = self._y / abs(self._y)

        # we subtract from the amount of movement we have left
        self._x -= x_move
        self._y -= y_move

        # then we move using the calculated movement
        self.move(Vector(x_move, y_move))


class PlayerCharacter(Character):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bag = ItemBag()


    def add_item(self, item):
        print("Player obtained item " + item)
        self.bag.add_item(item)