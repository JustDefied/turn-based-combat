"""In main(), currently code contains
    - main game loop
    - creation of Units to be in game instance
    - fixed calls to fight() #this needs to be changed and moved into a new function that decides the turns using SPEED
    - win and lose conditions, leading to...
    - play again/finish main game loop

Helpers functions:
    - health_stat() is used to display HP of all units. #make into a class method??
       I will need to add
        - MP
        - moves (functions) other than simple damage-dealing
        - computer AI
        - #maybe having one dictionary of moves, with values as a compulsory list of stats(e.g. mana cost, hit-chance) would be better for future modification
        - #regarding moves other than simple damage-dealing ones, better to have this function call on lesser functions that will be easier to find and modify later

Classes:
    - Unit()
        - an object representing the player or an enemy, containing stats and moves
        I will need to add
        - New stats: DEF, SPEED

v0.4.01
Changes:
    - added name input for player
    - changed health_stat() to show max HP, MP, max MP
    - changed health_stat() to have no parameters, still same function
    - fight() has become an instance method of Unit
    - combined moves dicts and made all moves require [DMG,MP used] attributes
    - new Unit class methods:
        - kill() :used in fight()
        - numEnemies(): used in main()

v0.4.02 (Jono)
Changes:
    - not selecting between 1-3 enemies doesn't break the script
    - comment spring cleaning
    - recommended another file to store all the move information

UPTO: CHECK FOR MANA AVAILABILITY... USE TRY STATEMENT?
"""
import os
import time
from collections import OrderedDict

#-------------------------------------------------------------------------------------
def main():
    run_game = True
    while run_game:

        name = input("What is your name?\n> ")

        #initialise all Units that will be present in this game instance
        player = Unit(name, 0)

        #select between 1-3 enemies, require a valid input
        while True:
          try:
            num_enemies = int(input("How many enemies would you like to fight? (Max 3)\n> "))
            if num_enemies in range (1,4):
              break
            elif num_enemies == 0:
              print("Don't be a pussy ass nigga")
            else:
              print("That's not a valid number.  Try again...")
          except ValueError:
            print("That's not a valid number.  Try again...")

        #fill list with Unit objects
        for i in range(num_enemies):
            Unit("Enemy " + str(i+1), 1)

        #display HP of all alive Units
        health_stat()

        #begin battle while loop (stop loop when either the players or all enemies are dead)
        while Unit.numEnemies() > 0 and not player.dead():

            time.sleep(0.5)
            print("Your turn\n")
            time.sleep(0.5)
            player.fight()                #call fight function for player against enemies
            time.sleep(1.0)

            health_stat()                 #display HP of all alive Units

            if Unit.numEnemies() <= 0:    #win condition
                print("\nYou win!\n")     #
                break                     #
            #--------------------------------
            time.sleep(1.0)
            print("Computer's turn\n")
            for i in range(Unit.numEnemies()):        #for each enemy
                Unit.team_one_list[i].fight()         #call fight function for enemy against player
                time.sleep(1)

                health_stat()                         #display HP of all alive Units##
                time.sleep(.5)

                if player.dead():                     #lose condition
                    print("\nEnemy wins\n")           #
                    break                             #

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

#########################################################################
"""This is a helper function for main(), takes in player Unit and list of enemy Units.
Prints HP of all currently alive Units in a readable manner."""
def health_stat():   #prints hp of all alive Units
    print("\n========================")
    for i in range(len(Unit.team_zero_list)):
        friendly = Unit.team_zero_list[i]
        print("{}'s HP: {}/{}        MP: {}/{}".format(friendly.name, friendly.hp, friendly.max_hp, friendly.mp, friendly.max_mp))
    print("========================\n")
    for i in range(len(Unit.team_one_list)):
        enemy = Unit.team_one_list[i]
        print("{} HP: {}/{}        MP: {}/{}".format(enemy.name, enemy.hp, enemy.max_hp, enemy.mp, enemy.max_mp))
    print("========================\n")
#########################################################################

"""Superclass called 'Unit' is constructed with one parameter 'name' (str).
Currently has variables for name (str), HP, MAX HP, MP, and MAX MP stats (all int).
It also has a dictionary 'normal_moves_dict' for normal moves (doesn't use MP, value = DMG) and 'special_moves_dict' for special moves (uses MP).
    - Values in 'special_moves_dict' contain a list relating to a move's [DMG, MP cost])

'name' is also used as an object's string representation

Class methods
kill(unit): removes unit from its respective team list
numEnemies(): returns len() of enemy list (number of alive enemies)

Instance methods
x.dead(): returns True if Unit has 0 or less HP. Else returns False
x.fight(): This function serves as the main combat system. Takes two parameters: the attacking Unit and the defending Unit
            Currently, only simple damage-dealing type moves work.
            If called for the player, inputs are required to complete the function.
            If after completing the action, an enemy dies, they will be removed from the enemy list.
            If called for an enemy, currently enemies will only use 'punch' move against the player.
"""
class Unit:

    #all_units_list = []                    #Unit in index 0 should be player Unit
    team_zero_list = []
    team_one_list = []

    def __init__(self, name, team):         #use 'name' for unit name,
        self.name = name

        self.team = team                    #0 for player team, 1 for enemy team
        self.hp = 10
        self.max_hp = 10
        self.mp = 10
        self.max_mp = 10

        # Jono: should be in a seperate file, maybe JSON because python can read those pretty easily
        self.normal_moves_dict = OrderedDict((('Punch',[3,0]),('Kick',[10,0]),('Suck his dick', [-2,0]),('Magic attack',[6,5]), ('Heal',[4,5])))

        #all_units_list.append(self)
        if self.team == 0:
            Unit.team_zero_list.append(self)
        elif self.team ==1:
            Unit.team_one_list.append(self)

    #~~~~~~~~~~~~Class methods~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def kill(unit):
        if unit.team == 0:
            Unit.team_zero_list.remove(unit)
        if unit.team == 1:
            Unit.team_one_list.remove(unit)

    def numEnemies():
        return len(Unit.team_one_list)

    #~~~~~~~~~~~~Instance methods~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __str__(self):
        return self.name

    def dead(self):
        if self.hp <= 0:
            return True
        return False


    def fight(self):
        #actions for player turn
        if self.team == 0:                                                  #if player is attacking
            movesList = []                                                  #make an empty avaiable moves list
            normalMoves = self.normal_moves_dict
            movesList.extend(list(normalMoves.keys()))                      #add moves from normal moves dict to movesList
            move_legit = False                                              #
            while not move_legit:                                           #Set up a while loop while move is not legit

                print("What would you like to do?")
                for move in movesList:                                      #print a list of available moves from dicts
                    print("{}. {}".format(movesList.index(move) + 1, move)) #
                self_move = int(input("> "))                                #ask for input

                if self_move in range(1,len(movesList)+1):                  #input should be a number -1  corresponding to an index in movesList
                    move_name = movesList[self_move-1]
                    #if 

                    
                    move_legit = True                                       #

                    print("Who would you like to attack?")
                    for i in range(len(Unit.team_one_list)):                #display all available targets
                        print("{}. {}".format(i+1, Unit.team_one_list[i]))  #
                    attack_who = int(input("> "))                           #choose who to attack

                    attacked_Unit = Unit.team_one_list[attack_who-1]

                    damage_dealt = normalMoves[move_name][0]

                    attacked_Unit.hp -= damage_dealt                        #target loses HP
                    print("You used " + move_name)
                    print("{} took {} damage!\n".format(attacked_Unit.name, damage_dealt))
                    if attacked_Unit.dead():                                #if defender dies
                        print("{} is down!\n".format(attacked_Unit.name))
                        Unit.kill(attacked_Unit)                            #remove it from enemy list
                else:                                                       #if move not legit
                    print("Please choose one of the above\n")               #print request for legit input

        #action for computer turn
        else:                                                               #if computer is attacking (just do punch)
            for i in range(3):                                              #computer
                print(".",end="")                                           #...
                time.sleep(0.4)                                             #delay
            Unit.team_zero_list[0].hp -= 2                                  #player loses HP
            print("{} punched you!".format(self.name))
            print("You took 2 damage\n")



main()
