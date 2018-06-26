"""main():
    - main game loop
    - creation of Units to be in game instance
    - fixed calls to unit.choose_move() #this needs to be changed and moved into a new function that decides the turns using SPEED
    - win and lose conditions
    - play again/finish main game loop

-TO DO:
        - Abilities > abilityDict integration #as in make another file full of abilities, maybe unneeded?
        - Units > Abilities integration:
            - finish adding basic ability methods e.g. heal method
            - add getters/setters for Unit stats (for letting abilities change unit stats safetly)
        - Combat mechanics
            - include use of unit attributes e.g. DEF, ATK as damage modifiers
            - create sample abilities with current Unit stats and Ability attributes
        - create subclasses of Unit() with differing stats

v0.4.10 (almost)SIGNIFICANT CHANGES!
Changes:
    - Split main() and Unit class into seperate files
    - started Unit and Ability class integration
        - moved abilityDict (previously moveDict) to Ability as a class variable
        - added Abilities.get_attr() to get the value of an ability attribute
        - added Abilities.targeted(): Unit.choose_target() now passes targeted unit and move_chosen to it
        - added other methods in Ability class
            - damage calculation and attribute modifying will be handled by Ability class
    - Added Unit stat ATK (no use yet)
    - Modified Ability attributes (an ongoing change)

v0.4.20 lotsa
    - Added ability to add allies (controllable) into game
    - More abilities can be used now
        - Split unit.choose_target() into unit.determine_targets() and unit.select_target()
        - Abilities with TARGET_TYPE 
    - Multiplayer
        - changed many methods to be able to play as both teams i.e. controlling team 2 units is possible
        - change is_multiplayer to True to try
    - Changed how death works
        - added unit status x.alive (boolean) and Unit class variable lists team_zero_alive_list and team_one_alive_list
            - x.alive: only alive units can have moves and take damage
            - alive_lists are used for keeping track of number of alive units e.g. for win conditions
            - changed num_units() (previously numEnemies()), can use to find len() of both teams and their alive units
        - dead units are still kept in their team lists (for future revival abilities)
    - changed some ABILITY ATTRIBUTES to boolean
        - improved Ability.get_attr() to accommodate this
UPTO: 
"""
import os
import time
from collections import OrderedDict
from random import randint
from Units import Unit

def main():
    run_game = True
    is_multiplayer = False

    team_zero_limit = 1         #plus player
    team_one_limit = 4

    while run_game:

        name = input("What is your name?\n> ")
        if name == '':
            name = 'Player'
        elif name == 'test':
            is_multiplayer = True
        #initialise all Units that will be present in this game loop
        player = Unit(name, 0)

        #number of allies
        while True:
            try:
                num_allies = int(input("How many allies would you like? (Max {})\n> ".format(team_zero_limit)))
                if num_allies in range (0,team_zero_limit+1):
                    print("")
                    break
                elif num_allies < team_zero_limit:
                    print("Don't be a pussy ass nigga")
                else:
                    print("That's not a valid number.  Try again...")
            except ValueError:
                print("That's not a valid number.  Try again...")

        #select between 1-4 enemies, require a valid input
        while True:
            try:
                num_enemies = int(input("How many enemies would you like to fight? (Max {})\n> ".format(team_one_limit)))
                if num_enemies in range (1,team_one_limit+1):
                    print("")
                    break
                elif num_enemies == 0:
                    print("Don't be a pussy ass nigga")
                else:
                    print("That's not a valid number.  Try again...")
            except ValueError:
                print("That's not a valid number.  Try again...")

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
            for i in range(Unit.num_units(1, "all")):         #for each enemy
                if Unit.team_one_list[i].alive:
                    if is_multiplayer:                                                 #for multiplayer. enemy units will use comp_move instead of choose_move
                        Unit.team_one_list[i].choose_move()    
                    else:
                        Unit.team_one_list[i].comp_move()
                    time.sleep(1.0)
                    Unit.display_health()                  #display HP of all alive Units
                    time.sleep(.5)

                    if Unit.num_units(0, "alive") <= 0:               #team 1 win condition
                        print("\nYou win!\n")                   #
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
