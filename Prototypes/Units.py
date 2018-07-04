"""Construction: x = Unit(name (str), team (int))

Class methods
    - Unit.create_units(player_name, num_allies, num_enemies): called by main() to create units at the start of the game
    - Unit.num_units(team, all_or_alive): returns the len() of one of four team lists (team zero/one, all/alive)
    - Unit.get_units(all_or_alive, team): returns one of four team lists (team zero/one, all/alive)
    - Unit.remove(unit): removes unit from its respective team list
    - Unit.display_health(): Prints HP of all currently alive Units in a formatted manner.
    - Unit.remove_all(): clears all unit lists of units, called at end of game in main()
    - Unit.downed(): checks all units for dead units and calls unit.kill() on them

Instance methods
    - x.choose_move(calling_ability=None): get a valid move from user inpot
    - x.comp_move(): used if team 2 is computer, unit will use pseudo-move
    - x.display_moves(movesList): display the unit's list of moves, their MP cost, and info about their moves
    - x.mp_check(mp_required): checks if enough mana, if enough then use that mana
    - x.is_dead(): returns True if Unit has <0HP and changes x.alive = False. Else returns False
    - x.display_buff_prompts(): displays prompts for buffs in buff_stacks_dict                              #needs work
    - x.modify_buff_stack_dict(add_or_remove, buff_name): simple dict entry adder/remover used by ability.check_stacks and special methods (for removing buff on expiration)
"""
import copy
import time
from collections import OrderedDict
import random
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
        self.alive = True       #use to determine if unit is allowed a move and is targetable
        self.buff_stacks_dict = {}        #when 

        self._hp = 100                    #cannot surpass max_hp (stops at max in setter method)
        self._mp = 20                    #cannot surpass max_mp (stops at max in setter method)

        self._max_hp = 100
        self._max_mp = 20
        self._ATK = 10
        self._DEF = 4            # dmg - defense = final dmg
        self._CRIT = 10          # /100%
        self._DODGE = 5          # /100%
        self._SPEED = 12         # max speed is 20

        self.movesList = ["Rest", "Punch", 'First aid']

        if self.team == 0:
            Unit.team_zero_list.append(self)
            Unit.team_zero_alive_list.append(self)
        elif self.team == 1:
            Unit.team_one_list.append(self)
            Unit.team_one_alive_list.append(self)

#~~~~~~~~~~~~Class methods~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #initialise all Units that will be present in this game loop
    @classmethod
    def create_units(cls, player_name, num_allies, num_enemies):
        if player_name == '':
            player_name = 'Justin'

        if player_name == 'Knight':
            player = Unit_Knight(player_name, 0)
        elif player_name == 'Thief':
            player = Unit_Thief(player_name, 0)
        else:
            player = Unit(player_name, 0)

        for i in range(num_allies):
            Unit("Ally " + str(i+1), 0)

        for i in range(num_enemies):
            Unit("Enemy " + str(i+1), 1)

    #returns len() of a team_list or team_alive_list using parameters team = 0, 1, all_alive = "all", "alive"
    @classmethod
    def num_units(cls, team, all_or_alive):
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

    #returns a list of currently alive units in chosen team, used in AbilityObject.select_target()
    @classmethod
    def get_units(cls, all_or_alive,  team):
        if team == 0:
            if all_or_alive == "all":
                return Unit.team_zero_list
            elif all_or_alive == "alive":
                return Unit.team_zero_alive_list
        if team == 1:
            if all_or_alive == "all":
                return Unit.team_one_list
            elif all_or_alive == "alive":
                return Unit.team_one_alive_list

    #removes unit from its team alive_list (use after checking is_dead())
    @classmethod
    def remove_unit(cls, unit):
        if unit.team == 0:
            Unit.team_zero_alive_list.remove(unit)
        if unit.team == 1:
            Unit.team_one_alive_list.remove(unit)

    #prints hp of all alive Units
    @classmethod
    def display_health(cls):   
        print("\n=====================================")
        for i in range(len(Unit.team_zero_list)):
            friendly = Unit.team_zero_list[i]
            print("{:9} HP:{:3}/{:3}     MP:{:3}/{:3}  ".format(friendly.name, friendly.hp, friendly.max_hp, friendly.mp, friendly.max_mp), end='')
            for buff in friendly.buff_stacks_dict.keys():
                print(" " + buff, end='')
                if friendly.buff_stacks_dict[buff] > 1:
                    print("x" + str(friendly.buff_stacks_dict[buff]), end='')
            print()
        print("-------------------------------------")
        for i in range(len(Unit.team_one_list)):
            enemy = Unit.team_one_list[i]
            print("{:9} HP:{:3}/{:3}     MP:{:3}/{:3}  ".format(enemy.name, enemy.hp, enemy.max_hp, enemy.mp, enemy.max_mp), end='')
            for buff in enemy.buff_stacks_dict.keys():
                print(" " + buff, end='')
                if enemy.buff_stacks_dict[buff] > 1:
                    print("x" + str(enemy.buff_stacks_dict[buff]), end='')
            print()
        print("=====================================\n")
        time.sleep(1.0)

    @classmethod
    def remove_all(cls):
        for l in [Unit.team_zero_list,Unit.team_one_list]:
            l.clear()
            del l[:]

    # checks all units, if unit is_dead(), call remove_unit() ##MAYBE CHANGE
    @classmethod
    def downed(cls):
        for team in Unit.all_units_list:
            for unit in team:
                if unit.is_dead():
                    if unit in Unit.team_one_alive_list or unit in Unit.team_zero_alive_list:                        
                        Unit.remove_unit(unit)
                        print("{} is down!\n".format(unit.name))                            
                        time.sleep(0.4)

#~~~~~~~~~~~~Instance methods~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __str__(self):
        return self.name

    #acquire valid move from user, then create an Ability object and put in Ability.Ability_queue, then call object.determine_targets() through that object
    def choose_move(self, calling_ability=None):
        move_id_counter = 0
        if calling_ability != None:
            Ability.Ability_queue.remove(calling_ability)
        Ability.check_Ability_queue(casting_unit = self)
        Unit.display_health()                   #display HP of all alive Units
        Unit.downed()
        print("  ------ {}'s move ------".format(self.name))
        time.sleep(0.8)
        self.display_moves(self.movesList)

        self.display_buff_prompts()

        while True:
            print("> What would you like to do?")
            try:
                self_move = int(input(">"))                                 #self_move is user input (int) -1 for move index
                if self_move in range(1,len(self.movesList)+1):             #if valid move
                    move_name = self.movesList[self_move-1]                     #valid move will be called move_name (str)

                    mana_required = Ability.get_attr(move_name, "MP_COST")              #check MP
                    if self.mp_check(mana_required):                                    #if passes mana check, break out of while loop
                        break
                else:                                                                               #if move not valid
                    print("Please enter a number between 1-{}\n".format(len(self.movesList)))           #print request for valid input
            except ValueError:                                                                          #
                print("Please enter a number between 1-{}\n".format(len(self.movesList)))               #
        current_Ability = Ability(move_name, Ability.ability_ID_counter)    #create Ability object
        Ability.Ability_queue += [current_Ability]                          #add it to the queue
        print()
        target_list = current_Ability.determine_targets(self)               #call ability's determine_targets
        if target_list == None:                       
            return
        Unit.downed()

    #pseudo-action for computer turn
    def comp_move(self):            ######## get to changing this
        Ability.check_Ability_queue(casting_unit = self)
        Unit.display_health()                   #display HP of all alive Units
        print("  ------ {}'s move ------\n".format(self.name))
        for i in range(3):                                        #computer
            print(".",end="")                                     #...
            time.sleep(0.4)                                       #
        print("{} throws a punch at you!".format(self.name))
        time.sleep(0.6)
        if random.random() < Unit.team_zero_list[0].DODGE/100:
            print("You dodged the attack!")
        else:
            damage = randint(8,12) - Unit.team_zero_list[0].DEF
            Unit.team_zero_list[0].hp -= damage                            #player loses HP
            print("You took {} damage".format(damage))
        time.sleep(1.0)
        Unit.downed()

    #Displays a unit's moveList
    def display_moves(self, movesList):
        for move in self.movesList:                                                 #print a list of available moves from dicts
            print("{}. {:15}".format(movesList.index(move) + 1, move), end='')      #
            if Ability.get_attr(move,"MP_COST") != 0:                                    #
                print("MP cost: {}  ".format(Ability.get_attr(move,"MP_COST")), end='')            #
            else:                                                                   #
                print("No cost     ", end='')                                                    #
            print(Ability.get_attr(move,"INFO"))
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

    def display_buff_prompts(self):                ###############################################################
        print()
        if "+ATK" in self.buff_stacks_dict:
            print("{}'s sword gleams".format(self.name))


    def modify_buff_stack_dict(self, add_or_remove, buff_name):
        if add_or_remove == "add":
            if buff_name in self.buff_stacks_dict:
                self.buff_stacks_dict[buff_name] += 1
            else:
                self.buff_stacks_dict[buff_name] = 1
        elif add_or_remove == "remove":
            if buff_name in self.buff_stacks_dict:
                if self.buff_stacks_dict[buff_name] > 2:
                    self.buff_stacks_dict[buff_name] -= 1
                else:
                    del self.buff_stacks_dict[buff_name]
            else:
                print("no {} to delete in {}'s buff_stack_dict".format(buff_name, self.name))               #for debugging

#===================setters and getters for Unit object stats======================
    @property
    def hp(self):
        return self._hp

    @hp.setter
    def hp(self, val):
        if val < 0:
            self._hp = 0
        elif val > self.max_hp:
            self._hp = self.max_hp
        else:
            self._hp = val
    #--------------------------
    @property
    def mp(self):
        return self._mp

    @mp.setter
    def mp(self, val):
        if val < 0:
            self._mp = 0
        elif val > self.max_mp:
            self._mp = self.max_mp
        else:
            self._mp = val
    #--------------------------
    @property
    def max_hp(self):
        return self._max_hp

    @max_hp.setter
    def max_hp(self, val):
        if val < 1:
            self._max_hp = 1
        elif val > 1000:
            self._max_hp = 1000
        else:
            self._max_hp = val
        #if val < self.hp:                       #add this? if new max_hp is lower than current hp, lower current hp to new max_hp
           # self.hp = val                              #or can just lower both if ability needs to
    #--------------------------
    @property
    def max_mp(self):
        return self._max_mp

    @max_mp.setter
    def max_mp(self, val):
        if val < 0:
            self._max_mp = 0
        elif val > 1000:
            self._max_mp = 1000
        else:
            self._max_mp = val
        #if val < self.mp:                       #add this? if new max_mp is lower than current mp, lower current mp to new max_mp
           # self.mp = val                              #or can just lower both if ability needs to
    #--------------------------
    @property
    def ATK(self):
        return self._ATK

    @ATK.setter
    def ATK(self, val):
        if val < 0:
            self._ATK = 0
        elif val > 100:
            self._ATK = 100
        else:
            self._ATK = val
    #--------------------------
    @property
    def DEF(self):
        return self._DEF

    @DEF.setter
    def DEF(self, val):
        if val < 0:
            self._DEF = 0
        elif val > 100:
            self._DEF = 100
        else:
            self._DEF = val
    #--------------------------
    @property
    def CRIT(self):
        return self._CRIT

    @CRIT.setter
    def CRIT(self, val):
        if val < 0:
            self._CRIT = 0
        elif val > 100:
            self._CRIT = 100
        else:
            self._CRIT = val
    #--------------------------
    @property
    def DODGE(self):
        return self._DODGE

    @DODGE.setter
    def DODGE(self, val):
        if val < 0:
            self._DODGE = 0
        elif val > 100:
            self._DODGE = 100
        else:
            self._DODGE = val
    #--------------------------
    @property
    def SPEED(self):
        return self._SPEED

    @SPEED.setter
    def SPEED(self, val):
        if val < 0:
            self._SPEED = 0
        elif val > 20:
            self._SPEED = 20
        else:
            self._SPEED = val
    #--------------------------
    @property
    def alive(self):
        return self._alive

    @alive.setter
    def alive(self, val):
        self._alive = val
    #--------------------------

##################### Unit sub-classes #########################################

class Unit_Knight(Unit):

    def __init__(self, name, team):
        super().__init__(name, team)

        self.max_hp = 100
        self.max_mp = 15
        self.hp = 100                    #cannot surpass max_hp (stops at max in setter method)
        self.mp = 15                    #cannot surpass max_mp (stops at max in setter method)

        self.ATK = 10
        self.DEF = 6            # dmg - defense = final dmg
        self.CRIT = 10          # /100%
        self.DODGE = 0          # /100%
        self.SPEED = 6         # max speed is 20

        self.movesList = ["Rest", "Sword slash", 'Raise shield', 'Sharpen sword']

class Unit_Thief(Unit):

    def __init__(self, name, team):
        super().__init__(name, team)

        self.max_hp = 100
        self.max_mp = 25
        self.hp = 100                    #cannot surpass max_hp (stops at max in setter method)
        self.mp = 25                    #cannot surpass max_mp (stops at max in setter method)

        self.ATK = 9
        self.DEF = 0            # dmg - defense = final dmg
        self.CRIT = 25          # /100%
        self.DODGE = 15          # /100%
        self.SPEED = 16         # max speed is 20

        self.movesList = ["Rest", "Dagger stab", 'Feint', 'Poison']


from Abilities import Ability