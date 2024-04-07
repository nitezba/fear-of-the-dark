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
    touched_tile = None
    touching = False

    for event in pygame.event.get() :
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == KEYDOWN : 
            if event.key == K_ESCAPE:
                playing = False
            if event.key == K_w:
                new_tile : tuple = player.move('u')
            if event.key == K_a:
                new_tile : tuple = player.move('l')
            if event.key == K_s:
                new_tile : tuple = player.move('d')
            if event.key == K_d:
                new_tile : tuple = player.move('r')
            if event.key == K_SPACE :
                touched_tile : tuple = player.stretch()
                touching = True
            if event.key == K_m :
                render_world = not render_world
            if event.key == K_p :
                render_player = not render_player
            print(new_tile)

    # IF WE INTERACT WITH SOMETHING - ANYTHING - IN THE ENVIRONMENT
    if new_tile in world[player.curr_room].keys() :
        if world[player.curr_room][new_tile] == 7:
            GamePrint("You pick up the orb of shitting.", 'item')
            GamePrint("The world becomes clearer to you.", 'response')
            world[player.curr_room].pop(new_tile)
            pygame.mixer.Sound.play(s_item)
            render_world = True
            # need to find that item in our world dict and remove it though
        elif world[player.curr_room][new_tile] == 8:
            GamePrint("You pick up the orb of pissing.", 'item')
            GamePrint("You seem to step outside yourself.", 'response')
            world[player.curr_room].pop(new_tile)
            pygame.mixer.Sound.play(s_item)
            render_player = True
        elif world[player.curr_room][new_tile] == 4:
            pygame.mixer.Sound.play(s_blocked_step)
            GamePrint("something blocks your path.", 'response')
    elif new_tile != None : # took a step into nothing
        pygame.mixer.Sound.play(s_step)

    # IF WE STRETCH OUT HAND OUT TRYING TO TOUCH SOMETHING IN THE WORLD
    if touched_tile in world[player.curr_room].keys() :
        pygame.mixer.Sound.play(s_touch)
        if world[player.curr_room][touched_tile] == 4 :
            GamePrint("the cold indifference of the wall seems", 'response')
            GamePrint("to slap you in the face.", 'response')
        elif world[player.curr_room][touched_tile] == 7 :
            GamePrint("you feel a soft orb.", 'response')
    else :
        if touched_tile != None :
            # we have stretched out our hand and found nothing
            pygame.mixer.Sound.play(s_hand)
            GamePrint("you find nothing...", 'response')

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

    # TODO : need this to sustain for a bit longer than one frame lmfao
    if touching :
        raw_window.blit(grab_sprite, (touched_tile[0] * 16, touched_tile[1] * 16))
    
    # text area =====           
    pygame.draw.rect(raw_window, (0, 0, 0), pygame.Rect(0, 144, WIN_WIDTH, 64))
    # pygame.draw.rect(raw_window, (255, 255, 255), pygame.Rect(0, 144, WIN_WIDTH, 64))
    # TEXT RENDERING ==========
    # # overflow handling
    # if len(on_screen_text) > 5:
    #     excess = len(on_screen_text) - 5
    #     for i in range(excess):
    #         on_screen_text.pop(i)

    line_num = 0
    for s in on_screen_text :
        num = 0
        for sprite in s:
            raw_window.blit(sprite, pygame.Rect(num * 4, 145 + (6 * line_num), 4, 4))
            num += 1
        line_num += 1

    # ==============================
    scaled_window = pygame.transform.scale(raw_window, display_window.get_size())
    display_window.blit(scaled_window, (0,0))
    pygame.display.update()

    # ==============================
    frame_end = pygame.time.get_ticks()
    dt = frame_end - frame_start
    clock.tick(60)

pygame.quit()
sys.exit()