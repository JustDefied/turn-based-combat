"""
-TO DO:
        - Abilities > abilityDict integration #as in make another file full of abilities, maybe unneeded?
        - Ability
            - add new abiltiy attribute BUFF_TRIGGER_ON for buffs, for when a buff should lose duration (turns_left)
                - if loses per caster turn, no changes needed (this is default)
                - if loses when being attacked, when another unit is targeted, 
                    - first check if targetting ability is ATTACK_TYPE = "NORMAL" or "MAGIC", 
                    - check target ability queue for IS_BUFF = TRUEs, and TRIGGER_ON = 1's then access those abilties, and -1 their turns_left
            - how will ability_ID work?
            - ability.special_sorter() needs a dictionary to map SPECIAL abilities to their methods
        - Unit
            - display_buff_prompts() should get prompts from a dicitonary rather than if/elifs
            - more unit stats, is SPEED needed
            - create subclasses of Unit() with differing stats
        - make comp_move actually go into Ability
        - include a description of abilities in ABILITY_ATTRIBUTES, as the first index in value, so they can be printed to output

v0.6.0
Changes:
    - made ATTRIBUTE_LIST more manageable, moved attributes around, have boolean for each section so not all sections need to be filled up
        - changed the way ability.AttributeValueDict is populated to accommodate this change
        - ABILITY ATTRIBUTE 'MP' is now 'MP_COST' and in its own section [2]
        - added MP_GAIN which is in REGEN section [4]
        - added DMG_TYPE and DMG_IS_PERCENT to DAMAGE section [3]
        - added new section BUFFS, with IS_BUFF, BUFF_STACKS, and BUFF_STATUS (BUFF_TRIGGER_ON not working yet)
   - buff-stacking is now controlled by ability attribute BUFF_STACKS
        - ability.check_stats will remove the earliest instance of the same buff if over stack limit
        - this is done by the unit.buff_stacks_dict which uses BUFF_STATUS as key and stacks as value
            - added modify_buff_stack_dict() to help modify the dict more easily
            - added display_buff_prompts() which displays buff messages by checking which buffs are in a unit's buff_stack_dict 
    - added ability attribute BUFF_STATUS which is a shortened indicator (str) of an ability, displayed in display_health()
        - uses modify_buff_stack_dict to determine which statuses are shown
    - added ability attribute BUFF_ENDS determines if a buff that is expired is removed before or after choose_move() messages
        - modified check_Ability_queue() to be able to be used at the beginning of unit.choose_move()
    -added ability attribute INFO, which contains info about an ability and is displayed during display_moves()
    - added ability to go back from 'choose target' to 'choose ability' (very messy)
    - split part of determine_targets() into a new method initial_cast() which calls cast_on_target() (formerly targeted())
    - Seperated several combat calculation methods for more accessibilty by SPECIAL ability mechanics
    - MP_GAIN is now managed in ability.calculate_heals() and actioned in Ability.heal_target()
    - DEF is now included in ability.calculate_def()
    - DODGE is now included in ability.ability_dodged() for offensive ability calculations
    - Created new abilities
    - created new subclasses
        - 'Knight' (with modified stats and unique abilities)
        - 'Thief' (with modified stats and unique abilities)
    - main() changes
        - put num_enemies, num_allies and play_again code blocks into their own helper functions get_num_enemies(), get_num_allies(), and play_again()
        - turned unit initialisation code block into Unit.create_units() 
        - No player name will default to 'Justin'
        - Use player name 'Knight' to play as Knight and 'Thief' to play as Thief
        - No 'num_allies' inputted will default to 0
        - No 'num_enemies' inputted will default to 1
    - console is now cleared after each team's turn
    - moved per-turn dead-checking and killing into a method Unit.downed() (may change later)
    - all unit stats have a maximum (in setter) to make calculations sound
    

UPTO: buff prompt dict, SPECIAL dict, BUFF_TRIGGER_ON, try add MAGIC, use all ability attributes
"""
import os
import time
from collections import OrderedDict
import random
from random import randint
from Units import Unit, Unit_Knight, Unit_Thief

team_zero_limit = 2         #plus player, min should be 1
team_one_limit = 4
is_multiplayer = True


def main(team_zero_limit, team_one_limit, is_multiplayer):
    run_game = True
    while run_game:
        #get player name input
        player_name = input("What is your name?\n> ")
        time.sleep(0.5)
        #get number of allies and enemies from input, then create those units and display their health
        num_allies = get_num_allies(team_zero_limit)
        time.sleep(0.5)
        num_enemies = get_num_enemies(team_one_limit)
        Unit.create_units(player_name, num_allies, num_enemies)

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
            time.sleep(1.0)
            Unit.display_health()                  #display HP of all alive Units
            time.sleep(1)

            os.system('cls')
            print("\n-----------[Team 2's turn]-----------")
            for unit in Unit.get_units("all", 1):         #for each unit in list 1
                if unit.alive:
                    if is_multiplayer:                       #for multiplayer. enemy units will use comp_move instead of choose_move
                        unit.choose_move()    
                    else:
                        unit.comp_move()

                    if Unit.num_units(0, "alive") <= 0:        #team 1 win condition
                        print("\nYou lose!\n")                 #
                        break                                  #
            time.sleep(1.0)
            Unit.display_health()                  #display HP of all alive Units
        Unit.remove_all()
        run_game = play_again()
########################################################################################
#select between 0 to team_zero_limit allies, require a valid input
def get_num_allies(team_limit):
    while True:
        try:
            num_allies_str = input("How many allies would you like? (Max {})\n> ".format(team_limit-1))
            if num_allies_str == '':
                num_allies = 0
                break
            num_allies = int(num_allies_str)
            if num_allies in range (0,team_limit):
                break
            elif num_allies >= team_limit:
                print("\nDon't be a pussy ass nigga")
            else:
                print("\nThat's not a valid number. Please try again.")
        except ValueError:
            print("\nThat's not a number. Please try again.")
    return num_allies

#select between team_one_limit enemies, require a valid input
def get_num_enemies(team_limit):
    while True:
        try:
            num_enemies_str = input("How many enemies would you like to fight? (Max {})\n> ".format(team_limit))
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
