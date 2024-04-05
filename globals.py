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
on_screen_text : list = [] # should only ever have size five
def GamePrint(text : str, text_type : str = None) :
    color = None
    if text_type == 'action' :
        color = (255, 0, 0)
    elif text_type == 'response' :
        color = (0, 212, 255)
    elif text_type == 'item' :
        color = (255, 0, 255)

    # TODO : could make purple for special item pick ups

    if len(text) <= 40 :
        on_screen_text.append(TextToImg(text, color))
    else :
        left = text[0:40]
        on_screen_text.append(TextToImg(left, color))
        on_screen_text.append(TextToImg(text[40:], color))

# ======== WORLD ========

# take json in directory and put it into a dict
def loadRoom(filename : str) -> dict:
    file = open(filename)
    data = json.load(file)
    world = {ast.literal_eval(k):v for (k,v) in data.items()}
    return world

def loadWorld() -> dict:
    # looks specifically for json files of the name "r1+1"
    world_dict = {}
    files = glob.glob("./map/r*.json")
    print(files)
    for filename in files:
        room : dict = loadRoom(filename)
        # this scans for the exact room "coords" for this specific storage method
        room_number : str = filename[7:10]
        world_dict[room_number] = room

    # return a dict of dict - outerkeys will be room index, inner dict will be specific room data
    return world_dict


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
world = loadWorld()

s_step          = pygame.mixer.Sound("./sfx/step.wav")
s_blocked_step  = pygame.mixer.Sound("./sfx/blocked_step.wav")
s_death         = pygame.mixer.Sound("./sfx/death.wav")
s_destroy_tile  = pygame.mixer.Sound("./sfx/destroy_tile.wav")
s_hand          = pygame.mixer.Sound("./sfx/hand.wav")
s_touch         = pygame.mixer.Sound("./sfx/touch.wav")
s_item          = pygame.mixer.Sound("./sfx/item.wav")

render_world = True
render_player = True
tile_sprite     = load_image('./sprites/tile.png')
player_sprite   = load_image('./sprites/player.png')
eye_sprite      = load_image('./sprites/eye.png')
eye2_sprite     = load_image('./sprites/eye2.png')
grab_sprite_raw = load_image('./sprites/grab.png')
grab_sprite     = pygame.transform.scale(grab_sprite_raw, (16,16))
enemy_sprite    = load_image('./sprites/enemy.png')

playing = True

death_counter = 0