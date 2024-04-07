from globals import *

class Entity() :
    def __init__(self, pos : list) -> None:
        self.pos        : list  = pos
        self.facing     : str   = 'u'
        self.is_walking : bool  = False
        self.is_touching: bool  = False
        self.touched_tile       = None
        self.health     : int   = 5
        self.curr_room  : str   = '1-0'
        self.inventory  : list  = []

    # def move(self, direction : str) -> tuple:
    def move(self) -> tuple:
        # TODO : move this into the if blocks so you can play a different sound based on what you actually end up doing
        # pygame.mixer.Sound.play(s_step)
        # self.facing = direction
        # original_pos = [self.pos[0], self.pos[1]]
        # if direction == 'u' :
        #     self.pos[1] -= 1
        # if direction == 'l' :
        #     self.pos[0] -= 1
        # if direction == 'd' :
        #     self.pos[1] += 1
        # if direction == 'r' :
        #     self.pos[0] += 1

        # NEW THING WE'RE TRYING - DIRECTION GETS HANDLED IN THE MAIN LOOP, THIS IS JUST IN CHARGE OF MOVING IT
        original_pos = [self.pos[0], self.pos[1]]
        if self.facing == 'u' :
            self.pos[1] -= 1
        if self.facing == 'l' :
            self.pos[0] -= 1
        if self.facing == 'd' :
            self.pos[1] += 1
        if self.facing == 'r' :
            self.pos[0] += 1

        # self.pos ends up (temporarily) being the new pos, until it gets error corrected if needed

        # world collision handling
        # NOTE: in the case of collision, we return the coords of the block we just collided with
        if tuple(self.pos) in world[self.curr_room].keys() :
            if world[self.curr_room][tuple(self.pos)] == 4 :
                pygame.mixer.Sound.play(s_blocked_step)
                invalid_pos = [self.pos[0], self.pos[1]]
                self.pos = original_pos
                return tuple(invalid_pos)

        # ==========================================
        # walk to different room - y direction
        if self.pos[1] > 8 : # down
            if self.curr_room[0] == '1' : # off screen
                GamePrint("only nothingness awaits you there")
                self.pos = original_pos
                # NOTE : this return is different from the rest - fine for now but fix later
                # pygame.mixer.Sound.play(s_step)
                return -1 # might need to be different since this is the same as a successful step
            else : # just move down normally
                GamePrint("southbound for some reason")
                prev_level : int = int(self.curr_room[0])
                room : str = self.curr_room[1:3]

                new_level = prev_level - 1
                new_room_num = str(new_level) + room
                self.curr_room = new_room_num
                self.pos = [original_pos[0], 0]
        if self.pos[1] < 0 : # up
            GamePrint("reach for da stars")
            prev_level : int = int(self.curr_room[0])
            room : str = self.curr_room[1:3]

            new_level = prev_level + 1
            new_room_num = str(new_level) + room
            self.curr_room = new_room_num
            self.pos = [original_pos[0], 8]

        # ========================================
        # walk to different room - x direction
        if self.pos[0] < 0 : # left
            GamePrint("westward bound in search of better")
            level : str = self.curr_room[0]
            prev_room : int = int(self.curr_room[2])

            if self.curr_room[1] == '-':
                prev_room *= -1

            new_room_num : int = prev_room - 1
            new_room_str : str = '-' + str(abs(new_room_num)) if new_room_num <= 0 else '+' + str(new_room_num)
            new_room = level + new_room_str

            self.curr_room = new_room
            self.pos = [9, original_pos[1]] # we are now in the rightmost corner of the next room
        elif self.pos[0] > 9 : # right
            GamePrint("eastward bound in hopes of different")
            level : str = self.curr_room[0]

            prev_room : int = int(self.curr_room[2])
            if self.curr_room[1] == '-':
                prev_room *= -1

            new_room_num : int = prev_room + 1
            new_room_str : str = '-' + str(abs(new_room_num)) if new_room_num <= 0 else '+' + str(new_room_num)
            new_room = level + new_room_str

            self.curr_room = new_room
            self.pos = [0, original_pos[1]] # we are now in the leftmost corner of the next room


        print("new pos", self.pos, " in room, ", self.curr_room)
        GamePrint("every step you take could be the end", 'action')
        # pygame.mixer.Sound.play(s_step)
        return tuple(self.pos)

    # there should be a limit on the number of times you can stretch your hand out
    # there should also be some other way to interact with the world, maybe different responses for walking into stuff
    def stretch(self) -> tuple:
        # GamePrint("you stretch your hand into the unknown.", 'action')
        GamePrint("Im gonna touch you vro...", 'action')
        front : tuple = None
        if self.facing == 'u' :
            front = (self.pos[0], self.pos[1] - 1)
        if self.facing == 'l' :
            front = (self.pos[0] - 1, self.pos[1])
        if self.facing == 'd' :
            front = (self.pos[0], self.pos[1] + 1)
        if self.facing == 'r' :
            front = (self.pos[0] + 1, self.pos[1])
            
        self.touched_tile = front
        self.is_touching = True

        if self.touched_tile in world[self.curr_room].keys() :
            pygame.mixer.Sound.play(s_touch)
            if world[self.curr_room][self.touched_tile] == 4 :
                GamePrint("the cold indifference of the wall seems", 'response')
                GamePrint("to slap you in the face.", 'response')
            elif world[self.curr_room][self.touched_tile] == 7 :
                GamePrint("you feel a soft orb.", 'response')
        else :
            if self.touched_tile != None :
                # we have stretched out our hand and found nothing
                pygame.mixer.Sound.play(s_hand)
                GamePrint("you find nothing...", 'response')
        
        return front
