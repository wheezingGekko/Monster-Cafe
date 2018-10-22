import kivy
kivy.require('1.10.1')

from kivy.vector import Vector
from kivy.properties import StringProperty

from imagelib import LoopingImage, OverlappingImage

class Character(LoopingImage, OverlappingImage):
    STRETCH = 4
    MOVEMENT_SPEED = 5

    image_state = StringProperty('')


    def __init__(self, **kwargs):
        super().__init__(**kwargs)


    def _get_transparency(self):
        left_transparency = self._find_left_transparency_size()
        right_transparency = self._find_right_transparency_size()

        left_transparency *= self.STRETCH
        right_transparency *= self.STRETCH

        return left_transparency, right_transparency


    def _find_left_transparency_size(self):
        true_left = self._coreimage.width
        for y in range(self._coreimage.height):
            for x in range(self._coreimage.width):
                if (self._coreimage.read_pixel(x, y)[-1] != 0
                        and x < true_left):
                    true_left = x
                    continue
        return true_left


    def _find_right_transparency_size(self):
        true_right = -1
        for y in range(self._coreimage.height):
            for x in range(self._coreimage.width - 1, -1, -1):
                if (self._coreimage.read_pixel(x, y)[-1] != 0
                        and x > true_right):
                    true_right = x
                    continue
        return self._coreimage.width - true_right


    def build(self):
        l_transparency, r_transparency = self._get_transparency()
        self.stretched_left = l_transparency
        self.stretched_right = r_transparency
        self.width = self._coreimage.width * self.STRETCH


    def idle(self):
        self.image_state = "idle"


    def move(self,  offset): 
        self.image_state = "run"
        self.pos = (self.MOVEMENT_SPEED * Vector(offset)) + self.pos 


class NonPlayerCharacter(Character):


    def setPatrol(self, movementList):
        self.MOVEMENT_LIST = movementList
        self._move_index = 1
        self._x, self._y = 0, 0


    def updateMovement(self):
        if (self._x == 0 and self._y == 0):
            self._x = self.MOVEMENT_LIST[self._move_index][0]
            self._y = self.MOVEMENT_LIST[self._move_index][1]
            self._move_index = (self._move_index + 1) % len(self.MOVEMENT_LIST)
        self._moveTowardGoal()


    def _moveTowardGoal(self):
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
    pass