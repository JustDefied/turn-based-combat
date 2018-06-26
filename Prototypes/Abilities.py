"""
This class currently does not create its own objects #will it need to for buffs/debuffs/DoT abilities?
Contains all info about abilities
All methods that are considered related to  particular abilities/moves should also be kept here.

Unit.choose_target() will call Ability.targeted(skill, target), which will call the needed methods.
All combat calculations and Unit attribute modifications (except initial mana cost) will be handled here.

Abilities (moves) should follow this format:

( "NAME", ["TARGET_TYPE", "TARGET_TEAM"],["DMG_BASE", "DMG_ROLL"], "MP", "HEAL"                     ####SUBJECT TO CHANGE ACCORDING TO THE NEEDS OF CREATED ABILITIES

TARGET [0]:
    TARGET_TYPE [0]     - (int) 0 = self,       1 = single,     2 = multiple,   3 = team (units in the team will no be differentiated),   4 =  all (units will not be differentiated)
    TARGET_ENEMY [1] - (boolean) True if targets enemies, False if it targets allies (ignore if TARGET_TYPE = self or all)
DAMAGE [1]:           
    DMG_BOOL [0]         - (boolean) True if move does initial damage, False otherwise
    DMG_BASE [1]         - (int) base damage is added onto unit's attack stat
    DMG_ROLL [2]         - (int) amount by which base damage may deviate each way, i.e. DMG_BASE ± DMG ROLL = Damage range (0 for no deviation) 
MP [2]              - (int) MP required (0 for none)
HEAL [3]            - (int) HP healed (0 for none)

"""
from collections import OrderedDict
import time
from random import randint

class Ability():

    attribute_list = [["TARGET_TYPE", "TARGET_ENEMY"],["DMG_BOOL", "DMG_BASE", "DMG_ROLL"], "MP", "HEAL"]            #get_attr() relies on the content and indexes of this list to work
                                                                                                        
    abilityDict = OrderedDict((                                                                         #this is where all abilities are currently stored
        ('Punch',       [[1,True],  [True, 10,2], 0, 0]),                                                         #To use an ability, it will have to be added to a unit's moveList
        ('Kick',        [[1,True],  [True, 15,3], 2, 0]),                                                             #abilities that aren't simple will need their own method/code

        ('Magic bolt',  [[1,True],  [True, 15,1], 6, 0]),
        ('Heal self',   [[0],       [False],      5, 15]), 
        ('Heal',        [[1,False], [False],      10, 10]),
        ('Heal team',   [[3,False], [False],      16, 6]),

        ('Leech',       [[1,True],  [True, 8, 4], 5, 0]),
        ('Triple Kick', [[1,True],  [True, 8, 2], 6, 0]),

        ('Big kick',    [[3,True],  [True, 15,12], 5, 0])

    ))
    
    def __init__(self):       
        pass

    #using an ability name(str) and attribute name (str), get an ability's attribute's value from abilityDict
    #also serves as a check for boolean attributes
    def get_attr(skill_name, attribute_name):
        attribute_value = None
        ability_attributes = Ability.abilityDict[skill_name]            #a list containing attributes' values of a particular skill
        if attribute_name in Ability.attribute_list:        
            index = Ability.attribute_list.index(attribute_name)
            attribute_value = ability_attributes[index]
        else:                                                               #attribute might be found in a secondary LIST 
            for attributes in Ability.attribute_list:                               #for each LIST in ability attributes, e.g. ["TARGET_TYPE", "TARGET_TEAM"]
                if isinstance(attributes, list):                                    #
                    if attribute_name in attributes:                                    #if attribute is found in this list
                        index1 = Ability.attribute_list.index(attributes)                   #get LIST 
                        index2 = Ability.attribute_list[index1].index(attribute_name)
                        attribute_value = ability_attributes[index1][index2]
        if attribute_value == None:
            raise ValueError('Attribute does not exist!')                           #if both loops ended and not found, raise error
        return attribute_value

    def targeted(skill, target):
        #this works for the simplest abilities, i.e ones that do the same effect on each unit that Ability.targeted() calls on 
        if Ability.get_attr(skill,"DMG_BOOL"):
            x, y = Ability.calc_damage_range(skill)
            damage_dealt = randint(x,y)
            print("You used " + skill)
            Ability.damage_target(damage_dealt,target)
        if Ability.get_attr(skill,"HEAL") != 0:
            print("LOTSA HEALING")
        
    def calc_damage_range(s):
        return (Ability.get_attr(s,"DMG_BASE") - Ability.get_attr(s,"DMG_ROLL"),
                Ability.get_attr(s,"DMG_BASE") + Ability.get_attr(s,"DMG_ROLL"))

    def damage_target(damage_amount, target):
        target.hp -= damage_amount                             #target loses HP
        print("{} took {} damage!\n".format(target.name, damage_amount))
        


            
