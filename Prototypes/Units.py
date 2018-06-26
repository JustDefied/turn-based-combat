"""Construction: x = Unit(name (str), team (int))

Class methods
    - Unit.kill(unit): removes unit from its respective team list
    - Unit.num_units(): returns the len() of one of four team lists (zero/one, all/alive)
    - Unit.display_health(): Prints HP of all currently alive Units in a formatted manner.
    - Unit.currently_alive(team): returns len() of the team list or team alive list

Instance methods
    - choose_move(): get a valid move from user inpot
    - x.determine_targets(move_name):  Determine available target/s, calling select_target if needed, then calls Ability.targeted() or other Ability methods for damage calculations/ability mechanics)
    - x.select_target(move_name): Displays available targets then gets target unit from user input
    - x.display_moves(movesList): display the unit's list of moves
    - x.mp_check(mp_required): checks if enough mana, if enough then use that mana
    - x.is_dead(): returns True if Unit has 0 or less HP and changes x.alive = False. Else returns False
"""
import copy
import time
from collections import OrderedDict
from random import randint
from Abilities import Ability

class Unit:
    team_zero_list = []
    team_zero_alive_list = []
    team_one_list = []
    team_one_alive_list = []
    all_units_list = [team_zero_list, team_one_list]
    all_alive_units_list = [team_zero_alive_list, team_one_alive_list]

    def __init__(self, name, team):
        self.name = name
        self.team = team            #0= player , 1 = enemy
        self.hp = 30
        self.max_hp = 30
        self.mp = 100
        self.max_mp = 20

        self.ATK = 15
        self.DEF = 6            # dmg - defense = final dmg
        self.CRIT = 10       # 100% = 100
        self.SPEED = 12             # max speed is 20

        self.alive = True           #use to determine if unit is allowed a move and is targetable
        
        self.movesList = ["Punch", "Kick", "Big kick", "Magic bolt", "Heal self", "Heal", "Heal team"]

        if self.team == 0:
            Unit.team_zero_list.append(self)
            Unit.team_zero_alive_list.append(self)
        elif self.team == 1:
            Unit.team_one_list.append(self)
            Unit.team_one_alive_list.append(self)

    #~~~~~~~~~~~~Class methods~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #removes unit from its team alive_list (only use after checking is_dead())
    def kill(unit):
        if unit.team == 0:
            Unit.team_zero_alive_list.remove(unit)
        if unit.team == 1:
            Unit.team_one_alive_list.remove(unit)

    #returns len() of the team list or team alive list using parameters team = 0, 1, all_alive = "all", "alive"
    def num_units(team, all_or_alive):
        if team == 0:
            if all_or_alive == "all":
                return len(Unit.team_zero_list)
            elif all_or_alive == "alive":
                return len(Unit.team_zero_alive_list)
        if team == 1:
            if all_or_alive == "all":
                return len(Unit.team_one_list)
            elif all_or_alive == "alive":
                return len(Unit.team_one_alive_list)


    #prints hp of all alive Units
    def display_health():   
        print("========================================")
        for i in range(len(Unit.team_zero_list)):
            friendly = Unit.team_zero_list[i]
            print("{:9} HP:{:3}/{:3}        MP:{:3}/{:3}".format(friendly.name, friendly.hp, friendly.max_hp, friendly.mp, friendly.max_mp))
        print("----------------------------------------")
        for i in range(len(Unit.team_one_list)):
            enemy = Unit.team_one_list[i]
            print("{:9} HP:{:3}/{:3}        MP:{:3}/{:3}".format(enemy.name, enemy.hp, enemy.max_hp, enemy.mp, enemy.max_mp))
        print("========================================\n")

    def remove_all():
        for l in [Unit.team_zero_list,Unit.team_one_list]:
            l.clear()
            del l[:]

    #returns a list of currently alive units in chosen team
    def currently_alive(team):
        targets_alive = []
        for i in range(len(team)):                     
            if team[i].alive:
                targets_alive += [team[i]]
        return targets_alive

    #~~~~~~~~~~~~Instance methods~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __str__(self):
        return self.name

    def choose_move(self):
        #move selection process for players
        print("{}'s move\n".format(self.name))
        self.display_moves(self.movesList)
        while True:
            print("\n> What would you like to do?")
            try:
                self_move = int(input(">"))                                 #self_move is user input (int) -1 for move index
                if self_move in range(1,len(self.movesList)+1):             #if valid move
                    move_name = self.movesList[self_move-1]                     #valid move will be called move_name (str)
                    mana_required = Ability.get_attr(move_name,"MP")            #check MP
                    if self.mp_check(mana_required):                            #if passes mana check, break out of while loop and move on to Unit.determine_targets()
                        break
                else:                                                                               #if move not valid
                    print("Please enter a number between 1-{}\n".format(len(self.movesList)))           #print request for valid input
            except ValueError:                                                                          #
                print("Please enter a number between 1-{}\n".format(len(self.movesList)))               #
        print()
        self.determine_targets(move_name)


    def comp_move(self):
        #action for computer turn                                                      #if computer is attacking, use pseudo-move
        for i in range(3):                                        #computer
            print(".",end="")                                     #...
            time.sleep(0.4)                                       #delay
        Unit.team_zero_list[0].hp -= 2                            #player loses HP
        print("{} punched you!".format(self.name))
        print("You took 2 damage\n")

    #use TARGET attributes to determine available target/s, calling select_target if needed, then calling Ability.targeted() or other Ability methods for damage calculations/ability mechanics)
    def determine_targets(self, move_name):
        target_type = Ability.get_attr(move_name,"TARGET_TYPE")
        target_is_enemy = Ability.get_attr(move_name,"TARGET_ENEMY")                

        if target_type == 0:                                                            #if TARGET_TYPE is self, this unit is the target
            print("an ability has been used on yourself") 

            #call Abilitiy.self_ability() which goes to smaller methods  <<TO BE CREATED

        if target_type in [1, 2, 3]:                                #if TARGET_TYPE is single, multiple, or team
            if target_is_enemy:                                         #if TARGET_ENEMY = True
                target_team = Unit.all_units_list[1 - self.team]            #then target team is the opposite team
            else:
                target_team = Unit.all_units_list[self.team]                #else the target team is own team

            if target_type == 1:                                        #if TARGET_TYPE = single target
                target_unit = self.select_target(move_name, target_team)     #call select_target() to get one target
                Ability.targeted(move_name, target_unit)                     #call for Ability class to take over

            if target_type == 2:                                        #if TARGET_TYPE = multiple targets
                print("TARGET_TYPE = 2 abilities have no effect yet")
                #needs multiple Unit.select_target() calls... need new attribute TARGET_NUM

            if target_type == 3:                                        #if TARGET_TYPE = team
                #print("target_type = 3")                                   #then call Ability.targeted() on each unit in target team
                for unit in target_team:
                    Ability.targeted(move_name, unit)                           #not sure if I should create a different Ability method for this, or just repeatedly use Ability.targeted() for whole team

        if target_type == 4:                                            #if TARGET_TYPE = all
            for team in Unit.all_units_list:                                #for all units
                for unit in team:                                           #
                    Ability.targeted(move_name, unit)                           #not sure if I should create a different Ability method for this, or just use Ability.targeted() for all units


        # checks all units, if unit is_dead(), call kill()
        for team in Unit.all_units_list:
            for unit in team:
                if unit.alive:
                    if unit.is_dead():                           
                        unit.kill()
                        print("{} is down!\n".format(unit.name))                            
                        time.sleep(0.5)
        time.sleep(1.0)

    #displays available targets and gets a unit from user input
    def select_target(self, move_name, target_team):
        targets_alive = Unit.currently_alive(target_team)
        for target in targets_alive:
            print("{}. {}".format(targets_alive.index(target)+1, target.name))
        print("Who would you like to use {} on?".format(move_name))
        while True:
            try:
                select_who = int(input("> "))                       #choose who to attack
                if select_who in range(1,len(targets_alive)+1):
                    break
                else:
                    print("Please enter a valid number")
            except ValueError:
                print("Please enter a valid number")
        return targets_alive[select_who-1]



    #Displays a unit's moveList
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

    #checks if hp of a unit is <= 0, if True, self.alive = False and return True
    def is_dead(self):
        if self.hp <= 0:
            self.alive = False
            return True
        return False