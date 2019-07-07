from random import choice
from string import (ascii_lowercase, ascii_uppercase, digits)

def id_generator(size=10, chars = ascii_lowercase + ascii_uppercase + digits):
  return ''.join(choice(chars) for _ in range(size))

def isInt(tester):
  try:
    int(tester)
    return True
  except:
    return False

def getHelpText(choice):
  texts = {
            "backup": "To make backups, use the /backup command. The bot then will take your stored lists and pack them in a .json file and send this one file to you. This function is also currently being developed, so there will be more functions to this soon.",
            "new": "If you want to make a new list, use the /new command or the inline function, type in what title you want and that's it.",
            "permission": "This bot uses a permission system. Per default, nobody except you can modify a list. To change this, you have to press the lower right button (👤) and the ones you want to work on the list needs to press the corresponding link of the list you shared. Please remember that as long as your list is marked as open, anyone with the link/code can join and manipulate it, so remember to close it again :)",
            "share": "Sharing a list is made with the inline function of telegram. you can either use the middle button at the bottom of the list or type @do2bot and the name or the code of your list to find and send it.",
            "support": "This bot is open source and the code is available on GitHub. If you need help with anything or the GitHub link, please join @do2chat and ask the creator :3\n\nIf you want to support me, you can do so by donating a bit via the following link:\nhttps://paypal.me/pools/c/8fWVnNBFaS for one-time donations, use this link.",
            "credits": "Creator: Lunaresk\nCoder: Lunaresk\nHoster: Lunaresk\nProfile Pic: Abdülkadir Coskun\n\nInspired by: @dotobot from @olebedev"
          }
  if choice in texts:
    text = texts[choice]
  else:
    text = "If you need help with something specific, try /help with one of these commands:\n"
    for i in texts.keys():
      text += "\n{0}".format(i)
    text += "\n\nFor example: /help support"
  return text

def rearrangeList(items, sorting):
  sortedIndexes = []
  sortBy = True
  if sorting == "sortDn":
    sortBy = False
  for item in items:
    if item[3] == sortBy:
      sortedIndexes.append(item[0])
  for item in items:
    if not item[3] == sortBy:
      sortedIndexes.append(item[0])
  print(sortedIndexes)
  return sortedIndexes

