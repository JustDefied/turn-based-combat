"""In main(), currently code contains
    - main game loop
    - creation of Units to be in game instance
    - fixed calls to fight() #this needs to be changed and moved into a new function that decides the turns using SPEED
    - win and lose conditions, leading to...
    - play again/finish main game loop

Classes:
    - Unit()
        - an object representing the player or an enemy, containing stats and moves
    -TO ADD:
        - Ability class, each ability(type?) has its own method?
        
v0.4.02
Changes:
    - cleaned up output to console
    - mana check added as an instance method x.mana_check())
    - added new defence, crit_chance, speed stats
    - display_health() (previously health_stat()) is now a Unit class method
    - split fight() into smaller functions:
        - choose_move()
        - display_moves()
        - choose_target()
    - changed how move attributes are formatted + added new attributes

UPTO: GET CHOOSE TARGET TO WORK WITH DIFFERENT MOVES AND ADD NEW FUNCTIONS FOR THE MOVES
"""
import os
import time
from collections import OrderedDict
from random import randint
#-------------------------------------------------------------------------------------
def main():
    run_game = True
    while run_game:

        name = input("What is your name?\n> ")

        #initialise all Units that will be present in this game loop
        player = Unit(name, 0)
        num_enemies = int(input("How many enemies would you like to fight? (Max 3)\n> "))
        for i in range(num_enemies):
            Unit("Enemy " + str(i+1), 1)                                   
        Unit.display_health()                   ##display HP of all alive Units##

        #begin battle while loop
        while Unit.numEnemies() > 0 and not player.dead():    #stop loop when either player or enemies are dead

            time.sleep(0.5)
            print("Your turn")
            time.sleep(0.5)
            player.choose_move()                #call fight function
            time.sleep(1.0)
            Unit.display_health()               ##display HP of all alive Units##

            if Unit.numEnemies() <= 0:                  #win condition
                print("\nYou win!\n")                   #
                break                                   #
            #--------------------------------
            time.sleep(1.0)
            print("Computer's turn")
            for i in range(Unit.numEnemies()):        #for each enemy
                Unit.team_one_list[i].choose_move()               #call fight function
                time.sleep(1)
                Unit.display_health()           ##display HP of all alive Units##
                time.sleep(.5)

                if player.dead():                       #lose condition
                    print("\nEnemy wins\n")             #
                    break                               #

        #play again?
        play_again = input("Would you like to play again? [Y/N]\n>")
        if play_again.lower() == "y":
            print("\n\n\n\n\n\n RESTARTING \n")
            time.sleep(1)               #####
            os.system('cls')
        else:
            run_game = False
            print("Goodbye")
            time.sleep(1.5)             #####

#-------------------------------------------------------------------------------------
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

"""Superclass called 'Unit' is constructed with parameters 'name' (str) and 'team' (0 for player, 1 for enemy).
Currently has variables for name (str), HP, MAX HP, MP, and MAX MP stats (all int).
It also has a dictionary 'movesDict' for  moves
    - Values in 'movesDict' contain a list relating to a move's [DMG, MP cost])

'name' is also used as an object's string representation

Class methods
kill(unit): removes unit from its respective team list
numEnemies(): returns len() of enemy list (number of alive enemies)
display_health(): Prints HP of all currently alive Units in a formatted manner.

Instance methods
x.dead(): returns True if Unit has 0 or less HP. Else returns False
x.fight(): This function serves as the main combat system. Takes two parameters: the attacking Unit and the defending Unit
            Currently, only simple damage-dealing type moves work.
            If called for the player, inputs are required to complete the function.
            If after completing the action, an enemy dies, they will be removed from the enemy list.
            If called for an enemy, currently enemies will only use 'punch' move against the player.
"""
class Unit:
    team_zero_list = []
    team_one_list = []

    def __init__(self, name, team):                                 
        self.name = name
        self.team = team            #0= player , 1 = enemy
        self.hp = 30
        self.max_hp = 30
        self.mp = 20
        self.max_mp = 20

        self.defence = 6            # dmg - defense = final dmg
        self.crit_chance = 10       # 100% = 100
        self.speed = 12             # max speed is 20
        
        self.movesDict = OrderedDict((('Punch',       [[1,1], randint(8,12), 0, 0]),
                                    ('Kick',        [[1,1], randint(7,14), 2, 0]),
                                    ('Magic bolt',  [[1,1], randint(11,16), 6, 0]),
                                    ('Heal',        [[0], 0, 8, 10])))

        if self.team == 0:
            Unit.team_zero_list.append(self)
        elif self.team == 1:
            Unit.team_one_list.append(self)

    #~~~~~~~~~~~~Class methods~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #removes unit from its team list (only use after checking dead())
    def kill(unit):
        if unit.team == 0:
            Unit.team_zero_list.remove(unit)
        if unit.team == 1:
            Unit.team_one_list.remove(unit)
            
    def numEnemies():
        return len(Unit.team_one_list)

    #prints hp of all alive Units
    def display_health():   
        for i in range(len(Unit.team_zero_list)):
            friendly = Unit.team_zero_list[i]
            print("{:9} HP:{:3}/{:3}        MP:{:3}/{:3}".format(friendly.name, friendly.hp, friendly.max_hp, friendly.mp, friendly.max_mp))
        print("========================")
        for i in range(len(Unit.team_one_list)):
            enemy = Unit.team_one_list[i]
            print("{:9} HP:{:3}/{:3}        MP:{:3}/{:3}".format(enemy.name, enemy.hp, enemy.max_hp, enemy.mp, enemy.max_mp))
        print("========================\n")



    #~~~~~~~~~~~~Instance methods~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __str__(self):
        return self.name
    
    def choose_move(self):
        #move selection process for player turn
        if self.team == 0:                                  #if calling unit is the player
            movesList = []                                      #movesList is a list of keys(names) of this unit's dictionary of moves 
            movesList.extend(list(self.movesDict.keys()))          #
            move_valid = False                                          #Set up a while loop while move is not legit
            while not move_valid:                                       #
                self.display_moves(movesList)
                print("What would you like to do?")                                     #
                self_move = int(input("> "))                                            #self_move is user input (int) -1 for move index
                if self_move in range(1,len(movesList)+1):                              #
                    move_name = movesList[self_move-1]                                  #move_name is the name/key of chosen move (str)
                    mana_required = self.movesDict[move_name][2]
                    if self.mp_check(mana_required):                        #if passes mana check
                        move_valid = True                                               #
                        self.choose_target(move_name)                                       #move on to choose_target method
                else:                                                                   #if move not legit
                    print("Please enter a number between 1-{}\n".format(len(movesList)))    #print request for legit input
                    
        #action for computer turn
        else:                               #if computer is attacking (just do punch)
            for i in range(3):                  #computer
                print(".",end="")               #...
                time.sleep(0.4) #####           #delay
            Unit.team_zero_list[0].hp -= 2                        #player loses HP
            print("{} punched you!".format(self.name))
            print("You took 2 damage\n")


    #use TARGET attributes to get targets, make new functions for damage calculations/ability mechanics)
    def choose_target(self, move_name):
        #if 
        print("Who would you like to attack?")
        for i in range(len(Unit.team_one_list)):                          #display all available targets
            print("{}. {}".format(i+1, Unit.team_one_list[i]))        #
        attack_who = int(input("> "))                           #choose who to attack

        attacked_Unit = Unit.team_one_list[attack_who-1]

        damage_dealt = self.movesDict[move_name][1]

        attacked_Unit.hp -= damage_dealt     #target loses HP
        print("You used " + move_name)
        print("{} took {} damage!\n".format(attacked_Unit.name, damage_dealt))
        time.sleep(1.0)
        if attacked_Unit.dead():                                            #if defender dies
            print("{} is down!\n".format(attacked_Unit.name))
            Unit.kill(attacked_Unit)                                    #remove it from enemy list
            time.sleep(0.5)

    #takes a list of keys(str) of movesDict and displays it 
    def display_moves(self, movesList):
                for move in movesList:                                                  #print a list of available moves from dicts
                    print("{}. {:15}".format(movesList.index(move) + 1, move), end='')  #
                    if self.movesDict[move][2] != 0:                                    #
                        print("MP cost: {}".format(self.movesDict[move][2]))            #
                    else:                                                               #
                        print("No cost")                                                #

    #checks if enough mana, if enough then use that mana
    def mp_check(self, mp_required):
        if mp_required =< self.mp:
            self.mp -= mp_required
            return True
        print("Not enough MP!\n")
        return False
    
    #checks if hp of a unit is >0
    def dead(self):
        if self.hp <= 0:
            return True
        return False

main()
