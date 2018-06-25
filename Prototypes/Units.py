"""Construction: x = Unit(name (str), team (int))

Class methods
    - kill(unit): removes unit from its respective team list
    - numEnemies(): returns len() of enemy list (number of alive enemies)
    - display_health(): Prints HP of all currently alive Units in a formatted manner.

Instance methods
    - x.choose_move():
    - x.choose_target(move_name):
    - x.display_moves(movesList): shows the unit's list of moves
    - x.mp_check(mp_required): checks if enough mana, if enough then use that mana
    - x.dead(): returns True if Unit has 0 or less HP. Else returns False
"""
import time
from collections import OrderedDict
from random import randint
from Abilities import Ability

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

        self.ATK = 15
        self.DEF = 6            # dmg - defense = final dmg
        self.CRIT = 10       # 100% = 100
        self.SPEED = 12             # max speed is 20
        
        self.movesList = ["Punch", "Kick", "Magic bolt", "Heal"]

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
        print("========================================")
        for i in range(len(Unit.team_one_list)):
            enemy = Unit.team_one_list[i]
            print("{:9} HP:{:3}/{:3}        MP:{:3}/{:3}".format(enemy.name, enemy.hp, enemy.max_hp, enemy.mp, enemy.max_mp))
        print("========================================\n")

    def remove_all():
        for l in [Unit.team_zero_list,Unit.team_one_list]:
            l.clear()
            del l[:]

    #~~~~~~~~~~~~Instance methods~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __str__(self):
        return self.name

    def choose_move(self):
        #move selection process for player turn
        if self.team == 0:                                              #if calling unit is the player
            self.display_moves(self.movesList)
            #removed move_valid here for a simpler while loop
            while True:
                print("\n> What would you like to do?")
                try:
                    self_move = int(input(">"))                            #self_move is user input (int) -1 for move index
                    if self_move in range(1,len(self.movesList)+1):
                        move_name = self.movesList[self_move-1]                 #move_name is the name of chosen move (str)
                        mana_required = Ability.get_attr(move_name,"MP")
                        if self.mp_check(mana_required):                            #if passes mana check, move on to choose_target
                            break
                    else:                                                                           #if move not valid
                        print("Please enter a number between 1-{}\n".format(len(self.movesList)))       #print request for valid input
                except ValueError:          
                    print("Please enter a number between 1-{}\n".format(len(self.movesList)))           #print request for valid input
            print()
            self.choose_target(move_name)

        #action for computer turn
        else:                                                         #if computer is attacking (just do punch)
            for i in range(3):                                        #computer
                print(".",end="")                                     #...
                time.sleep(0.4)                                       #delay
            Unit.team_zero_list[0].hp -= 2                            #player loses HP
            print("{} punched you!".format(self.name))
            print("You took 2 damage\n")

    #use TARGET attributes to get target/s, calling an ability function for damage calculations/ability mechanics)
    def choose_target(self, move_name):
        for i in range(len(Unit.team_one_list)):                     #display all available targets
            print("{}. {}".format(i+1, Unit.team_one_list[i]))
        print("Who would you like to attack?")
        while True:
            try:
                attack_who = int(input("> "))                       #choose who to attack
                if attack_who in range(1,len(Unit.team_one_list)+1):
                    break
                else:
                    print("Please enter a valid number")
            except ValueError:
                print("Please enter a valid number")

        target_unit = Unit.team_one_list[attack_who-1]
        #call for Ability class to take over
        Ability.targeted(move_name, target_unit)


        #remove target if dead. should change to include any unit dead from AoE or DoT attacks
        if target_unit.dead():                             #or don't remove instantly after death, for possible revive abilities?        
            print("{} is down!\n".format(target_unit.name))
            Unit.kill(target_unit)                                 
            time.sleep(0.5)
        time.sleep(1.0)

    #takes a unit's movesList and displays it 
    def display_moves(self, movesList):
        for move in self.movesList:                                                 #print a list of available moves from dicts
            print("{}. {:15}".format(movesList.index(move) + 1, move), end='')      #
            if Ability.get_attr(move,"MP") != 0:                                    #
                print("MP cost: {}".format(Ability.get_attr(move,"MP")))            #
            else:                                                                   #
                print("No cost")                                                    #

    #checks if enough mana, if enough then use that mana
    def mp_check(self, mp_required):
        if mp_required <= self.mp:
            self.mp -= mp_required
            return True
        print("Not enough MP!\n")
        return False

    #checks if hp of a unit is <= 0
    def dead(self):
        if self.hp <= 0:
            return True
        return False
