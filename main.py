import pygame
clock = pygame.time.Clock()
from pygame.locals import *
from utils import *

player = Entity(
    [5, 8] # starting pos at bottom middle of grid
)

borg = Enemy(
    [1,1]
)
borg.curr_room = '2-0'
borg.dest = (5,1)

timer = Timer()

eye_coords = generateRandomCoords()
while eye_coords in world['2-0'].keys():
    eye_coords = generateRandomCoords()
# place the eye inside our actual data representation of the world
world['2-0'][eye_coords] = 7
# world[player.curr_room][eye_coords] = 7

    
eye2_coords = generateRandomCoords()
while eye2_coords in world['2-0'].keys():
    eye2_coords = generateRandomCoords()
world['2-0'][eye2_coords] = 8
# world[player.curr_room][eye2_coords] = 8

frame_start = 0
frame_end = pygame.time.get_ticks()
dt = frame_end - frame_start

GamePrint("A Fear of the Dark consumes you.")

while playing:
    raw_window.fill((0,0,0))

    new_tile = None
    # touched_tile = None
    touching = False

    if death_counter == 1: 
        playCutscene(timer)

    for event in pygame.event.get() :
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        # NOTE : adding 12 on keydown makes the first step instant and we add to it 
        # from there to make subsequent steps take longer
        if event.type == KEYDOWN : 
            print("KD")
            if event.key == K_ESCAPE:
                playing = False
            if event.key == K_w:
                player.facing = 'u'
                player.is_walking = True
                walk_frame_counter += 12
                # new_tile : tuple = player.move('u')
            if event.key == K_a:
                player.facing = 'l'
                player.is_walking = True
                walk_frame_counter += 12
                # new_tile : tuple = player.move('l')
            if event.key == K_s:
                player.facing = 'd'
                player.is_walking = True
                walk_frame_counter += 12
                # new_tile : tuple = player.move('d')
            if event.key == K_d:
                player.facing = 'r'
                player.is_walking = True
                walk_frame_counter += 12
                # new_tile : tuple = player.move('r')
            if event.key == K_SPACE :
                touch_frame_counter = 0
                # touched_tile : tuple = player.stretch()
                player.stretch()
            if event.key == K_m :
                render_world = not render_world
            if event.key == K_p :
                render_player = not render_player
            if event.key == K_t :
                render_text = not render_text
            # print(new_tile)

        elif event.type == KEYUP : 
            if event.key == K_w and player.facing == 'u':
                player.is_walking = False
                walk_frame_counter = 0
            if event.key == K_a and player.facing == 'l':
                player.is_walking = False
                walk_frame_counter = 0
            if event.key == K_s and player.facing == 'd':
                player.is_walking = False
                walk_frame_counter = 0
            if event.key == K_d and player.facing == 'r':
                player.is_walking = False
                walk_frame_counter = 0
    
    if player.is_walking :
        # let's arbitrarily say that if we're walking, we're allowed to take a step every 16 frames
        if walk_frame_counter % 12 == 0 :
            new_tile = player.move()
            print(new_tile)
        
        walk_frame_counter += 1

    # IF WE INTERACT WITH SOMETHING - ANYTHING - IN THE ENVIRONMENT, THIS HANDLES THE WORLD'S RESPONSE
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

    # if in the same room as an (the) enemy
    if player.curr_room == borg.curr_room :
        if borg.move_to_dest() :
            borg.flip_dest()
        
        if player.pos == borg.pos : 
            render_player = False
            death_counter = 1
        raw_window.blit(enemy_sprite, (borg.pos[0] * 16, borg.pos[1] * 16))

    if player.is_touching and touch_frame_counter < 6:
        raw_window.blit(grab_sprite, (player.touched_tile[0] * 16, player.touched_tile[1] * 16))
        touch_frame_counter += 1
    else : 
        player.is_touching = False
        player.touched_tile = None
    # if touching :
    #     raw_window.blit(grab_sprite, (touched_tile[0] * 16, touched_tile[1] * 16))
    
    # text area =====           
    pygame.draw.rect(raw_window, (0, 0, 0), pygame.Rect(0, 144, WIN_WIDTH, 64))
    # pygame.draw.rect(raw_window, (255, 255, 255), pygame.Rect(0, 144, WIN_WIDTH, 64))
    # TEXT RENDERING ==========
    
    line_num = 0
    for s in on_screen_text :
        num = 0
        if render_text :
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