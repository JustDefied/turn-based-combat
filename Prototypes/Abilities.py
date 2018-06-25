"""
This class currently does not create its own objects #will it need to for buffs/debuffs/DoT abilities?
Contains all info about abilities
All methods that are considered related to  particular abilities/moves should also be kept here.

Unit.choose_target() will call Ability.targeted(skill, target), which will call the needed methods.
All combat calculations and Unit attribute modifications (except initial mana cost) will be handled here.

Abilities (moves) should follow this format:

( "NAME", ["TARGET_TYPE", "TARGET_TEAM"],["DMG_BASE", "DMG_ROLL"], "MP", "HEAL"                     ####SUBJECT TO CHANGE ACCORDING TO THE NEEDS OF CREATED ABILITIES

TARGET [0]:
    TARGET_TYPE [0]     - (int) 0 = self,       1 = single,     2 = multiple,   3 =  all
    TARGET_TEAM [1]     - (int) 0 = own team,   1 = enemy team (ignore if TARGET_TYPE = self)
DAMAGE [1]:
    DMG_BASE [0]         - (int) base damage is added onto unit's attack stat
    DMG_ROLL [1]         - (int) amount by which base damage may vary each way,
                                i.e. DMG_BASE ± DMG ROLL = Damage range (0 for just base dmg) 
MP [2]              - (int) MP required (0 for none)
HEAL [3]            - (int) HP healed (0 for none)

"""
from collections import OrderedDict
import time
from random import randint

class Ability():

    attribute_list = [["TARGET_TYPE", "TARGET_TEAM"],["DMG_BASE", "DMG_ROLL"], "MP", "HEAL"]            #get_attr() relies completely on the indexes of this list to work
                                                                                                        #
    abilityDict = OrderedDict((                                                                         #this is where all abilities are currently stored
        ('Punch',       [[1,1], [10,2], 0, 0]),                                                         #To use an ability, it will have to be added to a unit's moveList
        ('Kick',        [[1,1], [11,3], 2, 0]),                                                             #abilities that aren't simple will need their own method/code

        ('Magic bolt',  [[1,1], [15,1], 6, 0]),
        ('Heal',        [[0], 0, 8, 10]),

        ('Leech',       [[1,1], [8, 4], 5, 0]),
        ('Triple Kick', [[1,1], [8,2], 6, 0]),

        ('Big kick',       [[1,1,3], [15,12], 5, 0])

    ))
    
    def __init__(self):       
        pass

    #using an ability name(str) and attribute name (str), get an ability's attribute's value from abilityDict
    def get_attr(skill_name, attribute_name):
        ability_attributes = Ability.abilityDict[skill_name]            #a list containing attributes' values of a particular skill
        if attribute_name in Ability.attribute_list:
            index = Ability.attribute_list.index(attribute_name)
            return ability_attributes[index]
        else:
            for attributes in Ability.attribute_list:                               #for each attribute LIST in ability attributes, e.g. ["TARGET_TYPE", "TARGET_TEAM"]
                if isinstance(attributes, list):                                    #
                    if attribute_name in attributes:                                    #if attribute is found in this list
                        index1 = Ability.attribute_list.index(attributes)                   #get attribute LIST 
                        index2 = Ability.attribute_list[index1].index(attribute_name)
                        return ability_attributes[index1][index2]
            raise ValueError('Attribute does not exist!')                           #if loop ended and not found, raise error
            

		
    def targeted(skill, target):
        #this works for the simplest attacks
        x, y = Ability.calc_damage_range(skill)
        damage_dealt = randint(x,y)
        print("You used " + skill)
        Ability.damage_target(damage_dealt,target)
        
    def calc_damage_range(s):
        return (Ability.get_attr(s,"DMG_BASE") - Ability.get_attr(s,"DMG_ROLL"),
                Ability.get_attr(s,"DMG_BASE") + Ability.get_attr(s,"DMG_ROLL"))

    def damage_target(damage_amount, target):
        target.hp -= damage_dealt                             #target loses HP
        print("{} took {} damage!\n".format(target.name, damage_dealt))
        


            
