"""main():
    - main game loop
    - creation of Units to be in game instance
    - fixed calls to fight() #this needs to be changed and moved into a new function that decides the turns using SPEED
    - win and lose conditions
    - play again/finish main game loop


-TO DO:
        - Abilities > abilityDict integration #as in make another file full of abilities, maybe unneeded?
        - Units > Abilities integration:
            - add code for abilities that use different targets in Unit.choose_target(), e.g. Heal (TARGET_TYPE = self) has no target
            - add getters/setters for most Unit stats
        - Combat mechanics
            - 
            -include use of unit attributes e.g. DEF, ATK as damage modifiers
            - create sample abilities with current Unit stats and Ability attributes
        - create subclasses of Unit() with differing stats

v0.4.04 (Jono)
Changes:
    - require valid enemy no. input
    - choose_move no longer breaks on string input
        - probably good to make the while True loops I was using into their own function as I'm sure it'll be reused a lot
        - but im too lazy to do it bigLeL
    - comment cleanup
    - 'gui' cleanup

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
    
UPTO: 
"""
import os
import time
from collections import OrderedDict
from random import randint
from Units import Unit

def main():
    run_game = True
    while run_game:

        name = input("What is your name?\n> ")
        if name == '':
            name = 'Player'
        #initialise all Units that will be present in this game loop
        player = Unit(name, 0)

        #select between 1-3 enemies, require a valid input
        while True:
            try:
                num_enemies = int(input("How many enemies would you like to fight? (Max 3)\n> "))
                if num_enemies in range (1,4):
                    print("")
                    break
                elif num_enemies == 0:
                    print("Don't be a pussy ass nigga")
                else:
                    print("That's not a valid number.  Try again...")
            except ValueError:
                print("That's not a valid number.  Try again...")

        for i in range(num_enemies):
            Unit("Enemy " + str(i+1), 1)

        #display HP of all alive Units
        Unit.display_health()

        #begin battle while loop, stop loop when either player or all enemies are dead
        while Unit.numEnemies() > 0 and not player.dead():

            time.sleep(0.5)
            print("[Your turn]")
            time.sleep(0.5)
            player.choose_move()                        #call fight function
            time.sleep(1.0)
            Unit.display_health()                       #display HP of all alive Units

            if Unit.numEnemies() <= 0:                  #win condition
                print("\nYou win!\n")                   #
                break                                   #
  
            time.sleep(0.5)
            print("[Computer's turn]")
            for i in range(Unit.numEnemies()):         #for each enemy
                Unit.team_one_list[i].choose_move()    #call fight function
                time.sleep(1.0)
                Unit.display_health()                  #display HP of all alive Units
                time.sleep(.5)

                if player.dead():                      #lose condition
                    print("\nEnemy wins\n")            #
                    break                              #

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
