"""Construction: x = Unit(name (str), team (int))

Class methods
    - Unit.kill(unit): removes unit from its respective team list
    - Unit.num_units(): returns the len() of one of four team lists (zero/one, all/alive)
    - Unit.display_health(): Prints HP of all currently alive Units in a formatted manner.
    - Unit.currently_alive(team): returns len() of the team list or team alive list

Instance methods
    - choose_move(): get a valid move from user inpot

    - x.display_moves(movesList): display the unit's list of moves
    - x.mp_check(mp_required): checks if enough mana, if enough then use that mana
    - x.is_dead(): returns True if Unit has 0 or less HP and changes x.alive = False. Else returns False
"""
import copy
import time
from collections import OrderedDict
from random import randint


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


        self.max_hp = 100
        self.max_mp = 50
        self.hp = 100                    #cannot surpass max_hp (stops at max in setter method)
        self.mp = 50                    #cannot surpass max_mp (stops at max in setter method)


        self.ATK = 8
        self.DEF = 2            # dmg - defense = final dmg
        self.CRIT = 10       # 100% = 100
        self.SPEED = 12             # max speed is 20

        self.alive = True           #use to determine if unit is allowed a move and is targetable

        self.buffs = []             ##############TO ADD BUFFS/DEBUFFS
        
        self.movesList = ["Punch", "Kick", "Big kick", "Magic bolt", "Heal self", "Heal", "Heal team", 'Healing punch', 'Increase ATK', 'Nuke']

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
            print("{:9} HP:{:3}/{:3}        MP:{:3}/{:3}  ".format(friendly.name, friendly.hp, friendly.max_hp, friendly.mp, friendly.max_mp), end='')
            for buff in friendly.buffs:
                print(" " + buff, end='')
            print()
        print("----------------------------------------")
        for i in range(len(Unit.team_one_list)):
            enemy = Unit.team_one_list[i]
            print("{:9} HP:{:3}/{:3}        MP:{:3}/{:3}  ".format(enemy.name, enemy.hp, enemy.max_hp, enemy.mp, enemy.max_mp), end='')
            for buff in enemy.buffs:
                print(" " + buff, end='')
            print()
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

    #acquire valid move from user, then create an Ability object and put in Ability.Ability_queue, then call object.determine_targets() through that object
    def choose_move(self):
        move_id_counter = 0
        print("{}'s move\n".format(self.name))
        self.display_moves(self.movesList)

        self.display_buffs()
        while True:
            print("> What would you like to do?")
            try:
                self_move = int(input(">"))                                 #self_move is user input (int) -1 for move index
                if self_move in range(1,len(self.movesList)+1):             #if valid move
                    move_name = self.movesList[self_move-1]                     #valid move will be called move_name (str)
            
                    current_Ability = Ability(move_name, Ability.ability_ID_counter)
                    Ability.Ability_queue += [current_Ability]       #create Ability object with move_name and ID which can be referenced (unique for every Ability object)

                    mana_required = current_Ability.AttributeValueDict["MP"]            #check MP
                    if self.mp_check(mana_required):                            #if passes mana check, break out of while loop and move on to Unit.determine_targets()
                        break
                else:                                                                               #if move not valid
                    print("Please enter a number between 1-{}\n".format(len(self.movesList)))           #print request for valid input
            except ValueError:                                                                          #
                print("Please enter a number between 1-{}\n".format(len(self.movesList)))               #
        print()
        current_Ability.determine_targets(self)

        # checks all units, if unit is_dead(), call kill()
        for team in Unit.all_units_list:
            for unit in team:
                if unit.alive:
                    if unit.is_dead():                           
                        unit.kill()
                        print("{} is down!\n".format(unit.name))                            
                        time.sleep(0.5)

    def comp_move(self):
        #action for computer turn                                                      #if computer is attacking, use pseudo-move
        for i in range(3):                                        #computer
            print(".",end="")                                     #...
            time.sleep(0.4)                                       #delay
        damage = randint(4,10)
        Unit.team_zero_list[0].hp -= damage                            #player loses HP
        print("{} punched you!".format(self.name))
        print("You took {} damage\n".format(damage))


        time.sleep(1.0)

    #Displays a unit's moveList
    def display_moves(self, movesList):
        for move in self.movesList:                                                 #print a list of available moves from dicts
            print("{}. {:15}".format(movesList.index(move) + 1, move), end='')      #
            if Ability.get_attr(move,"MP") != 0:                                    #
                print("MP cost: {}".format(Ability.get_attr(move,"MP")))            #
            else:                                                                   #
                print("No cost")                                                    #
            time.sleep(0.08)

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

    def display_buffs(self):                ###############################################################
        print()
        if "+ATK" in self.buffs:
            print("Your sword gleams")


    #===================setters and getters for Unit object stats======================

    @property
    def hp(self):
        return self.__hp

    @hp.setter
    def hp(self, val):
        if val < 0:
            self.__hp = 0
        elif val > self.max_hp:
            self.__hp = self.max_hp
        else:
            self.__hp = val
    #--------------------------
    @property
    def mp(self):
        return self.__mp

    @mp.setter
    def mp(self, val):
        if val < 0:
            self.mp = 0
        elif val > self.max_mp:
            self.__mp = self.max_mp
        else:
            self.__mp = val
    #--------------------------
    @property
    def ATK(self):
        return self.__ATK

    @ATK.setter
    def ATK(self, val):
        self.__ATK = val
    #--------------------------
    @property
    def DEF(self):
        return self.__DEF

    @DEF.setter
    def DEF(self, val):
        self.__DEF = val
    #--------------------------
    @property
    def CRIT(self):
        return self.__CRIT

    @CRIT.setter
    def CRIT(self, val):
        self.__CRIT = val
    #--------------------------
    @property
    def SPEED(self):
        return self.__SPEED

    @SPEED.setter
    def SPEED(self, val):
        self.__SPEED = val
    #--------------------------
    @property
    def alive(self):
        return self.__alive

    @alive.setter
    def alive(self, val):
        self.__alive = val
    #--------------------------


from Abilities import Ability