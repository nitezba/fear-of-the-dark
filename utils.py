import pygame, sys, random, os, math, json, ast, glob
# ======== MISC. ========
BASE_PATH = './'
def load_image(path):
    img = pygame.image.load(BASE_PATH + path).convert()
    img.set_colorkey((0, 0, 0))
    return img

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
# ========  ========