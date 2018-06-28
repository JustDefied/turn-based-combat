"""main():
    - main game loop
    - creation of Units to be in game instance
    - fixed calls to unit.choose_move() #this needs to be changed and moved into a new function that decides the turns using SPEED
    - win and lose conditions
    - play again/finish main game loop

-TO DO:
        - Abilities > abilityDict integration #as in make another file full of abilities, maybe unneeded?
        - Ability
            - add more ability methods e.g. unit stat changing
            - each Ability object will need the target stored in a variable
            - how will ability_ID work?
            - include use of unit attributes e.g. DEF, ATK as damage modifiers
        - Unit
            - more unit stats
            - set a maximum for unit stats (in setters) to make calculations sound
            - create subclasses of Unit() with differing stats

v0.4.90
Changes:
    - Added ability.initial_healing, 'healing' works now
    - Ability now creates AbilityObjects, which will change the way abilities work
        - AbilityObjects store their attributes:values in ability.AttributeValueDict
        - AbilityObjects are stored in one queue Ability.Ability_queue and removed when finished
    - DoT and buff abilities can be made now
        - added LASTS ability attribute, which determines if an AbilityObject stays in Ability_queue after inital move
        - added Ability.check_abilityList() which will decide which AbilityObject in Ability_queue are removed/procced/ignored
        - added ability.special_sorter() to map AbilityObjects to their special methods
        - UnitObjects store a list of buff names in self.buffs, and is displayed beside HP display
        - made a first buff "Increase ATK"
    - Abilities now add ATK to their base damage
    - tidied determine_targets()
    - tidied output to console
    - split ability.targeted() into more simplified methods
    - determine_targets() and select_target() are now Ability instance methods (previously Unit instance methods)
    - re-added TARGET_NUM ability attribute (used for multiple target abilities, not fully implemented)
    - added SPECIAL ability attribute for abilities that have special mechanics and need their own methods
    - added getters/setters for Unit stats (some stats will only have a certain value range) which will be used by Ability methods

UPTO: make DEF calc
"""
import os
import time
from collections import OrderedDict
from random import randint
from Units import Unit

def main():
    run_game = True
    is_multiplayer = False

    team_zero_limit = 2         #plus player, min should be 1
    team_one_limit = 4

    while run_game:

        name = input("What is your name?\n> ")
        if name == '':
            name = 'Player'
        elif name == 'test':
            is_multiplayer = True
        #initialise all Units that will be present in this game loop
        player = Unit(name, 0)

        #select between 0 to team_zero_limit allies, require a valid input
        while True:
            try:
                num_allies = int(input("\nHow many allies would you like? (Max {})\n> ".format(team_zero_limit-1)))
                if num_allies in range (0,team_zero_limit):
                    print("")
                    break
                elif num_allies >= team_zero_limit:
                    print("\nDon't be a pussy ass nigga")
                else:
                    print("\nThat's not a valid number.  Try again...")
            except ValueError:
                print("\nThat's not a valid number.  Try again...")

        #select between 1-team_one_limit enemies, require a valid input
        while True:
            try:
                num_enemies = int(input("How many enemies would you like to fight? (Max {})\n> ".format(team_one_limit)))
                if num_enemies in range (1,team_one_limit+1):
                    print("")
                    break
                elif num_enemies == 0:
                    print("\nDon't be a pussy ass nigga")
                else:
                    print("\nThat's not a valid number.  Try again...")
            except ValueError:
                print("\nThat's not a valid number.  Try again...")

        for i in range(num_allies):
            Unit("Ally " + str(i+1), 0)

        for i in range(num_enemies):
            Unit("Enemy " + str(i+1), 1)

        #display HP of all alive Units
        Unit.display_health()

        #begin battle while loop, stop loop when either player or all enemies are dead
        while not Unit.num_units(0, "alive") <= 0 and not Unit.num_units(1, "alive") <= 0:

            time.sleep(0.5)
            print("---------[Team 1's turn]---------\n")
            time.sleep(0.5)
            for i in range(Unit.num_units(0, "all")):           #for each unit in list 0
                if Unit.team_zero_list[i].alive:
                    Unit.team_zero_list[i].choose_move()        #call fight function
                    time.sleep(1.0)
                    Unit.display_health()                       #display HP of all alive Units

                    if Unit.num_units(1, "alive") <= 0:         #team 0 win condition
                        print("\nYou win!\n")                   #
                        break                                   #
            if Unit.num_units(1, "alive") <= 0:                 #team 0 win condition
                break
            time.sleep(0.5)
            print("---------[Team 2's turn]---------\n")
            for i in range(Unit.num_units(1, "all")):         #for each unit in list 1
                if Unit.team_one_list[i].alive:
                    if is_multiplayer:                                                 #for multiplayer. enemy units will use comp_move instead of choose_move
                        Unit.team_one_list[i].choose_move()    
                    else:
                        Unit.team_one_list[i].comp_move()
                    time.sleep(1.0)
                    Unit.display_health()                  #display HP of all alive Units
                    time.sleep(.5)

                    if Unit.num_units(0, "alive") <= 0:               #team 1 win condition
                        print("\nYou lose!\n")                   #
                        break                                   #

        #play again?
        play_again = input("Would you like to play again? [Y/N]\n>")
        Unit.remove_all()
        if play_again.lower() == "y":
            print("\n\n\n\n\n\n RESTARTING \n")
            time.sleep(1)
            os.system('cls')
        else:
            run_game = False
            print("Goodbye")
            time.sleep(1.5)
            
main()
