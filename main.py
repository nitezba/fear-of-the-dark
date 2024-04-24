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
# borg.dest = (5,1)

frame_counter = FrameCounter()

frame_start = 0
frame_end = pygame.time.get_ticks()
dt = frame_end - frame_start

GamePrint("A Fear of the Dark consumes you.")

while playing:
    raw_window.fill((0,0,0))

    new_tile = None
    touching = False

    if death_counter == 1: 
        playCutscene(frame_counter)

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
            if player.can_walk :
                if event.key == K_w:
                    player.facing = 'u'
                    player.is_walking = True
                    frame_counter.walking += 12
                if event.key == K_a:
                    player.facing = 'l'
                    player.is_walking = True
                    frame_counter.walking += 12
                if event.key == K_s:
                    player.facing = 'd'
                    player.is_walking = True
                    frame_counter.walking += 12
                if event.key == K_d:
                    player.facing = 'r'
                    player.is_walking = True
                    frame_counter.walking += 12
            if event.key == K_SPACE :
                frame_counter.touching = 0
                player.stretch()
            if event.key == K_m :
                render_world = not render_world
            if event.key == K_p :
                render_player = not render_player
            if event.key == K_t :
                render_text = not render_text

        elif event.type == KEYUP : 
            if event.key == K_w and player.facing == 'u':
                player.is_walking = False
                frame_counter.walking = 0
            if event.key == K_a and player.facing == 'l':
                player.is_walking = False
                frame_counter.walking = 0
            if event.key == K_s and player.facing == 'd':
                player.is_walking = False
                frame_counter.walking = 0
            if event.key == K_d and player.facing == 'r':
                player.is_walking = False
                frame_counter.walking = 0
    
    if player.is_walking :
        # let's arbitrarily say that if we're walking, we're allowed to take a step every 16 (12 i guess) frames
        if frame_counter.walking % 12 == 0 :
            new_tile = player.move()
            print(new_tile)
        
        frame_counter.walking += 1

    # IF WE INTERACT WITH SOMETHING - ANYTHING - IN THE ENVIRONMENT, THIS HANDLES THE WORLD'S RESPONSE
    # we check the new_tile so that we can still respond specifically to the cases
    # where this is a "new" tile but we dont move to it. additionally to be able to make specific
    # responses to item pick ups
    # NOTE: i dont think we can check for enemy collision here since this only checks on an event happening on
    # A SINGLE FRAME

    curr_room_data = world.getRoomData(player.curr_room)

    if new_tile in curr_room_data.keys() : # since the keys are the coords with something in them
        if curr_room_data[new_tile] == 101 :
            GamePrint("You pick up the orb of shitting.", 'item')
            GamePrint("The world becomes clearer to you.", 'response')
            world.removeItem(player.curr_room, new_tile)
            pygame.mixer.Sound.play(s_item)
            render_world = True
            # need to find that item in our world dict and remove it though
        elif curr_room_data[new_tile] == 102 :
            GamePrint("You pick up the orb of pissing.", 'item')
            GamePrint("You seem to step outside yourself.", 'response')
            world.removeItem(player.curr_room, new_tile)
            pygame.mixer.Sound.play(s_item)
            render_player = True
        elif curr_room_data[new_tile] == 4:
            pygame.mixer.Sound.play(s_blocked_step)
            GamePrint("something blocks your path.", 'response')
    elif new_tile == -1 : # took a step, specifically down and outside the map
        pygame.mixer.Sound.play(s_blocked_step)
    elif new_tile != None : # took a step into empty space
        pygame.mixer.Sound.play(s_step)

    # game area
    if render_world :
        for tile_coord in curr_room_data.keys() :
            if curr_room_data[tile_coord] == 4 : # wall
                raw_window.blit(tile_sprite, (tile_coord[0] * 16, tile_coord[1] * 16))
            if curr_room_data[tile_coord] == 101 :
                raw_window.blit(eye_sprite, (tile_coord[0] * 16, tile_coord[1] * 16))
            if curr_room_data[tile_coord] == 102 :
                raw_window.blit(eye2_sprite, (tile_coord[0] * 16, tile_coord[1] * 16))

    if render_player :
        raw_window.blit(player_sprite, (player.pos[0] * 16, player.pos[1] * 16))

    # ENEMY RENDERING + LOGIC (might be smart to decouple these later)
    # if in the same room as an (the) enemy
    if player.curr_room == borg.curr_room :
        borg.dest = tuple(player.pos)
        if borg.move_to_dest() :
            # borg.flip_dest()
            pass
        
        if player.pos == borg.pos and death_counter == 0: 
            render_player       = False
            render_world        = False
            render_text         = True
            player.can_walk     = False
            death_counter = 1
            pygame.mixer.Sound.play(s_death)
            
        raw_window.blit(enemy_sprite, (borg.pos[0] * 16, borg.pos[1] * 16))

    # outstretched hand action
    if player.is_touching and frame_counter.touching < 6:
        raw_window.blit(grab_sprite, (player.touched_tile[0] * 16, player.touched_tile[1] * 16))
        frame_counter.touching += 1
    else : 
        player.is_touching = False
        player.touched_tile = None
    
    # text area =====           
    pygame.draw.rect(raw_window, (0, 0, 0), pygame.Rect(0, 144, WIN_WIDTH, 64))
    # pygame.draw.rect(raw_window, (255, 255, 255), pygame.Rect(0, 144, WIN_WIDTH, 64))
    # TEXT RENDERING ==========
    
    line_num = 0
    if render_text :
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