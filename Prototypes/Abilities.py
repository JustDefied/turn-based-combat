"""
All ability effects (except initial mana cost) will be handled here.
Entering point into this class is through Unit.choose_move(), where an Abilityobject is created, and then its determine_targets() method is called

Class methods:

    - get_attr(skill_name, ATTRIBUTE_NAME): gets the index and returns the value of a skill's attribute
    - check_Ability_queue(current_ability): removes expired abilities and procs active ones in the ability queue

    ----unit stat-modifying class methods------------
    - damage_target(damage_amount, target, dmg_type): damage (no calculations) with generic message outputs and minimum damage of 0
    - heal_target(target, hp_gain, mp_gain): healing (no calculations) with generic message outputs with cap at target's max hp/mp


Instance methods:

    - y.build_AttrValDict(): populates this ability object's AttrValDict with its stats as key:value pairs
    - y.determine_targets(caster): determines this ability's available targets to fill target_list (using select_target(target_team) if needed)
    - y.initial_cast(target_list, caster): use cast_on_target(target, caster) for targets in target_list (also check_stacks(target) if ability is a buff), 
                                            then check_Ability_queue(self) if there are any other abilites in queue
    - y.check_stacks(target): checks the stacks of the ability on the target, makes sure stack limit is not breached (this is only called by cast_on_target() if ability was successful)
    - y.select_target(target_team, caster):
    - y.cast_on_target(target, caster): Actions the ability's effects on the target 

    Instance (calculation) methods:
        - y.calculate_dmg(caster): calculates damage range from DMG_BASE and DMG_ROLL, gets random damage from that range and calls damage_target()
        - y.calculate_heals(target, caster)
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
        CAN_DODGE [2]   - (boolean) If ability can be dodged, True, else False
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
    #ATTR_NAME_LIST and aDict store data about abilities and how they work
    ATTR_NAME_LIST = [["TARGET_TYPE", "TARGET_ENEMY", "TARGET_NUM"], ["SPECIAL", "LASTS", "CAN_DODGE"], ["MP_COST"], ["DMG_TYPE", "DMG_IS_PERCENT", "DMG_BASE", "DMG_ROLL"], ["IS_HEAL", "HP_GAIN", "MP_GAIN"], ["IS_BUFF", "BUFF_TRIGGER_ON", "BUFF_ENDS",  "BUFF_STACKS", "BUFF_STATUS"], ["INFO"]] 
#----------------ABILITIES LIST--------------------------------------------------------------------------------------------------------------------------
    x = None
    aDict = OrderedDict((                                                                        
    ('Punch',           [[1, True,  x], [False, 0, True], [1],  ["NORMAL", False, 0, 2],    [False],      [False],                    ["Deal ATK(±2) damage to a target"]     ]),                             #To use an ability, it will have to be added to a unit's moveList
    ('Dagger stab',     [[1, True,  x], [False, 0, True], [1],  ["NORMAL", False, 2, 1],    [False],      [False],                    ["Deal ATK+2(±1) damage to a target"]     ]),                              #abilities with unique mechanics not covered by these need their own special function

    ('Magic bolt',      [[1, True,  x], [False, 0, True], [4],  ["MAGIC", False, 0, 2],   [False],      [False],                    ["Deal MAGIC(±2) magic damage to a target"]     ]),       #
    ('Leech',           [[1, True,  x], [True, 0, True],  [15], [False],                    [False],      [False],                    ["Steal HP from an enemy"]      ]),        #

    ('Rest',            [[0, x,     x], [False, 0, False], [0],  [False],                    [True, 6, 6], [False],                    ["Recover 6HP and 6MP"]  ]),       #
    ('First aid',       [[0, x,     x], [False, 0, False], [12], [False],                     [True, 20, 0], [False],                   ["Recover 20HP"]  ]),      #
    ('Heal',            [[1, False, x], [False, 0, False], [8], [False],                    [True, 20, 0], [False],                   ["Target ally will recover 20HP"]  ]),        #
    ('Heal team',       [[3, False, x], [False, 0, False], [16], [False],                    [True, 15, 0], [False],                   ["All units in team recover 15HP"]  ]),        #

    ('Nuke',            [[4, x,     x], [False, 0, False], [30], ["NORMAL", False, 99, 0],   [False],      [False],                    ["All units are dealt 99 damage (+ ATK)"]      ]),         #

    ('Big kick',        [[3, True,  x], [False, 0, True], [6],  ["NORMAL", False, 0, 6],    [False],      [False],                    ["All enemy units are dealt ATK ± 6 damage"]      ]),       #

    ('Sharpen sword',    [[0, x,     x], [True,  2, False], [6],  [False],                   [False],     [True, 0, 1, 1, "+ATK"],     ["Increase own ATK by 10 for the next 2 turns"]     ]),       #

    ('Poison',          [[1, True,  x], [True,  4, True], [5],  [False],                    [False],      [True, 0, 0, 3, "PSN"],     ["Shoot a poisonous dart into the target, doing minor damage and Poisoning them for the next 4 turns. Additional stacks increase damage dealt. Stacks 3 times."]  ]),      #

    ('Sword slash',     [[1, True,  x], [False, 0, True], [1],  ["NORMAL", False, 3, 2],    [False],      [False],                    ["Deal ATK+3(±2) damage to a target"]     ]),
    ('Raise shield',    [[0, x,     x], [True,  1, False], [2],  [False],                    [False],      [True, 0, 0, 1, "+DEF"],    ["Increase your DEF by 8 until your next turn"]     ]),
    ('Feint',           [[0, x,     x], [True,  2, False], [3],  [False],                    [False],      [True, 0, 0, 1, "+DODGE"],  ["Increase your DODGE by 60% for the next 2 turns"]     ]),
    ('Taunt',           [[1, True,  x], [True,  2, False], [4],  [False],                    [False],      [True, 0, 0, 1, "-DEF"],    ["Decrease the target's DEF by 6 for 2 turns"]     ])
    #('Triple Kick',     [[2, True, 3],      [True, 8, 2],        6, 0, [True]]) #should attack same target three times

    ))
#------------------------------------------------------------------------------------------------------------------------------------------
    #any buff that modifies unit stats should an entry here, following this key/value format:
                            # ability_name : [ [max_hp, max_mp, ATK, DEF, CRIT, DODGE],     #enter a value in the slot for the stat that will be changed, else use 0
                            #                   casted_prompt,                               #displayed at time of casting
                            #                   buff_action_prompt,                          #for BUFF_ENDS = 0, displayed as turn begins, 
                            #                                                                for BUFF_ENDS = 1, displayed after turn finishes,
                            #                   buff_reminder_prompt,                        # displayed right after display_moves()
                            #                   end_prompt                          ]

    buffDict = { "Sharpen sword" :  [0, 0, 10, 0, 0, 0],
                'Raise shield':     [0, 0, 0, 8, 0, 0],
                'Feint':            [0, 0, 0, 0, 0, 60], 
                'Taunt' :           [0, 0, 0, -6, 0, 0]  }

#------------------------------------------------------------------------------------------------------------------------------------------


    ability_ID_counter = 0
    Ability_queue = []          #most abilities are added, used then immediately removed, those with LASTS > 1 stay longer

    
    def __init__(self, ability_name, ability_ID):       

        self.ability_ID = ability_ID    #is this needed? The only reference to an ability after its turn is over is through the Ability_queue, is that enough?
        Ability.ability_ID_counter += 1       #for ability_ID during creating... is this needed?

        self.ABILITY_NAME = ability_name                                                        #used to match to special method if needed
        self.target_list = None                                                                      #the target of this ability
        self.caster = None                                                                      #the one using this ability, used in helping determine if it's a players turn
        self.AttrValDict = self.build_AttrValDict()
        self.turns_left = self.AttrValDict["LASTS"]

        self.sp_val = None              #a place to store a value for this particular ability, e.g. target's DEF at time of casting
        
        self.special_mapDict = { "Sharpen sword" :  self.IncreaseATK,
            'Raise shield': self.RaiseShield,
            'Feint':  self.Feint, 
            'Taunt' :  self.Taunt,
            "Poison": self.Poison ,
            "Leech": self.Leech          }
#========================================Class methods===========================================================================================
    #Uses ATTR_NAME_LIST and ability_dict to get an index and then value of (skill_name, ATTRIBUTE_NAME)
    #this is used when an Ability object is not refered to directly, e.g. getting MP for Unit.display_moves()
    @classmethod
    def get_attr(cls, skill_name, ATTRIBUTE_NAME):
        attribute_value = None
        ability_attributes = Ability.aDict[skill_name]            #a list containing attributes' values of a particular skill
        if ATTRIBUTE_NAME in Ability.ATTR_NAME_LIST:                        #if ATTRIBUTE_NAME is found by first-level search,
            index = Ability.ATTR_NAME_LIST.index(ATTRIBUTE_NAME)                #get the index of ATTRIBUTE_NAME
            attribute_value = ability_attributes[index]                         #and use index to get value from aDict
        else:                                                               #ATTRIBUTE_NAME might be found in a secondary-level LIST 
            for attributes in Ability.ATTR_NAME_LIST:                               #for each LIST in ATTR_NAME_LIST, e.g. ["TARGET_TYPE", "TARGET_TEAM"]
                if isinstance(attributes, list):                                    #
                    if ATTRIBUTE_NAME in attributes:                                    #if ATTRIBUTE_NAME is found in this list
                        try:                                                                #try 
                            index1 = Ability.ATTR_NAME_LIST.index(attributes)                   #to get the two-level index of the ATTRIBUTE_NAME
                            index2 = Ability.ATTR_NAME_LIST[index1].index(ATTRIBUTE_NAME)       #
                            attribute_value = ability_attributes[index1][index2]                #and use index to get value from aDict
                        except IndexError:                                                  #if the value does not exist in that index,
                            print("The value for this ability attribute does not exist!")        #print an error message (for debugging purposes)
                            return None                                                         #continue excecution, returning attribute value of None
        if attribute_value == None:                                             #if both loops ended
            raise ValueError('Attribute does not exist!')                           #and ATTRIBUTE NAME is not found, print error message (for debugging purposes)
        return attribute_value

    #checks queue for expired abilities and removes them from queue, procs any remaining abilities (excluding current one) and -1 their turns_left, then 
    @classmethod
    def check_Ability_queue(cls, current_ability = None, casting_unit = None):      
        if current_ability != None:                                                 #if this was called with a current_ability, then it was called by initial_cast()
            if current_ability.turns_left == 0:             #if current ability was immediate, remove it from queue 
                #print("{} is being deleted".format(current_ability.ABILITY_NAME))   FOR DEBUGGING
                for target in current_ability.target_list:
                    target.target_Ability_queue
                del Ability.Ability_queue[-1]
                copy_queue = Ability.Ability_queue
            else:                                           #else, make a new list without the current ability (so other abilities can proc)
                copy_queue = Ability.Ability_queue[:-1]     
            for ability in copy_queue:                      #for each ability in queue (less current one)
                if ability.turns_left == 0:                     #if expired, remove it from queue (i.e. turns_left = 0)
                    Ability.Ability_queue.remove(ability)
                else:                                           #else, 
                    if ability.caster == current_ability.caster:    #if the caster is the same person (i.e. ability belongs to caster)
                        if ability.AttrValDict["BUFF_ENDS"] == 1:       #if buff 
                            ability.turns_left -= 1                         # subtract a turn from turns_left and proc the ability for each of its targets
                            for target in ability.target_list:
                                ability.cast_on_target(target, ability.caster)# and proc it
                                time.sleep(0.5)
        elif casting_unit != None:                                  #otherwise, this was called with a casting_unit, and method was called by choose_move()
            copy_queue = Ability.Ability_queue
            for ability in reversed(copy_queue):                      #for each ability in queue (less current one)
                if ability.turns_left == 0:                     #if expired, remove it from queue (i.e. turns_left = 0)
                    #print("{} is being deleted".format(ability.ABILITY_NAME))              for DEBUGGING
                    Ability.Ability_queue.remove(ability)
                else:                                           #else, 
                    if ability.caster == casting_unit:    #if the caster is the same person (i.e. ability belongs to caster)
                        if ability.AttrValDict["BUFF_ENDS"] == 0:
                            ability.turns_left -= 1                         # subtract a turn from turns_left and proc the ability for each of its targets
                            for target in ability.target_list:
                                ability.cast_on_target(target, ability.caster)# and proc it
                                time.sleep(0.5)

    #generic damage (no calculations) with message outputs and minimum damage of 0
    @classmethod
    def damage_target(cls, final_damage, target, dmg_type):
        if dmg_type == "NORMAL":
            damage_message = "physical"
            blocked_message = "Their defence is too high!"
        elif dmg_type == "MAGIC":
            damage_message = "magic"
            blocked_message = "Their magic is too strong!"
        if final_damage > 0:                                #if there is damage,
            target.hp -= final_damage                             #target loses HP
            print("{} took {} {} damage!".format(str(target), final_damage, damage_message))       
        else:
            print("{} took no damage... {}".format(str(target), blocked_message))

    #abilities that are 'heals' should use this
    @classmethod
    def heal_target(cls,target, hp_gain, mp_gain):

        if hp_gain > 0:
            healed_to_max = (hp_gain + target.hp) >= target.max_hp
            if healed_to_max:
                print("{} was fully healed!".format(target))
            else:
                print("{} was healed for {} health!".format(target, hp_gain))
            target.hp += hp_gain
        if mp_gain > 0:
            mp_to_max = (mp_gain + target.mp) >= target.max_mp
            if mp_to_max:
                print("{}'s mana was fully restored!".format(target))
            else:
                print("{} recovered {} mana!".format(target, mp_gain))
            target.mp += mp_gain

    #finds every ability that targets the target and calls remove_ability() on them     ####maybe change when there are buffs that will have multiple targets
    @classmethod                                                                                    #i.e. if ability has more than one target in target_list, remove target from list and clear target without using remove_ability()
    def clear_target(cls, target):
        temp_copy = Ability.Ability_queue[:]
        for ability in temp_copy:
            if target in ability.target_list:
                Ability.remove_ability(ability, target)


    #removes an ability's buff indicator (in unit's stack dict), reverts its effects, and removes the ability from queue 
    @classmethod
    def remove_ability(cls, ability, target):
        if ability.AttrValDict["IS_BUFF"]:
            target.modify_buff_stack_dict("remove", ability.AttrValDict["BUFF_STATUS"])
            #print("removed {} from {}'s buff_stack_dict".format(ability.AttrValDict["BUFF_STATUS"], str(target)))          for debugging
        if ability.ABILITY_NAME in Ability.buffDict:                                               #if ability had stat-modifying, revert stats first
            ability.buff_stat_modifier("remove", target)                                                       #and remove it from target's buffs stack dict
            #print("reverted effects of {} from {}".format(ability.ABILITY_NAME, str(target)))                              #for debugging
        Ability.Ability_queue.remove(ability)                                               #remove the ability for good

#=================================Instance methods=========================================================================================
    #populates this ability object's AttrValDict with its stats as key:value pairs
    def build_AttrValDict(self):
        built_dict = {}
        abil_attr_list = Ability.aDict[self.ABILITY_NAME]                         #list of all attribute values
        for section in Ability.ATTR_NAME_LIST:                                             #for each section in ATTR_NAME_LIST
            section_index = Ability.ATTR_NAME_LIST.index(section)                              #store the section's index
            if abil_attr_list[section_index][0] == False and section_index not in [0, 1]:   #if first attribute in section is False, ignore the rest of the section
                built_dict[section[0]] = abil_attr_list[section_index][0]          #(unless that section is OTHER) and add that first attribute and value
            else:                                                                                   
                for attribute in section:
                    attribute_index = section.index(attribute)
                    built_dict[attribute] = abil_attr_list[section_index][attribute_index]
        return built_dict

    #determines this ability's available targets and gets targets (using select_target() if needed) to get a target_list
    def determine_targets(self, caster, is_multiplayer = False):
        target_type = self.AttrValDict["TARGET_TYPE"]
        target_is_enemy = self.AttrValDict["TARGET_ENEMY"]      

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
                    target_list = [self.select_target(target_team, caster, is_multiplayer)]             #call select_target() to get one target for target_list
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

    #sets the target_list and caster for this ability, takes MP_COST, displays 'used' output, and for every target in target_list, check buff_stacks if is a buff and cast_on_target(), then check_Ability_queue() if needed
    def initial_cast(self, target_list, caster):
        self.target_list = target_list                            #store target_list and caster in ability instance
        self.caster = caster
        if self.AttrValDict["TARGET_TYPE"] ==  0:
            print("{} used {} on themself".format(caster.name, self.ABILITY_NAME))
        elif self.AttrValDict["TARGET_TYPE"] == 1:
            print("{} used {} on {}".format(caster.name, self.ABILITY_NAME, str(self.target_list[0])))
        else:
            print("{} used {}".format(caster.name, self.ABILITY_NAME))
        caster.mp -= self.AttrValDict["MP_COST"]
        time.sleep(0.8)
        for target in target_list:                      #for every target unit
            success = self.cast_on_target(target, caster)                   #use cast_on_target()
            if self.AttrValDict["IS_BUFF"]:                         #if ability is a buff 
                if success == None:                                     #if cast was successful
                    self.check_stacks(target)                                           #check stacks for stack limits
        if len(Ability.Ability_queue) >= 2:             #if there are two or more abilities in queue,
            Ability.check_Ability_queue(current_ability = self)                 #then call check_Ability_queue to check other abilities still in queue
        #for ability in Ability.Ability_queue:                          #FOR DEBUGGING
            #print(ability.ABILITY_NAME)

    #if the ability is not stackable or past BUFF_STACKS limit, remove the first instance of the same ability, else, add a stack to unit.buff_stack_dict
    def check_stacks(self, target):
        times_stackable = self.AttrValDict["BUFF_STACKS"]
        buff_status = self.AttrValDict["BUFF_STATUS"]
        target.modify_buff_stack_dict("add", buff_status)                                       #add a stack initially
        if target.buff_stacks_dict[buff_status] > times_stackable:                              #if stacks is over limit,
            print("MAX stacks already reached.")                                                         
            for ability in Ability.Ability_queue:                                                   #search ability queue
                check_targets = ability.target_list                                                    
                if ability.ABILITY_NAME == self.ABILITY_NAME and target in check_targets:               #if ability has same name and target,
                    Ability.remove_ability(ability, target)                                                 #delete the ability (stack is removed in remove_ability())
                    break

    #displays available targets (in targeted team and alive) and returns a unit from user input
    def select_target(self, target_team, caster, is_multiplayer = True):
        targets_alive = Unit.get_units("alive", target_team[0].team)
        if is_multiplayer == True:
            print("Who would you like to use {} on?".format(self.ABILITY_NAME))
            for target in targets_alive:
                print("{}. {}".format(targets_alive.index(target)+1, str(target)))
            while True:
                try:
                    select_who = input("> ")                     #choose who to attack
                    if select_who == "b":                               #input b to choose another move (by returning with None)#
                        caster.choose_move(self)
                        return None
                    if int(select_who) in range(1,len(targets_alive)+1):             #if input number in range
                        target = targets_alive[int(select_who)-1]
                        if self.AttrValDict["IS_HEAL"]:
                            if self.AttrValDict["HP_GAIN"] != 0 and target.hp >= target.max_hp:                                        
                                print("Already at full health!")
                            elif self.AttrValDict["MP_GAIN"] != 0 and target.mp >= target.max_mp:
                                print("Already at full mana!")
                            else:
                                break
                        else:
                            break
                    else:
                        print("Please enter a valid number or enter 'b' to go back.")
                except ValueError:
                    print("Please enter a number or enter 'b' to go back.")
            print()
        else: 
            target = targets_alive[random.randint(0,len(targets_alive)-1)]              #else comp will choose random target
        return target

    #Do basic mechanics using ABILITY_ATTRIBUTES to target
    def cast_on_target(self, target, caster):          
        if not self.ability_dodged(target):                                 #if abiltiy hits (i.e. ability_dodged = False)
            if self.AttrValDict["SPECIAL"]:              #put it first in order because ..
                success = self.special_sorter(target, caster)                           
                if success == None:                                                                     #if success == None (i.e. not False)
                    if self.AttrValDict["IS_BUFF"] and self.turns_left == 0:                                     #if ability was buff AND ability is expiring,,
                        target.modify_buff_stack_dict("remove", self.AttrValDict["BUFF_STATUS"])                    #remove this buff stack
                elif success == False:                                                                  #elif move was unsuccessful
                    self.turns_left = 0     
            dmg_type = self.AttrValDict["DMG_TYPE"]                                                                #set turns_left to 0 to be deleted by check_Ability_queue()
            if dmg_type in ["NORMAL", "MAGIC"]:
                if dmg_type == "NORMAL":
                    raw_damage = self.calculate_dmg(caster, dmg_type)
                    final_damage = self.calculate_def(raw_damage, target, dmg_type)
                elif dmg_type == "MAGIC":
                    raw_damage = self.calculate_dmg(caster, dmg_type)
                    final_damage = self.calculate_def(raw_damage, target, dmg_type)
                Ability.damage_target(final_damage, target, dmg_type)
                
            if self.AttrValDict["IS_HEAL"]:
                hp_gain, mp_gain = self.calculate_heals(target)
                Ability.heal_target(target, hp_gain, mp_gain)
        else:
            success = False  
            self.turns_left = 0                                                                     #set turns_left to 0 to be deleted by check_Ability_queue()
        if self.AttrValDict["IS_BUFF"]:                                             #return success to signal if check_stats should be called in initial_cast()
            return success

    def calculate_dmg(self, caster, dmg_type):        #uses DMG_BASE, DMG_ROLL, and caster.ATK/caster.MAGIC to calculate and return raw_damage
        minDMG, maxDMG = (self.AttrValDict["DMG_BASE"] - self.AttrValDict["DMG_ROLL"],
                            self.AttrValDict["DMG_BASE"] + self.AttrValDict["DMG_ROLL"])
        if dmg_type == "NORMAL":
            raw_damage = caster.ATK + randint(minDMG,maxDMG)
        elif dmg_type == "MAGIC":
            raw_damage = caster.MAGIC + randint(minDMG,maxDMG)
        return raw_damage

    def calculate_def(self, raw_damage, target, dmg_type):    #uses a damage value and target.DEF/target.MAGIC to calculate and return final_damage
        if dmg_type == "NORMAL":
            final_damage = raw_damage - target.DEF
        if dmg_type == "MAGIC":
            final_damage = raw_damage - target.MAGIC
        return final_damage

    def calculate_heals(self, target):                  #
        hp_gain = self.AttrValDict["HP_GAIN"]
        mp_gain = self.AttrValDict["MP_GAIN"]
        return hp_gain, mp_gain

    #if CAN_DODGE = True, do dodge calculation and return True if dodged, False if hit, else if CAN_DODGE = False, always return False (ability always hits)
    def ability_dodged(self, target):                       
        if self.AttrValDict["IS_BUFF"] and self.turns_left != self.AttrValDict["LASTS"]:                #if it is a buff stack, it cannot be dodged
            return False
        if self.AttrValDict["CAN_DODGE"]:
            #print("Dodge is: {}".format(target.DODGE))                                 #for debugging
            if random.random() < target.DODGE/100:
                print("{} dodged the attack!".format(str(target)))
                return True
        return False

    #abilities with SPECIAL access this method to get to their special method, using special_mapDict
    def special_sorter(self, target, caster):
        if self.ABILITY_NAME in self.special_mapDict:
            success = self.special_mapDict[self.ABILITY_NAME](target, caster)
            return success
        else:
            print("special_sorter: ABILITY DOES NOT EXIST!!!!!!!!")             #for debugging

    #uses values in buffDict to find which unit stats to change. Usually called twice: at initial buff, and revert at expiration
    def buff_stat_modifier(self, add_remove, target):
        buff_values = Ability.buffDict[self.ABILITY_NAME]
        unit_stats = [target.max_hp, target.max_mp, target.ATK, target.DEF, target.CRIT, target.DODGE]          #HOW TO MAKE THIS WORK>>>>>>
        for index in range(len(buff_values)):
            if buff_values[index] != 0:
                val_to_add = buff_values[index]
                if add_remove == 'remove':
                    val_to_add = -buff_values[index]            #if method was called to remove, make value negative
                #print("This will be added: {}".format(val_to_add))                             #for debugging
                if index == 0:
                    target.max_hp += val_to_add
                elif index == 1:
                    target.max_mp += val_to_add  
                elif index == 2:
                    target.ATK += val_to_add   
                elif index == 3:
                    target.DEF += val_to_add    
                elif index == 4:
                    target.CRIT += val_to_add   
                elif index == 5:
                    target.DODGE += val_to_add       

#----------------------Special instance methods----------------------------------------------------
    #This section contains all methods used by abilities that have unique mechanics not covered by basic ones
    #
    def IncreaseATK(self, target, caster=None):             
        if self.turns_left == self.AttrValDict["LASTS"]:
            self.buff_stat_modifier("add", target)
            print("{}'s ATK has increased by 10!".format(str(target)))
        elif self.turns_left > 0:                                       #do nothing if in 2nd turn
            print("{}'s sword gleams".format(str(target)))
        elif self.turns_left == 0:                                     #reverse effects after last turn
            if self.AttrValDict["IS_BUFF"]:
                if self.AttrValDict["BUFF_TRIGGER_ON"] == 0:     
                    self.buff_stat_modifier("remove", target)
                    print("{}'s sword dims".format(str(target)))

    #
    def Leech(self, target, caster):
        damage = caster.ATK + 5 - target.DEF + randint(0, 6)
        if damage < 0:
            target.hp -= damage
            caster.hp += damage
            print("{} leeched {} health from {}!".format(str(caster), damage, str(target)))       
        else:
            print("{} was unable to leech health from {}!".format(str(caster), str(target)))   

    #
    def Poison(self, target, caster=None):   
        if self.turns_left == self.AttrValDict["LASTS"]:
            self.sp_val = target.DEF
        damage = 2 - math.floor(self.sp_val / 2)                                                 #base damage minus half of target's DEF                                                                                       #else three different damages
        x, y, z = (damage, damage + 3, damage + 2)
        if self.turns_left == self.AttrValDict["LASTS"]:                                         #if just cast, do inital dart damage
            if damage <= 0:                                                                              #if damage is 0 or less,
                print("The poison dart bounced off {}... their defense is too high!".format(str(target)))       #ability fails, return False
                return False
            else:
                target.hp -= x
                print("{} took {} damage from a poison dart!".format(str(target), x))   
        elif self.turns_left > 0:                                                                      #elif in middle of buff, add to PSN_dmg (poison dmg x stacks)
            target.PSN_count += 1
            target.PSN_dmg += math.floor(y  + (0.5* y * (target.buff_stacks_dict["PSN"]-1)))  
        elif self.turns_left == 0:                                                                       #elif last turn,add slightly less to (poison dmg x stacks)
            target.PSN_count += 1
            target.PSN_dmg  += math.floor(z  + (0.5* z * (target.buff_stacks_dict["PSN"]-1)))

        if self.turns_left != self.AttrValDict["LASTS"]:                                               #if not initial cast i.e. buff stack call,
            #if target.PSN_count == target.buff_stacks_dict[self.AttrValDict["BUFF_STATUS"]]:            #if PSN_count = stacks by caster (i.e. this is the last stack by caster being called)
            target.hp -= target.PSN_dmg                                                                        #deal the accumulated damage
            print("{} took {} damage from poisoning!".format(str(target), target.PSN_dmg))  
            target.PSN_dmg = 0                                                                                     #and reset dmg/count for next time
            target.PSN_count = 0
            if self.turns_left == 0:                                                                                #if this stack is expiring,
                if target.HP != 0:
                    if target.buff_stacks_dict[self.AttrValDict["BUFF_STATUS"]] == 1:                                       #and about to lose last stack,
                        print("{} has recovered from Poison.".format(str(target)))                                              #target has recovered
                    else:
                        print("{} is slowly recovering from Poison.".format(str(target)))                                     #else if still stacks remaining, target is recovering
    #
    def RaiseShield(self, target, caster=None):                                                                                  
        if self.turns_left == self.AttrValDict["LASTS"]:      #if just cast, increase DEF by 8
            self.buff_stat_modifier("add", target)
            print("{}'s} DEF has increased by 8!".format(str(target)))
        elif self.turns_left == 0:                                                           #reverse effects in last turn
            self.buff_stat_modifier("remove", target)
            print("{} lowers their shield".format(str(target)))

    #
    def Feint(self, target, caster=None):                                                                                  # also in future it could mean value could vary with unit stats e.g. MAGIC
        if self.turns_left == self.AttrValDict["LASTS"]:      #if just cast, increase ATK by 10
            self.buff_stat_modifier("add", target)
            print("{}'s DODGE has increased by 60%!".format(str(target)))
        elif self.turns_left == 0:                                                        #reverse effects in last turn
            self.buff_stat_modifier("remove", target)
            print("{} takes a steady stance. Their DODGE returns to normal.".format(str(target)))

    #
    def Taunt(self, target, caster=None):                                                                                  
        if self.turns_left == self.AttrValDict["LASTS"]:      #if just cast, 
            self.buff_stat_modifier("add", target)
            print("{}'s DEF has decreased by 6!".format(str(target)))
        elif self.turns_left == 0:                                                           #reverse effects in last turn
            self.buff_stat_modifier("remove", target)
            print("{} regains his composure. His DEF returns to normal".format(str(target)))


from Units import Unit, Unit_Knight, Unit_Thief, Unit_Priest