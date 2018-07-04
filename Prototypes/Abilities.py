"""
All ability effects (except initial mana cost) will be handled here.
Entering point into this class is through Unit.choose_move(), where an Abilityobject is created, and then its determine_targets() method is called

Class methods:

    - get_attr(skill_name, ATTRIBUTE_NAME): gets the index and returns the value of a skill's attribute
    - check_Ability_queue(current_ability): removes expired abilities and procs active ones in the ability queue

    ----unit stat-modifying class methods------------
    - damage_target(damage_amount, target): damage (no calculations) with generic message outputs and minimum damage of 0
    - heal_target(target, hp_gain, mp_gain): healing (no calculations) with generic message outputs with cap at target's max hp/mp


Instance methods:

    - y.build_AttributeValueDict(): populates this ability object's AttributeValueDict with its stats as key:value pairs
    - y.determine_targets(caster): determines this ability's available targets to fill target_list (using select_target(target_team) if needed)
    - y.initial_cast(target_list, caster): use cast_on_target(target, caster) for targets in target_list (also check_stacks(target) if ability is a buff), 
                                            then check_Ability_queue(self) if there are any other abilites in queue
    - y.check_stacks(target):
    - y.select_target(target_team, caster):
    - y.cast_on_target(target, caster): Actions the ability's effects on the target 

    Instance (calculation) methods:
        - y.calculate_dmg(target, caster): calculates damage range from DMG_BASE and DMG_ROLL, gets random damage from that range and calls damage_target()
        - y.calculate_heals(target, caster): 
        - y.calculate_def(raw_damage, target)
        - y.ability_dodged(target)

All abilities should be declared in Ability_dict and should follow this format:
    ( "NAME", [ ["TARGET_TYPE", "TARGET_ENEMY", "TARGET_NUM"], ["SPECIAL", "LASTS"], ["MP_COST"], ["DMG_TYPE", "DMG_IS_PERCENT", "DMG_BASE", "DMG_ROLL"], ["IS_HEAL", "HP_GAIN", "MP_GAIN"] ] )     #SUBJECT TO CHANGE ACCORDING TO THE NEEDS OF CREATED ABILITIES

    TARGET [0]:
        TARGET_TYPE [0]     - (int) 0 = self,       1 = single,     2 = multiple,   3 = team (units in the team will no be differentiated),   4 =  all (units will not be differentiated)
        TARGET_ENEMY [1]    - (boolean) True if targets enemies, False if it targets allies (use x if TARGET_TYPE = self, all )
        TARGET_NUM [2]      - (int) Number of targets to target if TARGET_TYPE = multiple (use x if otherwise)
    OTHER [1]:      
        SPECIAL [0]     - (int) 0 if only initial methods should be used, 1 if only a special method should be used, 2 if both initial and special methods should be used
        LASTS [1]       - (int) Number of (caster) moves this ability will last for (0 for immediate expiration)
    MP_COST [2]
    DAMAGE [3]:           
        DMG_TYPE [0]        - (boolean) "NORMAL" or "MAGIC" if move does initial damage, False otherwise and ignore rest of section
        DMG_IS_PERCENT [2]  - (boolean)
        DMG_BASE [1]        - (int) base damage of this ability. This is added onto the ATK of the unit
        DMG_ROLL [2]        - (int) amount by which base damage may deviate each way, i.e. DMG_BASE ± DMG ROLL = Damage range (0 for no deviation) 
    REGEN [4]:           
        IS_HEAL [0]         - (bool) Uses any of this section means True, else False and ignore rest of section
        HP_GAIN [1]         - (int) HP healed (0 for none)
        MP_GAIN [2]         - (int) MP gained (0 for none)
    BUFF [5]:
        IS_BUFF [0]         - (bool) True if ability should be considered a buff, i.e. will be changing a unit's stats, False otherwise and ignore rest of section
        BUFF_TRIGGER_ON [1] - (int) buff loses duration: 0 = per turn, 1 =  when attacked, 2=  when attacking 
        BUFF_ENDS [ 2]      - (int) buff ends before or after caster move,  0 = before, 1 = after
        BUFF_STACKS [3]     - (int) How many instances of this buff can exist on a target, (1 for no stacking, i.e. only one instance) 
        BUFF_STATUS [4]     - (str) the string that is displayed to represent this buff
        


    If an abiltiy also has a buff/debuff effect which affects units' stats (TO ADD: or other mechanics that are popular), they should be put into specialDict:

    ( "NAME",  [ {BUFFS} ] )

    BUFFS [0]   - (dict of (stat(str):value(int))) A dict of all unit stat-modifying, with key being the stat, and value being the amount by which it changes
"""

from collections import OrderedDict
import time
import random
from random import randint
import math

class Ability():
    #ATTRIBUTE_NAME_LIST and abilityDict store data about abilities and how they work
    ATTRIBUTE_NAME_LIST = [["TARGET_TYPE", "TARGET_ENEMY", "TARGET_NUM"], ["SPECIAL", "LASTS"], ["MP_COST"], ["DMG_TYPE", "DMG_IS_PERCENT", "DMG_BASE", "DMG_ROLL"], ["IS_HEAL", "HP_GAIN", "MP_GAIN"], ["IS_BUFF", "BUFF_TRIGGER_ON", "BUFF_ENDS",  "BUFF_STACKS", "BUFF_STATUS"], ["INFO"]] 
#----------------make abilities here--------------------------------------------------------------------------------------------------------------------------
    x = None
    abilityDict = OrderedDict((                                                                        
    ('Punch',           [[1, True,  x], [False, 0], [1],  ["NORMAL", False, 0, 2],    [False],      [False],                    ["Deals ATK ± 2 damage to a target"]     ]),                             #To use an ability, it will have to be added to a unit's moveList
    ('Dagger stab',     [[1, True,  x], [False, 0], [1],  ["NORMAL", False, 3, 1],    [False],      [False],                    ["Deals ATK + 3 ± 1 damage to a target"]     ]),                              #abilities with unique mechanics not covered by these need their own special function

    ('Magic bolt',      [[1, True,  x], [False, 0], [6],  ["NORMAL", False, 10, 1],   [False],      [False],                    ["add MAGIC? to ignore DEF"]     ]),       #
    ('Leech',           [[1, True,  x], [True, 0],  [15], [False],                    [False],      [False],                    ["Steal HP from an enemy"]      ]),        #

    ('Rest',            [[0, x,     x], [False, 0], [0],  [False],                    [True, 6, 6], [False],                    ["Recovers 6HP and 6MP"]  ]),       #
    ('First aid',       [[0, x,     x], [False, 0], [9], [False],                     [True, 20, 0], [False],                   ["Recovers 20HP"]  ]),      #
    ('Heal',            [[1, False, x], [False, 0], [10], [False],                    [True, 15, 0], [False],                   ["Target ally recovers 15HP"]  ]),        #
    ('Heal team',       [[3, False, x], [False, 0], [16], [False],                    [True, 30, 0], [False],                   ["All units in team recover 30HP"]  ]),        #

    ('Nuke',            [[4, x,     x], [False, 0], [30], ["NORMAL", False, 99, 0],   [False],      [False],                    ["All units are dealt 99 damage (+ ATK)"]      ]),         #

    ('Big kick',        [[3, True,  x], [False, 0], [6],  ["NORMAL", False, 0, 6],    [False],      [False],                    ["All enemy units are dealt ATK ± 6 damage"]      ]),       #

    ('Sharpen sword',    [[0, x,     x], [True,  2], [6],  [False],                   [False],     [True, 0, 1, 1, "+ATK"],     ["Increase own ATK by 10 for the next 2 turns"]     ]),       #

    ('Poison',          [[1, True,  x], [True,  6], [5],  [False],                    [False],      [True, 0, 0, 3, "PSN"],     ["Poisons for 5 turns, with each turn being more damaging. Stacks multiply the damage given. Stacks 3 times."]  ]),      #

    ('Sword slash',     [[1, True,  x], [False, 0], [1],  ["NORMAL", False, 5, 4],    [False],      [False],                    ["Deals ATK + 5 ± 4 damage to a target"]     ]),
    ('Raise shield',    [[0, x,     x], [True,  1], [2],  [False],                    [False],      [True, 0, 0, 1, "+DEF"],    ["Increase own DEF by 15 until next turn"]     ]),
    ('Feint',           [[0, x,     x], [True,  1], [3],  [False],                    [False],      [True, 0, 0, 1, "+DODGE"],  ["Increase own DODGE by 40\%\ until next turn"]     ])
    #('Triple Kick',     [[2, True, 3],      [True, 8, 2],        6, 0, [True]]) #should attack same target three times

    ))
#------------------------------------------------------------------------------------------------------------------------------------------
    #BUFF_ATTRIBUTE_LIST = [["TYPE"], ["TARGET_TYPE", "TARGET_ENEMY", "TARGET_NUM"], ["BUFFS DICT"]

    ability_ID_counter = 0
    Ability_queue = []          #most abilities are added, used then immediately removed, those with LASTS > 1 stay longer
    
    def __init__(self, ability_name, ability_ID):       

        self.ability_ID = ability_ID    #is this needed? The only reference to an ability after its turn is over is through the Ability_queue, is that enough?
        Ability.ability_ID_counter += 1       #for ability_ID during creating... is this needed?

        self.ABILITY_NAME = ability_name                                                        #used to match to special method if needed
        self.target_list = None                                                                      #the target of this ability
        self.caster = None                                                                      #the one using this ability, used in helping determine if it's a players turn
        self.AttributeValueDict = self.build_AttributeValueDict()
        self.turns_left = self.AttributeValueDict["LASTS"]
        
        
#========================================Class methods===========================================================================================
    #Uses ATTRIBUTE_NAME_LIST and ability_dict to get an index and then value of (skill_name, ATTRIBUTE_NAME)
    #this is used when an Ability object is not refered to directly, e.g. getting MP for Unit.display_moves()
    @classmethod
    def get_attr(cls, skill_name, ATTRIBUTE_NAME):
        attribute_value = None
        ability_attributes = Ability.abilityDict[skill_name]            #a list containing attributes' values of a particular skill
        if ATTRIBUTE_NAME in Ability.ATTRIBUTE_NAME_LIST:                        #if ATTRIBUTE_NAME is found by first-level search,
            index = Ability.ATTRIBUTE_NAME_LIST.index(ATTRIBUTE_NAME)                #get the index of ATTRIBUTE_NAME
            attribute_value = ability_attributes[index]                         #and use index to get value from abilityDict
        else:                                                               #ATTRIBUTE_NAME might be found in a secondary-level LIST 
            for attributes in Ability.ATTRIBUTE_NAME_LIST:                               #for each LIST in ATTRIBUTE_NAME_LIST, e.g. ["TARGET_TYPE", "TARGET_TEAM"]
                if isinstance(attributes, list):                                    #
                    if ATTRIBUTE_NAME in attributes:                                    #if ATTRIBUTE_NAME is found in this list
                        try:                                                                #try 
                            index1 = Ability.ATTRIBUTE_NAME_LIST.index(attributes)                   #to get the two-level index of the ATTRIBUTE_NAME
                            index2 = Ability.ATTRIBUTE_NAME_LIST[index1].index(ATTRIBUTE_NAME)       #
                            attribute_value = ability_attributes[index1][index2]                #and use index to get value from abilityDict
                        except IndexError:                                                  #if the value does not exist in that index,
                            print("The value for this ability attribute does not exist!")        #print an error message (for debugging purposes)
                            return None                                                         #continue excecution, returning attribute value of None
        if attribute_value == None:                                             #if both loops ended
            raise ValueError('Attribute does not exist!')                           #and ATTRIBUTE NAME is not found, print error message (for debugging purposes)
        return attribute_value

    #checks queue for expired abilities and removes them from queue, procs any remaining abilities (excluding current one) and -1 their turns_left, then 
    @classmethod
    def check_Ability_queue(cls, current_ability = None, casting_unit = None):
        if current_ability != None:
            if current_ability.turns_left == 0:             #if current ability was immediate, remove it from queue 
                del Ability.Ability_queue[-1]
                copy_queue = Ability.Ability_queue
            else:                                           #else, make a new list without the current ability (so other abilities can proc)
                copy_queue = Ability.Ability_queue[:-1]     
            for ability in copy_queue:                      #for each ability in queue (less current one)
                if ability.turns_left == 0:                     #if expired, remove it from queue (i.e. turns_left = 0)
                    Ability.Ability_queue.remove(ability)
                else:                                           #else, 
                    if ability.caster == current_ability.caster:    #if the caster is the same person (i.e. ability belongs to caster)
                        if ability.AttributeValueDict["BUFF_ENDS"] == 1:
                            ability.turns_left -= 1                         # subtract a turn from turns_left and proc the ability for each of its targets
                            for target in ability.target_list:
                                ability.cast_on_target(target, ability.caster)# and proc it
        elif casting_unit != None:
            copy_queue = Ability.Ability_queue
            for ability in copy_queue:                      #for each ability in queue (less current one)
                if ability.turns_left == 0:                     #if expired, remove it from queue (i.e. turns_left = 0)
                    Ability.Ability_queue.remove(ability)
                else:                                           #else, 
                    if ability.caster == casting_unit:    #if the caster is the same person (i.e. ability belongs to caster)
                        if ability.AttributeValueDict["BUFF_ENDS"] == 0:
                            ability.turns_left -= 1                         # subtract a turn from turns_left and proc the ability for each of its targets
                            for target in ability.target_list:
                                ability.cast_on_target(target, ability.caster)# and proc it

    #generic damage (no calculations) with message outputs and minimum damage of 0
    @classmethod
    def damage_target(cls, final_damage, target):
        if final_damage > 0:                                #if there is damage,
            target.hp -= final_damage                             #target loses HP
            print("{} took {} damage!".format(target.name, final_damage))       
        else:
            print("{} took no damage... His defence is too high!".format(target.name))

    #abilities that are 'heals' should use this
    @classmethod
    def heal_target(cls,target, hp_gain, mp_gain):

        if hp_gain > 0:
            healed_to_max = (hp_gain + target.hp) >= target.max_hp
            if healed_to_max:
                print("{} was fully healed!".format(target))
            else:
                print("{} was healed for {} HP!".format(target, hp_gain))
            target.hp += hp_gain
        if mp_gain > 0:
            mp_to_max = (mp_gain + target.mp) >= target.max_mp
            if mp_to_max:
                print("{}'s mana was fully restored!".format(target))
            else:
                print("{} recovered {} MP!".format(target, mp_gain))
            target.mp += mp_gain
#=================================Instance methods=========================================================================================
    #populates this ability object's AttributeValueDict with its stats as key:value pairs
    def build_AttributeValueDict(self):
        built_dict = {}
        ability_attribute_list = Ability.abilityDict[self.ABILITY_NAME]                         #list of all attribute values
        for section in Ability.ATTRIBUTE_NAME_LIST:                                             #for each section in ATTRIBUTE_NAME_LIST
            section_index = Ability.ATTRIBUTE_NAME_LIST.index(section)                              #store the section's index
            if ability_attribute_list[section_index][0] == False and section_index not in [0, 1]:   #if first attribute in section is False, ignore the rest of the section
                built_dict[section[0]] = ability_attribute_list[section_index][0]          #(unless that section is OTHER) and add that first attribute and value
            else:                                                                                   
                for attribute in section:
                    attribute_index = section.index(attribute)
                    built_dict[attribute] = ability_attribute_list[section_index][attribute_index]
        return built_dict

    #determines this ability's available targets and gets targets (using select_target() if needed) to get a target_list
    def determine_targets(self, caster):
        target_type = self.AttributeValueDict["TARGET_TYPE"]
        target_is_enemy = self.AttributeValueDict["TARGET_ENEMY"]      

        if target_type == 0:                                            #if TARGET_TYPE is self,        
            target_list = [caster]                                          #target_list is just the caster      

        if target_type in [1, 2, 3]:                                    #if TARGET_TYPE is single, multiple, or team
            if target_is_enemy:                                             #if TARGET_ENEMY = True
                target_team = Unit.all_units_list[1 - caster.team]              #then target team is the opposite team
            else:
                target_team = Unit.all_units_list[caster.team]                  #else the target team is own team

            if target_type == 1:                                                #if TARGET_TYPE = single target
                if len(target_team) == 1:                                           #and there is only one unit in target team,
                    target_list = [target_team[0]]                                      #target_list is that unit
                else:                                                               #else:
                    target_list = [self.select_target(target_team, caster)]             #call select_target() to get one target for target_list
                if target_list == [None]:                                           #if cast_on_target returned with None,
                    return None                                                         #return to choose_move#

            if target_type == 2:                                                #if TARGET_TYPE = multiple targets
                #
                #needs a new select_targetS() method, then target_list is those selected
                print("TARGET_TYPE = 2 still working on it")       

            if target_type == 3:                                                #if TARGET_TYPE = team
                target_list = target_team                                           #target_list is target_team

        if target_type == 4:                                                    #if TARGET_TYPE = all
            target_list = []                                                        #target_list is all units
            for team in Unit.all_units_list:                                
                target_list += team
        
        self.initial_cast(target_list, caster)
        return target_list

    #sets the target_list and caster for this ability, displays 'used' output, and for every target in target_list, check buff_stacks if is a buff and cast_on_target(), then check_Ability_queue() if needed
    def initial_cast(self, target_list, caster):
        self.target_list = target_list                            #store target_list and caster in ability instance
        self.caster = caster
        print("You used {}".format(self.ABILITY_NAME))
        time.sleep(0.8)
        for target in target_list:                      #for every target unit
            if self.AttributeValueDict["IS_BUFF"]:          #if this ability is a buff, then check buff stacks on target
                self.check_stacks(target)
            self.cast_on_target(target, caster)                   #use cast_on_target()
        if len(Ability.Ability_queue) >= 2:             #if there are two or more abilities in queue,
            Ability.check_Ability_queue(current_ability = self)                 #then call check_Ability_queue to check other abilities still in queue

    #if the ability is not stackable or past BUFF_STACKS limit, remove the first instance of the same ability, else, add a stack to unit.buff_stack_dict
    def check_stacks(self, target):

        times_stackable = self.AttributeValueDict["BUFF_STACKS"]
        buff_status = self.AttributeValueDict["BUFF_STATUS"]
        target.modify_buff_stack_dict("add", buff_status)                                       #add a stack initially
        if target.buff_stacks_dict[buff_status] > times_stackable:                              #if stacks is over limit,
            print("Already reached maximum stacks!")                                                          #if this ability is NOT stackable,
            for ability in Ability.Ability_queue:                                               #search ability queue
                check_targets = ability.target_list                                             
                if ability.ABILITY_NAME == self.ABILITY_NAME and target in check_targets:           #if ability has same name and target,
                    Ability.Ability_queue.remove(ability)                                               #remove that ability then break loop
                    target.modify_buff_stack_dict("remove", buff_status)
                    break

    #displays available targets (in targeted team and alive) and returns a unit from user input
    def select_target(self, target_team, caster):
        targets_alive = Unit.get_units("alive", target_team[0].team)
        for target in targets_alive:
            print("{}. {}".format(targets_alive.index(target)+1, target.name))
        print("Who would you like to use {} on?".format(self.ABILITY_NAME))
        while True:
            try:
                select_who = input("> ")                     #choose who to attack
                if select_who == "b":                               #input b to choose another move (by returning with None)#
                    caster.choose_move(self)
                    return None
                if int(select_who) in range(1,len(targets_alive)+1):             #if input number in range
                    target = targets_alive[int(select_who)-1]
                    if self.AttributeValueDict["IS_HEAL"]:
                        if self.AttributeValueDict["HP_GAIN"] != 0 and target.hp >= target.max_hp:                                        
                            print("Already at full health!")
                        elif self.AttributeValueDict["MP_GAIN"] != 0 and target.mp >= target.max_mp:
                            print("Already at full mana!")
                    else:
                        break
                else:
                    print("Please enter a valid number or enter 'b' to go back.")
            except ValueError:
                print("Please enter a number or enter 'b' to go back.")
        print()
        return target

    #Do basic mechanics using ABILITY_ATTRIBUTES to target
    def cast_on_target(self, target, caster):          

        if self.AttributeValueDict["SPECIAL"]:              #put it first in order because 
            self.special_sorter(target, caster)

        if self.AttributeValueDict["DMG_TYPE"] in ["NORMAL", "MAGIC"]:
            if self.ability_dodged(target):
                print("{} dodged the attack!".format(target.name))
            else:
                self.calculate_dmg(target, caster)
                raw_damage = self.calculate_dmg(target, caster)
                final_damage = self.calculate_def(raw_damage, target)
                Ability.damage_target(final_damage, target)

            
        if self.AttributeValueDict["IS_HEAL"]:
            hp_gain, mp_gain = self.calculate_heals(target)
            Ability.heal_target(target, hp_gain, mp_gain)

    def calculate_dmg(self, target, caster):        #uses DMG_BASE, DMG_ROLL, caster.ATK to calculate and return raw_damage
        minDMG, maxDMG = (self.AttributeValueDict["DMG_BASE"] - self.AttributeValueDict["DMG_ROLL"],
                            self.AttributeValueDict["DMG_BASE"] + self.AttributeValueDict["DMG_ROLL"])
        raw_damage = caster.ATK + randint(minDMG,maxDMG)
        return raw_damage

    def calculate_def(self, raw_damage, target):    #uses a damage value and target.DEF to calculate and return final_damage
        final_damage = raw_damage - target.DEF
        return final_damage

    def calculate_heals(self, target):                  #
        hp_gain = self.AttributeValueDict["HP_GAIN"]
        mp_gain = self.AttributeValueDict["MP_GAIN"]
        return hp_gain, mp_gain

    def ability_dodged(self, target):
        if random.random() < target.DODGE/100:
            return True
        return False

#----------------------Special instance methods----------------------------------------------------
    #Only abilities with LASTS greater than 1 or is SPECIAL access this method and section
    #This method maps the ability to its method containing unique mechanics .... use a dictionary
    def special_sorter(self, target, caster):
        if self.ABILITY_NAME == "Sharpen sword":
            self.IncreaseATK(target)
        elif self.ABILITY_NAME == "Leech":
            self.Leech(target, caster)
        elif self.ABILITY_NAME == "Poison":
            self.Poison(target)
        elif self.ABILITY_NAME == "Raise shield":
            self.RaiseShield(target)
        elif self.ABILITY_NAME == "Feint":
            self.Feint(target)

#This section contains all methods used by abilities that have unique mechanics not covered by basic ones

    #In addition to no basic mechanics, increases target (self) ATK by 10 for 2 turns (excluding this turn)         #this ability's value is hardcoded, maybe make a BUFF_VALUE attribute so it can change
    def IncreaseATK(self, target):                                                                                  # also in future it could mean value could vary with unit stats e.g. MAGIC
        if self.turns_left == self.AttributeValueDict["LASTS"]:      #if just cast, increase ATK by 10
            target.ATK += 10
            print("Your ATK has increased by 10!")
        elif self.turns_left > 0:                                       #do nothing if in 2nd turn
            pass
        else:                                                           #reverse effects after last turn
            if self.AttributeValueDict["IS_BUFF"]:
                if self.AttributeValueDict["BUFF_TRIGGER_ON"] == 0:     
                    target.ATK -= 10
                    print("{}'s sword dims".format(target.name))
                    target.modify_buff_stack_dict("remove", self.AttributeValueDict["BUFF_STATUS"])

    def Leech(self, target, caster):
        damage = caster.ATK + 5 - target.DEF + randint(0, 6)
        if damage < 0:
            target.hp -= damage
            caster.hp += damage
            print("{} leeched {} health from {}!".format(caster.name, damage, target.name))       
        else:
            print("{} was unable to leech health from {}!".format(caster.name, damage, target.name))   

    def Poison(self, target):                                                      # each part happens IN the caster's turns
        damage = 2 - math.floor(target.DEF / 3)  
        if damage < 0:    
            x, y, z = (0, 0, 0)
        else:
            x, y, z = (damage, damage + 2, damage + 4)
        if self.turns_left == self.AttributeValueDict["LASTS"]:  
            target.hp -= x
            print("{} took {} damage from a poison dart!".format(target.name, x))     
        elif self.turns_left > 0:                                    
            y_final = y * target.buff_stacks_dict["PSN"]
            target.hp -= y_final 
            print("{} took {} damage from poisoning!".format(target.name, y_final))     
        elif self.turns_left == 0:
            z_final = z * target.buff_stacks_dict["PSN"]
            target.hp -= z_final
            print("{} took {} damage from poisoning!".format(target.name, z_final))     
        else: 
            if self.AttributeValueDict["IS_BUFF"]:
                if self.AttributeValueDict["BUFF_TRIGGER_ON"] == 0:      
                    print("{} recovered from Poison".format(target.name))
                    target.modify_buff_stack_dict("remove", self.AttributeValueDict["BUFF_STATUS"])

    def RaiseShield(self, target):                                                                                  # also in future it could mean value could vary with unit stats e.g. MAGIC
        if self.turns_left == self.AttributeValueDict["LASTS"]:      #if just cast, increase ATK by 10
            target.DEF += 15
            print("Your DEF has increased by 15!")
        else:                                                           #reverse effects in last turn
            target.DEF -= 15
            print("{} lowers their shield".format(target.name))
            target.modify_buff_stack_dict("remove", self.AttributeValueDict["BUFF_STATUS"])

    def Feint(self, target):                                                                                  # also in future it could mean value could vary with unit stats e.g. MAGIC
        if self.turns_left == self.AttributeValueDict["LASTS"]:      #if just cast, increase ATK by 10
            target.DODGE += 60
            print("Your DODGE has increased by 60%!")
        elif self.turns_left == 0:                                                           #reverse effects in last turn
            target.DEF -= 60
            print("{} takes a steady stance. Your DODGE returns to normal.".format(target.name))
            target.modify_buff_stack_dict("remove", self.AttributeValueDict["BUFF_STATUS"])

from Units import Unit, Unit_Knight, Unit_Thief