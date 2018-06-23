"""
Abilities (moves) should follow this format:

"name", [[TARGET_TYPE, TARGET_TEAM, TARGET_NUM], DMG, MP, HEAL]

TARGET [0]:
    TARGET_TYPE [0]     - (int) 0 = self,       1 = single,     2 = multiple,   3 =  all
    TARGET_TEAM [1]     - (int) 0 = own team,   1 = enemy team (ignore if TARGET_TYPE = self)
    TARGET_NUM  [2]     - (int) Number of targets if TARGET_TYPE = 2
DMG [1]             - (int) Damage done
MP [2]              - (int) MP required (0 for none)
HEAL [3]            - (int) HP healed





('Punch',       [[1,1], randint(8,12), 0, 0]),
('Kick',        [[1,1], randint(7,14), 2, 0]),


('Magic bolt',  [[1,1], randint(11,16), 6, 0]),
('Heal',        [[0], 0, 8, 10]),

('Leech',       [[1,1], randint(6,10), 5, 0]),
('Triple Kick', [[1,1], randint(5,15), 6, 0]),
