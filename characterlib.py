import kivy
kivy.require('1.10.1')

from kivy.vector import Vector
from kivy.properties import StringProperty

from imagelib import LoopingImage, OverlappingImage
from item import ItemBag

# TODO  Check if we should separate the 'patrolling' aspect of the NPC
#       to a separate class

class Character(LoopingImage, OverlappingImage):
    ''' class handling images of characters in the game '''
    STRETCH = 4
    MOVEMENT_SPEED = 5
    MOVE_INCREASE = 3

    image_state = StringProperty('')


    def idle(self):
        self.image_state = "idle"


    def move(self,  offset): 
        ''' move the character based on the movement speed and change
        animation to the running animation 
        
        Keyword arguments:
        offset  -- the amount of pixels that the character will move
        '''
        self.image_state = "run"
        self.pos = (self.MOVEMENT_SPEED * Vector(offset)) + self.pos


    def sprint(self, offset):
        ''' adjust movement based on the sprint-speed of the character
        
        Keyword arguments:
        offset  -- the amount of pixels the character is initially moving
        '''
        new_offset = Vector(offset) * self.MOVE_INCREASE
        return new_offset


class NonPlayerCharacterImage(Character):
    ''' class handling all non-player controlled characters' animation '''
    def set_patrol(self, movement_list):
        ''' sets the places that the NPC is meant to move to
        
        Keyword arguments:
        movement_list   --  a list of coordinates that the character will
                            move to in order of the elements
        '''
        self.MOVEMENT_LIST = movement_list
        self._move_index = 1

        # the amount of moves in a particular axis that the NPC expects
        self._x, self._y = 0, 0


    def update_movement(self):
        ''' called by the main class, updating the current goal as well as
        moving the NPC to said goal
        '''
        if len(self.MOVEMENT_LIST) > 0:
            # if no more movements left, shift to the next set of coordinates
            if self._x == 0 and self._y == 0:
                self._x = self.MOVEMENT_LIST[self._move_index][0]
                self._y = self.MOVEMENT_LIST[self._move_index][1]
                self._move_index = ((self._move_index + 1) 
                                    % len(self.MOVEMENT_LIST))
            self._move_toward_goal()


    def _move_toward_goal(self):
        ''' moves the NPC to the current pair of desired coordinates '''
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


class PlayerCharacter:
    ''' class handling the player-controlled characters '''
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.image = Character(image_name = "skelet")
        self.bag = ItemBag()


    def add_item(self, item):
        print("Player obtained item " + item)
        self.bag.add_item(item)