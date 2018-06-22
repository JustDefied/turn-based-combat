import time
from collections import OrderedDict

"""
In main(), currently code contains
    - main game loop
    - creation of Units to be in game instance
    - fixed calls to fight() #this needs to be changed and moved into a new function that decides the turns using SPEED
    - win and lose conditions, leading to...
    - play again/finish main game loop

Helpers functions:
    - health_stat() is used to display HP of all units. #how to remove the need to pass the same arguments every time???
    - fight(), when used for player, currently
        - lists all moves available(only in normal_moves_dict right now)
        - deals DMG from simple damage-dealing moves (from normal_moves_dict, as opposed to DoT, AoE, healing, buffing moves)
        - checks and removes dead enemies from enemy list
       I will need to add
        - MP
        - moves other than simple damage-dealing
        - computer AI
        - #maybe having one dictionary of moves, with values as a compulsory list of stats(e.g. mana cost, hit-chance) would be better for future modification
        - #regarding moves other than simple damage-dealing ones, better to have this function call on lesser functions that will be easier to find and modify later

Classes:
    - Unit()
        - an object representing the player or an enemy, containing stats and moves
        I will need to add
        - New stats: DEF, SPEED

"""

#-------------------------------------------------------------------------------------
def main():
    run_game = True
    while run_game:

        #initialise all Units that will be present in this game instance
        player = Unit("Player")
        num_enemies = int(input("How many enemies would you like to fight? (Max 3)\n"))
        enemy_list = [None] * num_enemies                                               #create enemy list 
        for i in range(num_enemies):
            enemy_list[i] = Unit("Enemy " + str(i+1))                                   #fill list with Unit objects

        health_stat(player, enemy_list)                 ##display HP of all alive Units##
        
        #begin battle while loop
        while len(enemy_list) > 0 and not player.dead():    #stop loop when either player or enemies are dead

            time.sleep(0.5)             
            print("Your turn\n")
            time.sleep(0.5)             
            fight(player,enemy_list)                #call fight function for player against enemies
            time.sleep(1.0)
            
            health_stat(player, enemy_list)         ##display HP of all alive Units##

            if len(enemy_list) <= 0:                #win condition
                print("\nYou win!\n")               #
                break                               #
            #--------------------------------
            time.sleep(1.0)             
            print("Computer's turn\n")
            for i in range(len(enemy_list)):        #for each enemy
                fight(enemy_list[i],player)             #call fight function for enemy against player
                time.sleep(1)
                
                health_stat(player, enemy_list)         ##display HP of all alive Units##
                time.sleep(.5)          
                
                if player.dead():                       #lose condition
                    print("\nEnemy wins\n")             #
                    break                               #
                
        #play again?
        play_again = input("Would you like to play again? [Y/N]")
        if play_again.lower() == "y":
            print("\n\n\n\n\n\n RESTARTING \n")
            time.sleep(1)               #####
        else:
            run_game = False
            print("Goodbye")
            time.sleep(1.5)             #####
            
#-------------------------------------------------------------------------------------
            
#########################################################################
            
"""This is a helper function for main(), takes in player Unit and list of enemy Units.
Prints HP of all currently alive Units in a readable manner.
"""
def health_stat(player, enemy_list):   #prints hp of all alive Units
    print("\
Your health: {}\n\
============".format(player.hp))
    for i in range(len(enemy_list)):
        print("{} health: {}".format(enemy_list[i].name, enemy_list[i].hp))
    print("============\n")
    
#########################################################################

"""This function serves as the main combat system. Takes two parameters: the attacking Unit and the defending Unit
Currently, only simple damage-dealing type moves work.
If called for the player, inputs are required to complete the function.
    - If after completing the action, an enemy dies, they will be removed from the enemy list.
If called for an enemy, currently enemies will only use 'punch' move against the player.
"""
def fight(attacker, defender):
    #actions for player turn 
    if attacker.name == "Player":                               #if player is attacking
        movesList = []                                          #make an empty avaiable moves list        
        normalMoves = attacker.normal_moves_dict
        movesList.extend(list(normalMoves.keys()))              #add moves from normal moves dict to movesList
        move_legit = False                                          #
        while not move_legit:                                       #Set up a while loop while move is not legit
            
            print("What would you like to do?")
            for move in movesList:                                      #print a list of available moves from dicts
                print("{}. {}".format(movesList.index(move) + 1, move)) #
            self_move = int(input("> "))                            #ask for input
            
            if self_move in range(1,len(movesList)+1):              #input should a number corresponding to an index in movesList
                move_legit = True                                   #
                
                print("Who would you like to attack?")
                for i in range(len(defender)):                          #display all available targets
                    print("{}. {}".format(i+1,defender[i].name))        #
                attack_who = int(input("> "))                           #choose who to attack
                
                attacked_Unit = defender[attack_who-1]          
                move_name = movesList[self_move-1]
                damage_dealt = normalMoves[move_name]
                
                attacked_Unit.hp -= damage_dealt     #defender loses HP
                print("You used " + move_name)
                print("{} took {} damage!\n".format(attacked_Unit.name, damage_dealt))
                if attacked_Unit.dead():                                            #if defender dies                       
                    print("{} is down!\n".format(attacked_Unit.name))                          
                    del defender[attack_who-1]                                      #remove it from enemy list
                    
            else:                                                           #if move not legit
                print("Please choose one of the above\n")                   #print request for legit input
                
    #action for computer turn
    else:                               #if computer is attacking (just do punch)
        for i in range(3):                  #computer
            print(".",end="")               #...
            time.sleep(0.4) #####           #delay
        defender.hp -= 2                        #player loses HP
        print("{} punched you!".format(attacker.name))
        print("You took 2 damage\n")

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

"""Superclass called 'Unit' is constructed with one parameter 'name' (str).
Currently has variables for name (str), HP, MAX HP, MP, and MAX MP stats (all int).
It also has a dictionary 'normal_moves_dict' for normal moves (doesn't use MP, value = DMG) and 'special_moves_dict' for special moves (uses MP).
    - Values in 'special_moves_dict' contain a list relating to a move's [DMG, MP cost])

'name' is also used as an object's string representation

x.dead(): returns True if Unit has 0 or less HP. Else returns False 
"""
class Unit:
    def __init__(self, name):                                   
        self.name = name
        self.hp = 10
        self.max_hp = 10
        self.mp = 10
        self.max_mp = 10
        self.normal_moves_dict = OrderedDict((('Punch',3),('Kick',10)))             #ADD YOUR OWN MOVES
        self.special_moves_dict = OrderedDict((('Magic attack',[6,5]), ('Heal',[4,5])))     #yet to be implemented

    def __str__(self):
        return self.name

    def dead(self):             
        if self.hp <= 0:
            return True
        return False

    
main()
