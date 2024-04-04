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
import pygame
clock = pygame.time.Clock()
from pygame.locals import *
from utils import *

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
                new_tile : tuple = player.move('u')
                pygame.mixer.Sound.play(s_step)
            if event.key == K_a:
                new_tile : tuple = player.move('l')
                pygame.mixer.Sound.play(s_step)
            if event.key == K_s:
                new_tile : tuple = player.move('d')
                pygame.mixer.Sound.play(s_step)
            if event.key == K_d:
                new_tile : tuple = player.move('r')
                pygame.mixer.Sound.play(s_step)
            if event.key == K_SPACE :
                player.stretch()
            if event.key == K_m :
                render_world = not render_world
            if event.key == K_p :
                print("flip")
                render_player = not render_player
            print(new_tile)

    # IF WE INTERACT WITH SOMETHING - ANYTHING - IN THE ENVIRONMENT
    if new_tile in world[player.curr_room].keys() :
        if world[player.curr_room][new_tile] == 7:
            GamePrint("The world becomes clearer to you.")
            render_world = True
            # need to find that item in our world dict and remove it though
        if world[player.curr_room][new_tile] == 8:
            GamePrint("You seem to step outside yourself.")
            render_player = True
        if world[player.curr_room][new_tile] == 4:
            GamePrint("something blocks your path.")
        


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