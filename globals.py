import pygame, json, random, glob, ast, sys, os

# https://stackoverflow.com/questions/13356752/pygame-has-huge-delay-with-playing-sounds
pygame.mixer.pre_init(44100, -16, 2, 256)
pygame.mixer.init()
pygame.init()

WIN_WIDTH = 160 + 1 # one extra pixel for text readability
WIN_HEIGHT = 144 + (6 * 5) # 5 sentences each one 6px tall in the text boxx=
WIN_SCALE = 3

display_window = pygame.display.set_mode((WIN_WIDTH * WIN_SCALE, WIN_HEIGHT * WIN_SCALE), 0, 32)
raw_window = pygame.Surface((WIN_WIDTH,WIN_HEIGHT))

# "Waltz, bad nymph, for quick jigs vex." 
# "Glib jocks quiz nymph to vex dwarf." 
# "Sphinx of black quartz, judge my vow." 
# "How quickly daft jumping zebras vex!" 
# "The five boxing wizards jump quickly." 
# "Jackdaws love my big sphinx of quartz." 
# "Pack my box with five dozen liquor jugs." 
# https://www.pygame.org/wiki/Spritesheet
BASE_PATH = './'
def load_image(path):
    img = pygame.image.load(BASE_PATH + path).convert()
    img.set_colorkey((0, 0, 0))
    return img

# https://gamedev.stackexchange.com/questions/26550/how-can-a-pygame-image-be-colored
# ^^ for coloring the letters ^^
def color_surface(surface : pygame.Surface, rgb : tuple = None) :
    arr = pygame.surfarray.pixels3d(surface)
    arr[:,:,0] = rgb[0]
    arr[:,:,1] = rgb[1]
    arr[:,:,2] = rgb[2]

chars = load_image('./letters/alphabet.png')
alphanumeric = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z','0','1','2','3','4','5','6','7','8','9', ' ', '.']
# 40 CHARACTERS FIT IN A LINE BEFORE OVERFLOW
def TextToImg(text : str, rgb : tuple = None) -> list:
    utext = text.upper()
    sentence = []

    for c in utext :
        index = alphanumeric.index(c)
        sprite_x = index * 4

        letter : pygame.Surface = chars.subsurface(pygame.Rect(sprite_x, 0, 4, 4))
        if rgb != None :
            letter.convert_alpha()
            
            colored_letter = letter.copy()
            color_surface(colored_letter, rgb)
            sentence.append(colored_letter)
        else :
            sentence.append(letter)


    return sentence

# TODO : make it print one color for text that describes user action and another color for text that responds to that action
# TODO: once colors are picked out more, i think player action text should be the same
# color as the player and world as the world
# BUG : repeated print is weird with multi lines, try touching a wall a bunch
    # THIS IS BECAUSE OF REPEATED CALLS TO GAMEEPRINT
on_screen_text  : list = [] # should only ever have size five
raw_text        : list = []
def GamePrint(text : str, text_type : str = None, allow_repeat : bool = True) :
    color = None
    if text_type == 'action' :
        color = (255, 0, 0)
    elif text_type == 'response' :
        color = (0, 212, 255)
    elif text_type == 'item' :
        color = (255, 0, 255)
    elif text_type == 'highlight' :
        color = (255, 255, 0)

    if len(text) <= 40 :
        if not allow_repeat :
            if raw_text[4] == text : # trying to add something that is the same as last thing printed
                return

        raw_text.append(text)
        on_screen_text.append(TextToImg(text, color))
        if len(on_screen_text) > 5:
            raw_text.pop(0)
            on_screen_text.pop(0)
    else :
        left = text[0:40]
        on_screen_text.append(TextToImg(left, color))
        on_screen_text.append(TextToImg(text[40:], color))
        if len(on_screen_text) == 6:
            on_screen_text.pop(0)
        elif len(on_screen_text) == 7:
            print("len 8")
            on_screen_text.pop(0)
            on_screen_text.pop(1)
        elif len(on_screen_text) == 8:
            on_screen_text.pop(0)
            on_screen_text.pop(1)
            on_screen_text.pop(2)

    # overflow handling
    # if len(on_screen_text) > 5:
    #     excess = len(on_screen_text) - 5
    #     for i in range(excess):
    #         on_screen_text.pop(i)

# ======== WORLD ========

# ============================================================

class World() :
    def __init__(self) -> None:
        self.world_data     : dict = {}
        # idk if this makes things easier or not but at the moment it makes sense
        # to keep a separate list of item names and their respective coords in a dict
        # actually i think it makes more sense if the key is the items unique integer and
        # the value is the sprite itself?
        self.items          : dict = {}

    def getRoomData(self, room : str) -> dict :
        return self.world_data[room]

    # returns the empty/steppable tiles nearby a coord
    def getValidNeighbors(self, room : str, coords : tuple) -> dict :
        left = (coords[0] - 1, coords[1]) if coords[0] > 0 else None
        right = (coords[0] + 1, coords[1]) if coords[0] < 9 else None  # 10 should be the tile limit
        top = (coords[0], coords[1] - 1) if coords[1] > 0 else None
        bottom = (coords[0], coords[1] + 1) if coords[1] < 8 else None  # 9 should be the tile limit
 
        all_neighbors = {'l' : left, 'r' : right, 'u' : top, 'd' : bottom}
        valid_neighbors = {}
        for elt in all_neighbors:
            if all_neighbors[elt] != None :
                valid_neighbors[elt] = all_neighbors[elt]

        steppable_neighbors = {}
        curr_room = self.getRoomData(room)
        # might need to remove this - premature optimization, since i think we need
        # to actually see it as a wall and give it that inf score
        for elt in valid_neighbors :
            check_for_wall = valid_neighbors[elt]
            if check_for_wall not in curr_room.keys() :
                steppable_neighbors[elt] = valid_neighbors[elt]
            elif curr_room[check_for_wall] == 4 :
                pass
            else : # that tile is likely an item
                steppable_neighbors[elt] = valid_neighbors[elt]

        return steppable_neighbors

    def removeItem(self, room : str ,tile : tuple) -> None :
        self.world_data[room].pop(tile)

    # loads an individual room from json
    def loadRoom(self, filename : str) -> dict :
        file = open(filename)
        data = json.load(file)
                # tuple : int are the kv pairs here
        world = {ast.literal_eval(k):v for (k,v) in data.items()}
        return world
    
    # loads every room file from a directory
    def loadWorld(self) -> None:
        # looks specifically for json files of the name "r1+1"
        world_dict = {}
        files = glob.glob("./map/r*.json")
        print(files)
        for filename in files:
            room : dict = self.loadRoom(filename)
            # this scans for the exact room "coords" for this specific storage method
            room_number : str = filename[7:10]
            world_dict[room_number] = room

        # return a dict of dict - outerkeys will be room index, inner dict will be specific room data
        # return world_dict
        self.world_data = world_dict

    # we're gonna make items 3 digit
    def spawnItems(self) -> None :
        eye_coords = generateRandomCoords()
        while eye_coords in self.world_data['2-0'].keys():
            eye_coords = generateRandomCoords()
        # place the eye inside our actual data representation of the world
        self.world_data['2-0'][eye_coords] = 101
        self.items['eye 1'] = eye_coords

        eye2_coords = generateRandomCoords()
        while eye2_coords in self.world_data['2-0'].keys():
            eye2_coords = generateRandomCoords()
        self.world_data['2-0'][eye2_coords] = 102
        self.items['eye 2'] = eye2_coords


# TODO - move this into the class
def saveWorld(world : dict) -> None :
    save_dict = {}
    for room in world.keys() :
        room_dict = {}
        for pair in world[room].items() :
            room_dict[str(pair[0])] = pair[1]
        save_dict[room] = room_dict

    with open("world_save.json", "w") as outfile :
        json.dump(save_dict, outfile) 
    # TODO: going to need a separate function to load the kind of file that will get outputted by the save function

# need ints between 1 and 8 (inclusive) for x and 1 and 7 for y
def generateRandomCoords() -> tuple :
    x = random.randint(1, 8) 
    y = random.randint(1,7) 

    return (x,y)

# "GLOBAL" DATA DECLARATION
world = World()
world.loadWorld()
# world.spawnItems()

s_step          = pygame.mixer.Sound("./sfx/step.wav")
s_blocked_step  = pygame.mixer.Sound("./sfx/blocked_step.wav")
s_death         = pygame.mixer.Sound("./sfx/death.wav")
s_destroy_tile  = pygame.mixer.Sound("./sfx/destroy_tile.wav")
s_hand          = pygame.mixer.Sound("./sfx/hand.wav")
s_touch         = pygame.mixer.Sound("./sfx/touch.wav")
s_item          = pygame.mixer.Sound("./sfx/item.wav")
s_respawn       = pygame.mixer.Sound("./sfx/respawn.wav")
s_room_change   = pygame.mixer.Sound("./sfx/room_change.wav")

render_world    = True
render_player   = True
render_text     = False
render_enemy    = True
render_items    = True

tile_sprite     = load_image('./sprites/tile.png')
player_sprite   = load_image('./sprites/player.png')
eye_sprite      = load_image('./sprites/eye.png')
eye2_sprite     = load_image('./sprites/eye2.png')
grab_sprite_raw = load_image('./sprites/grab.png')
grab_sprite     = pygame.transform.scale(grab_sprite_raw, (16,16))
enemy_sprite    = load_image('./sprites/enemy.png')

playing = True

death_counter = -1