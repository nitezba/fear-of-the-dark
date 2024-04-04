# ==================
# FEAR OF THE DARK
# this started as an idea about explorin just my room in the dark to find and item
# but how about a whole adventure game set in the dark
# ==================
# SFXR
# LOOK INTO GENERATING SOUND EFFECTS MAYBE!!!!!
# --------------------
# idea - dungeon starts out as a normal thing, you can see everything and navigate normally
# then, into one of the 2-1 room, a scripted death. your eyes have fallen out of your sockets
# left and right rooms can contain (optional) hints? items? instructions on the stretch?
# whille you have your eyes, you can be given the goal - reach the last room in the dungeon

# being able to type into the thing as a subversion later in the game would be cool, especially in a scenario where 
# your normal actions are failing
# --------------------
# You step forward, into a world unknown. 
# Every step could mean your demise, and yet you press forward, unwavering.
# TODO: inline overflow
# TODO: load in multiple screens as a full map - PCG CAN COME IN HERE
# TODO: powerupsz
# there should be a power up to reveal the players location and a 
# separate one to show the map ( you can only have one at a time)
    # player location one should reveal enemies as well but maybe make them move as a consequence (they'd be static in the dark)
    # seeing the world one should also reveal secrets but AT WHAT COST
    # one of the powerups should also reveal items in the world - should it be world or player revealing one though (im thinking player)

    # maybe having the map off will tell you your coords by default

    # another idea, maybe you walk into a room, see two identical eyes, but one is for seeing the world, the other for yourself, you dont know which
    # picking one up removes the other one
# TODO: health
# TODO: pause menu
# TODO: different color letters for different actions so you can quickly tell without having to 
# read the same thing multiple times

# TODO: maybe the eye could be a switch on a timer instead of a permanent upgrade 
# (or both and it just varies depending on the room - like oops your eyes fell out again)

# TODO: game design problem - locating yourself when you lose track of where you are - WITHOUT reading coords

# TODO: going to need a separate function to load the kind of file that will get outputted by the save function

# TODO: locked doors between rooms and keys that open them, which implies the need for an inventory

import pygame, sys, random, os, math, json, ast, glob
clock = pygame.time.Clock()
from pygame.locals import *
from utils import *

# https://stackoverflow.com/questions/13356752/pygame-has-huge-delay-with-playing-sounds
pygame.mixer.pre_init(44100, -16, 2, 256)
pygame.mixer.init()
pygame.init()

WIN_WIDTH = 160 + 1 # one extra pixel for text readability
WIN_HEIGHT = 144 + (6 * 5) # 5 sentences each one 6px tall in the text boxx=
WIN_SCALE = 3

display_window = pygame.display.set_mode((WIN_WIDTH * WIN_SCALE, WIN_HEIGHT * WIN_SCALE), 0, 32)
raw_window = pygame.Surface((WIN_WIDTH,WIN_HEIGHT))

s_step          = pygame.mixer.Sound("./sfx/step.wav")
s_death         = pygame.mixer.Sound("./sfx/death.wav")
s_destroy_tile  = pygame.mixer.Sound("./sfx/destroy_tile.wav")
s_hand          = pygame.mixer.Sound("./sfx/hand.wav")

# "Waltz, bad nymph, for quick jigs vex." 
# "Glib jocks quiz nymph to vex dwarf." 
# "Sphinx of black quartz, judge my vow." 
# "How quickly daft jumping zebras vex!" 
# "The five boxing wizards jump quickly." 
# "Jackdaws love my big sphinx of quartz." 
# "Pack my box with five dozen liquor jugs." 
# https://www.pygame.org/wiki/Spritesheet
chars = load_image('./letters/alphabet.png')
alphanumeric = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z','0','1','2','3','4','5','6','7','8','9', ' ', '.']
# 40 CHARACTERS FIT IN A LINE BEFORE OVERFLOW
def TextToImg(text : str) -> list:
    # given text, we want to turn each character into an integer that can be used to go into the 
    # sprite sheet and get the corresponding letter to then put it into Sprite()
    utext = text.upper()
    sentence = []
    for c in utext :
        index = alphanumeric.index(c)
        sprite_x = index * 4

        subsurf : pygame.Surface = chars.subsurface(pygame.Rect(sprite_x, 0, 4, 4))
        # sentence.append(Sprite(None, subsurf))
        sentence.append(subsurf)

    return sentence

on_screen_text = [] # should only ever have size five
def GamePrint(text : str) :
    if len(text) <= 40 :
        on_screen_text.append(TextToImg(text))
    else :
        left = text[0:40]
        on_screen_text.append(TextToImg(left))
        on_screen_text.append(TextToImg(text[40:]))

# W = loadRoom('./map/r1-0.json')
world = loadWorld()
# saveWorld(world)

render_world = True
render_player = True
tile_sprite     = load_image('./sprites/tile.png')
player_sprite   = load_image('./sprites/player.png')
eye_sprite      = load_image('./sprites/eye.png')
eye2_sprite     = load_image('./sprites/eye2.png')
grab_sprite_raw = load_image('./sprites/grab.png')
grab_sprite = pygame.transform.scale(grab_sprite_raw, (16,16))

class Entity() :
    def __init__(self, pos : list) -> None:
        self.pos        : list  = pos
        self.facing     : str   = 'u'
        self.health     : int   = 5
        self.curr_room  : str   = '1-0'
        self.inventory  : list  = []

    # return none on success, flag on collision check
        # NEW (maybe - i think i can flag) : return tuple,
        # nnvm that doesnt work cuz we're supposed to be removing from the world dict
        # HOWEVER, MAYBE WE CAN LEAVE IT IN THE WORLD AND JUS USE AN EXTERNAL FLAG TO MARK IT AS INACTIVE
    def move(self, direction : str) -> int:
        x_borders = [0, 9]
        y_borders = [0, 8]
        
        self.facing = direction
        original_pos = [self.pos[0], self.pos[1]]
        if direction == 'u' :
            self.pos[1] -= 1
        if direction == 'l' :
            self.pos[0] -= 1
        if direction == 'd' :
            self.pos[1] += 1
        if direction == 'r' :
            self.pos[0] += 1

        # self.pos ends up (temporarily) being the new pos, until it gets error corrected if needed

        # world collision handling
        if tuple(self.pos) in world[self.curr_room].keys() :
            if world[self.curr_room][tuple(self.pos)] == 4 :
                GamePrint("something blocks your path.")
                invalid_pos = [self.pos[0], self.pos[1]]
                self.pos = original_pos
                return world[self.curr_room][tuple(invalid_pos)]

        # ==========================================
        if self.pos[1] > 8 : # down room change
            if self.curr_room[0] == '1' : # off screen
                GamePrint("only nothingness awaits you there")
                self.pos = original_pos
                return -1 # might need to be different since this is the same as a successful step
            else : # just move down normally
                GamePrint("southbound for some reason")
                prev_level : int = int(self.curr_room[0])
                room : str = self.curr_room[1:3]

                new_level = prev_level - 1
                new_room_num = str(new_level) + room
                self.curr_room = new_room_num
                self.pos = [original_pos[0], 0]
        if self.pos[1] < 0 :
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
        GamePrint("every step you take could be the end")
        # if it's some tile, which we've already checked is not a wall/invalid tile
        if tuple(self.pos) in world[self.curr_room].keys() :
            return world[self.curr_room][tuple(self.pos)]
        
        return -1

    # there should be a limit on the number of times you can stretch your hand out
    # there should also be some other way to interact with the world, maybe different responses for walking into stuff
    def stretch(self) -> int:
        pygame.mixer.Sound.play(s_hand)
        # on_screen_text.append(TextToImg("you stretch your hand into the unknown."))
        GamePrint("you stretch your hand into the unknown.")
        front : tuple = None
        if self.facing == 'u' :
            front = (self.pos[0], self.pos[1] - 1)
        if self.facing == 'l' :
            front = (self.pos[0] - 1, self.pos[1])
        if self.facing == 'd' :
            front = (self.pos[0], self.pos[1] + 1)
        if self.facing == 'r' :
            front = (self.pos[0] + 1, self.pos[1])
            
        ret = world['1-0'][front] if front in world['1-0'].keys() else -1
        # TODO: this isn't returning what i think it is sometimes, second to last room is where i found this
        if ret == -1:
            GamePrint("you find nothing...")
        if ret == 4:
            GamePrint("you meet the cold indifference of the wall")
        # maybe this could hurt if you stretch and touch something bad, but you
        # still only get a limited number of stretches (your arm gets tired)
        
        return ret

playing = True

player = Entity(
    [5, 8] # starting pos at bottom middle of grid
)

eye_coords = generateRandomCoords()
while eye_coords in world[player.curr_room].keys():
    eye_coords = generateRandomCoords()
# place the eye inside our actual data representation of the world
world[player.curr_room][eye_coords] = 7

    
eye2_coords = generateRandomCoords()
while eye2_coords in world[player.curr_room].keys():
    eye2_coords = generateRandomCoords()
world[player.curr_room][eye2_coords] = 8

frame_start = 0
frame_end = pygame.time.get_ticks()
dt = frame_end - frame_start

GamePrint("A Fear of the Dark consumes you.")

while playing:
    raw_window.fill((0,0,0))

    new_tile = None
    for event in pygame.event.get() :
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == KEYDOWN : 
            if event.key == K_ESCAPE:
                playing = False
            if event.key == K_w:
                new_tile = player.move('u')
                pygame.mixer.Sound.play(s_step)
            if event.key == K_a:
                new_tile = player.move('l')
                pygame.mixer.Sound.play(s_step)
            if event.key == K_s:
                new_tile = player.move('d')
                pygame.mixer.Sound.play(s_step)
            if event.key == K_d:
                new_tile = player.move('r')
                pygame.mixer.Sound.play(s_step)
            if event.key == K_SPACE :
                player.stretch()
            if event.key == K_m :
                render_world = not render_world
            if event.key == K_p :
                print("flip")
                render_player = not render_player
            print(new_tile)

    if new_tile == 7:
        GamePrint("The world becomes clearer to you.")
        render_world = True
        # need to find that item in our world dict and remove it though
    if new_tile == 8:
        GamePrint("You seem to step outside yourself.")
        render_player = True


    # game area
    if render_world :
        for tile_coord in world[player.curr_room].keys() :
            if world[player.curr_room][tile_coord] == 4 : # wall
                raw_window.blit(tile_sprite, (tile_coord[0] * 16, tile_coord[1] * 16))
            if world[player.curr_room][tile_coord] == 7 :
                raw_window.blit(eye_sprite, (eye_coords[0] * 16, eye_coords[1] * 16))
            if world[player.curr_room][tile_coord] == 8 :
                raw_window.blit(eye2_sprite, (eye2_coords[0] * 16, eye2_coords[1] * 16))


    if render_player :
        raw_window.blit(player_sprite, (player.pos[0] * 16, player.pos[1] * 16))

    
    # text area =====           
    pygame.draw.rect(raw_window, (255, 255, 255), pygame.Rect(0, 144, WIN_WIDTH, 64))
    # TEXT RENDERING ==========
    # overflow handling
    if len(on_screen_text) > 5:
        excess = len(on_screen_text) - 5
        for i in range(excess):
            on_screen_text.pop(i)

    line_num = 0
    for s in on_screen_text :
        num = 0
        for sprite in s:
            raw_window.blit(sprite, pygame.Rect(num * 4, 145 + (6 * line_num), 4, 4))
            num += 1
        line_num += 1

    # ========
    scaled_window = pygame.transform.scale(raw_window, display_window.get_size())
    display_window.blit(scaled_window, (0,0))
    pygame.display.update()

    # ========
    frame_end = pygame.time.get_ticks()
    dt = frame_end - frame_start
    clock.tick(60)

pygame.quit()
sys.exit()