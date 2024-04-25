# FEAR OF THE DARK

This started as an idea about explorin just my room in the dark to find and item
but how about a whole adventure game set in the dark
==================
## IDEAS
- Dungeon starts out as a normal thing, you can see everything and navigate normally then, into one of the 2-1 room, a scripted death. your eyes have fallen out of your sockets (by an enemy? or just some malignant force of the dungeon)
- left and right rooms of the first level (1-_) can contain (optional) hints? items? instructions on the stretch?
- while you have your eyes, you can be given the goal - reach the last room in the dungeon
- being able to type into the thing to respond to the world or give a command/instruction as a subversion later in the game would be cool (let's say this becomes possible bc of currently unknown story reasons), maybe especially in a scenario where your normal actions are failing
- maybe there should be text that tells you when you're within range of an item, custom text per item
- RANDOMLY CENSORED TEXT COULD BE INTERESTING for obfuscating info, maybe there's a third eye, one that lets you see the text
    actually maybe you start with no third eye, but when you lose your two eyes, you gain this one and the ability to see text
    so in that opening "cutscene" i have planned, text would appear blocked out as you walk around- thought about it could
- maybe you walk into a room, see two identical eyes, but one is for seeing the world, the other for yourself, you dont know which picking one up removes the other one
- maybe the eye could be a switch on a timer instead of a permanent upgrade (or both and it just varies depending on the room - like oops your eyes fell out again)
- now that we've change the text background to be white, another subversion could be to allow the player to step into the text box at some point in the story

### ITEM IDEAS
- movement speed item
- torch to see immediately adjacent tiles

## DECISIONS

- we're gonna do the binding of isaac thing where you pick up an item get a cryptic description and the rest is for you to figure out
    - this would likely apply to future items, not our items of seeing right now as it's pretty obvious what those do

- there should be a power up to reveal the players location and a separate one to show the map ( you can only have one at a time maybe?)
    - player location one should reveal enemies as well but maybe make them move as a consequence (they'd be static in the dark)
    - seeing the world one should also reveal secrets but AT WHAT COST one of the powerups should also reveal items in the world - should it be world or player revealing one though (im thinking player)

    - maybe having the map off will tell you your coords by default

- you will die to one hit - part of the point is memorizing dungeon layout so it makes sense to make the player do it a few times

==================
## TODOS

### SMALL
- inline overflow in GamePrint() function (i.e. print sentences of more than 40 chars in a single call to the function)
    - obstacles: bug with how it pops existing elements in textbox
- player health 
- player inventory
    - this is a prerequisite for having locked doors between certain rooms (and keys that open them of course)
- inventory UI - I think i'd prefer to have an inventory button that just tells you what you have on you at the moment (might have to be max 5 because of line cap lmfao)
- make different sound effects for different movement directions

### LARGE
- load in multiple screens as a full map
    - we can PCG'ify overall world gen - possibly only keeping the first "dungeon" as a permanently set one
- a larger list of items/abilities than the two eyes
    - in adding more we need to also think about how theyd work with/without each of the eyes
- pause menu
- going to need a separate function to load the kind of file that will get outputted by the save function
- SFXR - LOOK INTO GENERATING SOUND EFFECTS MAYBE!!!!!
 
### BACKBURNER PROBLEMS
- locating yourself when you lose track of where you are WITHOUT reading coords

### DONE
- continuous keydown movement
- make hand animation stay out longer