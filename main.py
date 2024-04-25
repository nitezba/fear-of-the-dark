# TODO : BETTER NAVIGATION IN THE DARK - WITH ONLY ONE EYE
# - BONUS ITEMS IN THE SIDE ROOMS THAT YOU CAN ONLY PICK UP BEFORE PICKING UP EITHER OF YOUR EYES AND AFTER DYING
# - THINK SPECIFICALLY ABOUT HOW THE WORLD WILL RESPOND TO EACH EYE PICK UP

# item in side room will be extra life
    # this implies being able to survive a hit of an enemy - are all enemies kamikaze warriors
    # this implies the need for a health bar
    # kamikaze and projectiles

# MAYBE STRETCH SHOULD BE MORE LENIENT AND TELL YOU ALL NEIGHBORS
import pygame
clock = pygame.time.Clock()
from pygame.locals import *
from utils import *

player = Entity()
player.inventoryAdd('world eye')
player.inventoryAdd('self eye')
player.inventoryAdd('item eye')
player.resetToStart()

kamikaze = Enemy(
    [1,1]
)
kamikaze.curr_room = '2-0'

frame_counter = FrameCounter()

frame_start = 0
frame_end = pygame.time.get_ticks()
dt = frame_end - frame_start

while playing:
    raw_window.fill((0,0,0))

    new_tile = None
    touching = False

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
            if player.can_act :
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
                if player.inventoryContains('world eye') :
                    player.inventoryRemove('world eye')
                else :
                    player.inventoryAdd('world eye')
            if event.key == K_p :
                if player.inventoryContains('self eye') :
                    player.inventoryRemove('self eye')
                else :
                    player.inventoryAdd('self eye')
            if event.key == K_t :
                if player.inventoryContains('text eye') :
                    player.inventoryRemove('text eye')
                else :
                    player.inventoryAdd('text eye')
            if event.key == K_i :
                print(player.inventory)

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
        
        frame_counter.walking += 1

    # IF WE INTERACT WITH SOMETHING - ANYTHING - IN THE ENVIRONMENT, THIS HANDLES THE WORLD'S RESPONSE
    # we check the new_tile so that we can still respond specifically to the cases
    # where this is a "new" tile but we dont move to it. additionally to be able to make specific
    # responses to item pick ups

    curr_room_data = world.getRoomData(player.curr_room)

    if new_tile in curr_room_data.keys() : # since the keys are the coords with something in them
        if curr_room_data[new_tile] == 101 :
            GamePrint("You slide a slimy eye back into place.", 'item')
            GamePrint("The world becomes clearer to you.", 'response')
            world.itemRemove(player.curr_room, 101)
            player.inventoryAdd('world eye')
            pygame.mixer.Sound.play(s_item)

            world.itemRemove(player.curr_room, 102)
            GamePrint("You hear something crush your other eye", 'item')

            # need to find that item in our world dict and remove it though
        elif curr_room_data[new_tile] == 102 :
            GamePrint("You slide a slimy eye back into place.", 'item')
            GamePrint("You seem to step outside yourself.", 'response')
            world.itemRemove(player.curr_room, 102)
            player.inventoryAdd('self eye')
            pygame.mixer.Sound.play(s_item)

            world.itemRemove(player.curr_room, 101)
            GamePrint("You hear something crush your other eye.", 'item')
            
        elif curr_room_data[new_tile] == 171 : 
            GamePrint("You feel invigorated.", 'item')
            world.itemRemove(player.curr_room, 171)

            pygame.mixer.Sound.play(s_oneup)

        elif curr_room_data[new_tile] == 111 :
            if player.inventoryContains('self eye') :
                GamePrint("A faint light surrounds you.", 'item')
                world.itemRemove(player.curr_room, 111)
                player.inventoryAdd('torch')
                pygame.mixer.Sound.play(s_item)

        elif curr_room_data[new_tile] == 4:
            pygame.mixer.Sound.play(s_blocked_step)
            GamePrint("something blocks your path.", 'response', False)
    elif new_tile == -1 : # took a step, specifically down and outside the map
        pygame.mixer.Sound.play(s_blocked_step)
    elif new_tile != None : # took a step into empty space
        pygame.mixer.Sound.play(s_step)

    # game area
    if player.inventoryContains('world eye') : 
        for tile_coord in curr_room_data.keys() :
            world.renderTile(player.curr_room, tile_coord)
    elif render_items: 
        for tile_coord in curr_room_data.keys() :
            world.renderTile(player.curr_room, tile_coord, 'only items')
            
    if player.inventoryContains('self eye') : 
        raw_window.blit(player_sprite, (player.pos[0] * 16, player.pos[1] * 16))

        if player.inventoryContains('torch') : 
            adjacent_tiles = world.getValidNeighbors(player.curr_room, player.pos, True)
            for elt in adjacent_tiles.values() :
                print(elt)

    # outstretched hand action
    # NOTE - things are weird if i keep this coupled with the above render player check 
    # doing this separately here makes it so that if it's a frame where the action was detected
    # AND the rendering is true, then it'll respond, as opposed to an if then, which kinda
    # stores the stretch rendering for whenever the flag gets set
    if player.inventoryContains('self eye') and player.is_touching and frame_counter.touching < 6:
        raw_window.blit(grab_sprite, (player.touched_tile[0] * 16, player.touched_tile[1] * 16))
        frame_counter.touching += 1
    else : 
        player.is_touching = False
        player.touched_tile = None


    # ENEMY RENDERING + LOGIC (might be smart to decouple these later)
    # if in the same room as an (the) enemy
    if player.curr_room == kamikaze.curr_room :
        kamikaze.dest = tuple(player.pos)
        if kamikaze.move_to_dest() and death_counter == -1:
            # kamikaze.flip_dest()
            player.inventoryRemove('self eye')
            player.inventoryRemove('world eye')
            player.inventoryAdd('text eye')
            player.can_act      = False
            death_counter = 0
            world.spawnItems()
            pygame.mixer.Sound.play(s_death)
        
        # if player.pos == kamikaze.pos and death_counter == 0: 
        if render_enemy:
            raw_window.blit(enemy_sprite, (kamikaze.pos[0] * 16, kamikaze.pos[1] * 16))

    # text area =====           
    pygame.draw.rect(raw_window, (0, 0, 0), pygame.Rect(0, 144, WIN_WIDTH, 64))
    # pygame.draw.rect(raw_window, (255, 255, 255), pygame.Rect(0, 144, WIN_WIDTH, 64))
    # TEXT RENDERING ==========
    line_num = 0
    if player.inventoryContains('text eye'):
        for s in on_screen_text :
            num = 0
            for sprite in s:
                raw_window.blit(sprite, pygame.Rect(num * 4, 145 + (6 * line_num), 4, 4))
                num += 1
            line_num += 1

    if death_counter == 0: 
        if playCutscene(frame_counter, 'first death') :
            death_counter += 1
            render_enemy = False
            render_items = False
            pygame.mixer.Sound.play(s_respawn)
            GamePrint("A Fear of the Dark consumes you.", 'highlight')
            player.resetToStart()

    if death_counter == 1:
        if player.step_count == 5 :
            GamePrint("Your eyes are somewhere in this dungeon.", 'highlight', False)
        elif player.step_count == 10 :
            GamePrint("The sword at the end calls your name.", 'highlight', False)

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