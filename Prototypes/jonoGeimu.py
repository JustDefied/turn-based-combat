
# Global Character Statistics
playerChar = {'HP':200, 'MP':70, 'STR':2, 'INT':5} 
enemyChar = {'HP':100, 'Crit': 0.02, 'Drop': 0.2}

def main():
  # Print GUI & Recieve User Input
  user_input = print_gui(playerChar, enemyChar)

  # Process User Input
  game_action(user_input)

  # Main Game Loop
  if playerChar['HP'] <= 0:
    print("----------------------------------------")
    print("u suck")
  elif enemyChar['HP'] <= 0:
    print("----------------------------------------")
    print("gub job u win")
  else:
    main()

def print_gui(playerChar, enemyChar):
  print("====================")
  print("ENEMY HP : " + str(enemyChar.get('HP')))
  print("--------------------")
  print("YOUR HP : " + str(playerChar.get('HP')))
  print("YOUR MP : " + str(playerChar.get('MP')))
  print("==================== \n")
  print("Type the number of your action and press ENTER:")
  print("1. Attack")
  print("2. Spell (15 MP)")
  print("3. Nothing \n")
  user_input = input("=>") 
  return user_input

def game_action(user_input):
  if user_input == "1":
    enemyChar['HP'] -= 10
    playerChar['HP'] -= 10
  elif user_input == "2":
    enemyChar['HP'] -= 30
    playerChar['HP'] -= 10
    playerChar['MP'] -= 15
  elif user_input == "3":
    playerChar['HP'] -= 10

main()
