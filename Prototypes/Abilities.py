"""
All ability effects (except initial mana cost) will be handled here.
Entering point into this class is through Unit.choose_move(), where an Abilityobject is created, and then its determine_targets() method is called



Class methods:
    - get_attr(skill_name, ATTRIBUTE_NAME): Uses ATTRIBUTE_NAME_LIST and ability_dict to get an index and then value of a skill's attribute
    - get_flat_list(nested_list): helps flatten nested lists for easier iteration
----damage-related class methods------------
    - select_target(ability_name, target_team): displays available targets (in targeted team and alive) and returns a unit from user input
    - damage_target(damage_amount, target): subtracts damage from target's HP
    - heal_target(heal_amount, target): adds damage to target's HP
    - check_abilityList(ability): 

Instance methods:
    - y.determine_targets(move_name):  Determine available target/s, calling select_target if needed, then calls Ability.targeted() or other Ability methods for damage calculations/ability mechanics)
    - y.targeted(target_list, caster): Displays available targets then gets target unit from user input
    - y.initial_dmg(target): calculates damage range from DMG_BASE and DMG_ROLL, gets random damage from that range and calls damage_target()
    - y.initial_heal(target): gets HEAL and calls heal_target()

Abilities should follow this format:
( "NAME", ["TARGET_TYPE", "TARGET_ENEMY", "TARGET_NUM"], ["DMG_BOOL", "DMG_BASE", "DMG_ROLL"], "MP", "HEAL", ["SPECIAL", "LASTS"]     #SUBJECT TO CHANGE ACCORDING TO THE NEEDS OF CREATED ABILITIES

TARGET [0]:
    TARGET_TYPE [0]     - (int) 0 = self,       1 = single,     2 = multiple,   3 = team (units in the team will no be differentiated),   4 =  all (units will not be differentiated)
    TARGET_ENEMY [1] - (boolean) True if targets enemies, False if it targets allies (use x if TARGET_TYPE = self, all )
    TARGET_NUM [2]      - (int) Number of targets to target if TARGET_TYPE = multiple (use x if otherwise)
DAMAGE [1]:           
    DMG_BOOL [0]         - (boolean) True if move does initial damage, False otherwise
    DMG_BASE [1]         - (int) base damage of this ability. This is added onto the ATK of the unit
    DMG_ROLL [2]         - (int) amount by which base damage may deviate each way, i.e. DMG_BASE ± DMG ROLL = Damage range (0 for no deviation) 
MP [2]              - (int) MP required (0 for none)
HEAL [3]            - (int) HP healed (x for none)
OTHER [4]:      
    SPECIAL [0]     - (boolean) True if ability will require its own method (i.e. it has unique mechanics not covered by basic ones), False otherwise
    LASTS [1]       - (int)  Number of moves (target moves, ending at the end of last one) this ability will last for, e.g. for a buff, or damage over time (1 is default)
"""

from collections import OrderedDict
import time
from random import randint

class Ability():
    #ATTRIBUTE_NAME_LIST and abilityDict store data about abilities and how they work

    #if an ATTRIBUTE needs to be added/removed, they should be changed concurrently 
    #(i.e. as well as modifying ATTRIBUTE_NAME_LIST, all abilities must have their lists modified to mirror the new change in indexes)
    ATTRIBUTE_NAME_LIST = [["TARGET_TYPE", "TARGET_ENEMY", "TARGET_NUM"], ["DMG_BOOL", "DMG_BASE", "DMG_ROLL"], "MP", "HEAL", ["SPECIAL", "LASTS"]]            
                                                                                           
    x = None
    abilityDict = OrderedDict((                                                                        
        ('Punch',           [[1, True, x],  [True, 0, 2],  0, x,    [False, 1]]),       #works                         #To use an ability, it will have to be added to a unit's moveList
        ('Kick',            [[1, True, x],  [True, 4, 4],  2, x,    [False, 1]]),       #works                         #abilities with unique mechanics not covered by these need their own special function

        ('Magic bolt',      [[1, True, x],  [True, 10, 1], 6, x,    [False, 1]]),       #works
        ('Healing punch',   [[1, True, x],  [True, 8, 2],  5, 8,    [True, 1]]),        #damages then heals target..should damage target and heal caster.. make a special method

        ('Heal self',       [[0, x,     x], [False, x, x], 5, 10,   [False, 1]]),       #works
        ('Heal',            [[1, False, x], [False, x, x], 10, 15,  [False, 1]]),       #works
        ('Heal team',       [[3, False, x], [False, x, x], 16, 30,  [False, 1]]),       #works

        ('Nuke',            [[4, x,     x], [True, 99, 0], 30, x,   [False, 1]]),       #works

        ('Big kick',        [[3, True, x],   [True, 0, 6],  6, x,   [False, 1]]),       #works

        ('Increase ATK',    [[0, x,     x],  [False, x, x],  4, x,  [True,  3]])        #works
        #('Triple Kick',     [[2, True, 3],      [True, 8, 2],        6, 0, [True]]) #should attack same target three times
    ))

    ability_ID_counter = 0
    Ability_queue = []          #most abilities are added and immediately used then removed, 
                                # (to add: those with LASTS stay (e.g. DoT, buffs) for )
    
    def __init__(self, ability_name, ability_ID):       

        self.ability_ID = ability_ID    #is this needed? The only reference to an ability after its turn is over is through the Ability_queue, is that enough?

        self.ABILITY_NAME = ability_name                                                        #used to match to special method if needed
        self.target = None                                                                      #the target of this ability
        self.caster = None                                                                      #the one using this ability, used in helping determine if it's a players turn

        flat_attribute_name_list = Ability.get_flat_list(Ability.ATTRIBUTE_NAME_LIST)             #indexes of these two lists should match
        flat_attribute_value_list = Ability.get_flat_list(Ability.abilityDict[ability_name])
        self.AttributeValueDict = dict(zip(flat_attribute_name_list, flat_attribute_value_list)) #maps attribute to its value as a key:value pair

        self.turns_left = self.AttributeValueDict["LASTS"] -1 
        Ability.ability_ID_counter += 1                                                         #for ability_ID during creating... is this needed?

#========================================Class methods===========================================================================================
    #Uses ATTRIBUTE_NAME_LIST and ability_dict to get an index and then value of (skill_name, ATTRIBUTE_NAME)
    #this is used when an Ability object is not refered to directly, e.g. getting MP for Unit.display_moves()
    def get_attr(skill_name, ATTRIBUTE_NAME):
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

    def get_flat_list(nested_list):
        flat_list = []
        for element in nested_list:                     #for all elements in nested_list
            if isinstance(element, list):                           #if the element is a list
                flat_list += element                       #append the list to the flat list
            else: flat_list += [element]               #else add element to flat list 
        return flat_list

    #displays available targets (in targeted team and alive) and returns a unit from user input
    def select_target(ability_name, target_team):
        targets_alive = Unit.currently_alive(target_team)
        for target in targets_alive:
            print("{}. {}".format(targets_alive.index(target)+1, target.name))
        print("Who would you like to use {} on?".format(ability_name))
        while True:
            try:
                select_who = int(input("> "))                       #choose who to attack
                if select_who in range(1,len(targets_alive)+1):
                    print()
                    break
                else:
                    print("Please enter a valid number")
            except ValueError:
                print("Please enter a valid number")
        return targets_alive[select_who-1]

    #called in targeted() (after current ability procs) to see if there are any other abilities in the queue
    #Just to be clear: AbilityObject is created with (LASTS - 1) moves_left (i.e. normal moves will have 0)
    #                     > AbilityObject does all effects, then check_abilityList checks if AbilityObject needs to be removed (normal abilities are removed at this stage)
    #                         > Any other AbilityObjects have their turns_left - 1 (if caster's move) (there may now be buffs with turns_left = 0, which are removed), and the remaining ones are procced
    #                               > 
    def check_abilityList(current_ability):
        if len(Ability.Ability_queue) >= 2:             #if there are two more AbilityObjects in queue,
            if current_ability.turns_left == 0:                     #if passed AbilityObject was not a buff/DoT, remove it from queue 
                del Ability.Ability_queue[-1]
                copy_queue = Ability.Ability_queue
            else:                                           #else, make a new list without passed AbilityObject
                copy_queue = Ability.Ability_queue[:-1]     
            for ability in copy_queue:                      #for remaining buffs/DoTs
                if ability.turns_left == 0:                     #if turns_left = 0, remove it from queue (i.e. end of ability)
                    Ability.Ability_queue.remove(ability)
                else:                                           #else, 
                    if ability.caster == current_ability.caster:    #if the caster is the same person (i.e. ability belongs to caster)
                        ability.turns_left -= 1                         # subtract a turn from turns_left
                        ability.targeted(ability.target, ability.caster)# and proc it

    #abilities that need to reduce target's hp should use this
    def damage_target(damage_amount, target):
        target.hp -= damage_amount                             #target loses HP
        print("{} took {} damage!".format(target.name, damage_amount))

    #abilities that are 'heals' should use this
    def heal_target(heal_amount, target):
        target.hp += heal_amount
        print("{} was healed for {} HP!".format(target, heal_amount))
#=================================Instance methods=========================================================================================

    #use TARGET attributes to determine available target/s, calling select_target if needed, then calling Ability.targeted() or other Ability methods for damage calculations/ability mechanics)
    def determine_targets(self, caster):
        target_type = self.AttributeValueDict["TARGET_TYPE"]
        target_is_enemy = self.AttributeValueDict["TARGET_ENEMY"]      

        if target_type == 0:                                                            #if TARGET_TYPE is self,        
            target_list = [caster]                                                          #call Ability.targeted() on the caster        

        if target_type in [1, 2, 3]:                                #if TARGET_TYPE is single, multiple, or team
            if target_is_enemy:                                         #if TARGET_ENEMY = True
                target_team = Unit.all_units_list[1 - caster.team]            #then target team is the opposite team
            else:
                target_team = Unit.all_units_list[caster.team]                #else the target team is own team

            if target_type == 1:                                                        #if TARGET_TYPE = single target
                target_list = [Ability.select_target(self.ABILITY_NAME, target_team)]        #call select_target() to get one target for target_list

            if target_type == 2:                                        #if TARGET_TYPE = multiple targets
                #
                #needs a new select_targetS() method, then target_list is those selected
                print("TARGET_TYPE = 2 still working on it")       

            if target_type == 3:                                        #if TARGET_TYPE = team
                target_list = target_team                                   #target_list is target_team

        if target_type == 4:                                            #if TARGET_TYPE = all
            target_list = []                                                #target_list is all units
            for team in Unit.all_units_list:                                
                target_list += team
            
        print("You used {}".format(self.ABILITY_NAME))
        time.sleep(0.8)
        for target in target_list:
            self.targeted(target, caster)
            print()

        #after ability has had its effects done, save the target and caster in this AbilityObject
        self.target = target
        self.caster = caster
        Ability.check_abilityList(self)         #then check for other abilities still in queue

    #Do basic mechanics using ABILITY_ATTRIBUTES to target
    def targeted(self, target, caster):                     
        if self.AttributeValueDict["DMG_BOOL"]:
            self.initial_dmg(target, caster)
            
        if self.AttributeValueDict["HEAL"] != None:
            self.initial_heal(target)

        if self.AttributeValueDict["SPECIAL"]:
            self.special_sorter(target, caster)

    def initial_dmg(self, target, caster):
        minDMG, maxDMG = (self.AttributeValueDict["DMG_BASE"] - self.AttributeValueDict["DMG_ROLL"],
                            self.AttributeValueDict["DMG_BASE"] + self.AttributeValueDict["DMG_ROLL"])
        damage_dealt = caster.ATK + randint(minDMG,maxDMG)
        Ability.damage_target(damage_dealt,target)

    def initial_heal(self, target):
        heal_amount = self.AttributeValueDict["HEAL"]
        Ability.heal_target(heal_amount, target)
        

    #----------------------Special instance methods----------------------------------------------------
    #Only abilities with LASTS greater than 1 or is SPECIAL access this method and section
    #This method maps the ability to its method containing unique mechanics
    def special_sorter(self, target, caster=None):
        if self.ABILITY_NAME == "Increase ATK":
            self.IncreaseATK(target)

    #This section contains all methods used by abilities that have unique mechanics not covered by basic ones

    #In addition to no basic mechanics, increases target (self) ATK by 10 for 2 turns (excluding this turn)         #this ability's value is hardcoded, maybe make a BUFF_VALUE attribute so it can change
    def IncreaseATK(self, target):                                                                                  # also in future it could mean value could vary with unit stats e.g. MAGIC
        if self.turns_left == self.AttributeValueDict["LASTS"] -1:      #if just cast, increase ATK by 10
            target.ATK += 10
            print("Your ATK has increased by 10!")
            target.buffs += ["+ATK"]
        elif self.turns_left > 0:                                       #if already had a turn and still not dead, do nothing
            pass
            #print("Your sword is gleaming")
            #time.sleep(0.8)
        else: 
            target.ATK -= 10
            print("{}'s sword dims".format(target.name))
            target.buffs.remove("+ATK")

from Units import Unit

