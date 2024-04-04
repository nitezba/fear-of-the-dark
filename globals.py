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
s_death         = pygame.mixer.Sound("./sfx/death.wav")
s_destroy_tile  = pygame.mixer.Sound("./sfx/destroy_tile.wav")
s_hand          = pygame.mixer.Sound("./sfx/hand.wav")

render_world = True
render_player = True
tile_sprite     = load_image('./sprites/tile.png')
player_sprite   = load_image('./sprites/player.png')
eye_sprite      = load_image('./sprites/eye.png')
eye2_sprite     = load_image('./sprites/eye2.png')
grab_sprite_raw = load_image('./sprites/grab.png')
grab_sprite     = pygame.transform.scale(grab_sprite_raw, (16,16))

# FORMER ENTITY CLASS

playing = True
