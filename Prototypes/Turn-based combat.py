"""
TO DO:
    - Ability
        - TARGET_TYPE multiple needs to be implemented
        - add new abiltiy attribute BUFF_TRIGGER_ON for buffs, for when a buff should lose duration (turns_left)
            - if loses per caster turn, no changes needed (this is default)
            - if loses when being attacked, when another unit is targeted, 
                - first check if targetting ability is ATTACK_TYPE = "NORMAL" or "MAGIC", 
                - check target ability queue for IS_BUFF = TRUEs, and TRIGGER_ON = 1's then access those abilties, and -1 their turns_left
        - buff prompt dict
        - make abilities that use all ability attributes i.e. DMG_IS_PERCENT and DMG_TYPE
        - how will ability_ID work?
    - Unit
        - unit creation system
        - display_buff_prompts() should get prompts from a dicitonary rather than if/elifs
        - add MAGIC 
        - is SPEED needed?
        - create subclasses of Unit() with differing stats

v0.6.2 
Changes:
    Units:
    - added randomized names for all created units (names_list in Unit.create_units())
    - moved mp usage into unit.initial_cast() so that it is only taken if cast is successful
    Abilities:
    - shortened some variable names in Ability
        - AttributeValueDict > AttrValDict
        - ATTRIBUTE_NAME_LIST > ATTR_NAME_LIST
        - ability_dict > aDict
    - changed check_Ability_queue() so that it procs abilities in reverse (so all buffs proc before the oldest can be removed)
    - ability.check_stacks() is now only called if the ability is successful (this only applies to buffs)
    - unit.modify_buff_stacks_dict is now only used at two points, in check_stacks() (called by inital_cast()), and in cast_on_target() if ability expires
    - added ability attribute CAN_DODGE in 'others' section, which signifies if dodge should be considered (ability_dodged() is called regardless, but will return False if CAN_DODGE = False)
    - ability.special_mapDict now maps abilities to their respective methods
    - added ability.buff_stat_modifier() which takes values from Ability.buffDict to modify unit stats  
    - removed unit.comp_move(), computer will now use choose_move()
        - is_multiplayer will decide whether team 2 is user or computer
        - computer goes through same method calls (with altered blocks)
        - computer will currently always choose moveList's index 1 move and a random enemy
    - changed when display_health() is used (once at beginning of choose_move, once at the end)
    - user is required to press enter after every move (otherwise text moves too fast) 

UPTO: add MAGIC/ MAGIC DEF??
"""
import os
import time
from collections import OrderedDict
import random
from random import randint
from Units import Unit, Unit_Knight, Unit_Thief, Unit_Priest

team_zero_limit = 2         #plus player, min should be 1
team_one_limit = 4
is_multiplayer = False


def main(team_zero_limit, team_one_limit, is_multiplayer):
    run_game = True
    while run_game:
        #get player name input
        player_name = input("What is your name?\n> ")
        time.sleep(0.2)
        num_allies = get_num_allies(team_zero_limit)
        time.sleep(0.2)
        num_enemies = get_num_enemies(team_one_limit)
        Unit.create_units(player_name, num_allies, num_enemies)
        input("\n<Press ENTER to start the battle>\n")
        #begin battle while loop, stop loop when all of one team is dead
        while not Unit.num_units(0, "alive") <= 0 and not Unit.num_units(1, "alive") <= 0:
            time.sleep(1)
            os.system('cls')
            print("-----------[Team 1's turn]-----------\n")
            for unit in Unit.get_units("all", 0):       #for each unit in team_zero
                if unit.alive:                              #if unit is alive
                    unit.choose_move()                      #call its choose_move function

                    #team 0 win condition
                    if Unit.num_units(1, "alive") <= 0:             
                        break                                   
            if Unit.num_units(1, "alive") <= 0:                 
                print("\nYou win!\n")                       
                break

            os.system('cls')
            print("\n-----------[Team 2's turn]-----------")
            for unit in Unit.get_units("all", 1):         #for each unit in list 1
                if unit.alive:
                    unit.choose_move(is_multiplayer = is_multiplayer)    

                    if Unit.num_units(0, "alive") <= 0:        #team 1 win condition
                        print("\nYou lose!\n")                 #
                        break                                  #
        Unit.remove_all()
        run_game = play_again()
########################################################################################
#select between 0 to team_zero_limit allies, require a valid input
def get_num_allies(team_limit):
    while True:
        try:
            num_allies_str = input("\nHow many allies would you like? (Max {})\n> ".format(team_limit-1))
            if num_allies_str == '':
                num_allies = 0
                break
            num_allies = int(num_allies_str)
            if num_allies in range (0,team_limit):
                break
            elif num_allies >= team_limit:
                print("\nYou can't have more than {} allies!".format(team_limit))
            else:
                print("\nThat's not a valid number. Please try again.")
        except ValueError:
            print("\nThat's not a number. Please try again.")
    return num_allies

#select between team_one_limit enemies, require a valid input
def get_num_enemies(team_limit):
    while True:
        try:
            num_enemies_str = input("\nHow many enemies would you like to fight? (Max {})\n> ".format(team_limit))
            if num_enemies_str == '':
                num_enemies = 1
                break
            num_enemies = int(num_enemies_str)
            if num_enemies in range (1,team_limit+1):
                break
            elif num_enemies == 0:
                print("\nYou need at least 1 enemy!. Please try again.")
            else:
                print("\nThat's not a valid number. Please try again.")
        except ValueError:
            print("\nThat's not a number. Please try again.")
    return num_enemies

def play_again():
    choice = input("Would you like to play again? [Y/N]\n>")
    
    if choice.lower() == "y":
        print("\n\n\n\n\n\n RESTARTING \n")
        time.sleep(1)
        os.system('cls')
        return True
    else:
        print("Goodbye")
        time.sleep(1.5)   
        return False 

main(team_zero_limit, team_one_limit, is_multiplayer)
