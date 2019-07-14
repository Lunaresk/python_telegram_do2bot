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

def getHelpText(choice, texts):
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

