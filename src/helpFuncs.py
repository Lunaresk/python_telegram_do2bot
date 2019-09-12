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

def getHelpText(choice, _):
  texts = ["backup", "credits", "limitations", "new", "permission", "settings", "share", "sublist", "support"]
  if choice == "":
    return _("help")
  elif choice == "backup":
    return _("helpbackup")
  elif choice == "credits":
    return _("helpcredits")
  elif choice == "limitations":
    return _("helplimitations")
  elif choice == "new":
    return _("helpnew")
  elif choice == "permission":
    return _("helppermission")
  elif choice == "settings":
    return _("helpsettings")
  elif choice == "share":
    return _("helpshare")
  elif choice == "sublist":
    return _("helpsublist")
  elif choice == "support":
    return _("helpsupport")
  else:
    text = _("helpcommands1")
    for i in texts:
      text += "\n{0}".format(i)
    text += _("helpcommands2")
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
  return sortedIndexes

