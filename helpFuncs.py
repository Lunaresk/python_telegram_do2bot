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
  if choice == "":
    return _("To create a new list, use /new. Then enter a title for this list. When you're done, you can send a list of things here and this bot will insert it to the list.\n"
             "The lower right button on the owner's list indicates whether the list is open or not. Only the owner can switch if the list is open."
             " When open, other people who enters the unique code of your list will be added as operator for your list."
             " This will grant them the possibility to add items to the list and recall the list with the inline function.\n\n"
             "If you need help with something specific, try this one out: `/help commands`\n\n"
             "This bot is usable via inline mode. To see a list of your current lists, just type the bots name in the chat like '`@do2bot `'.")
  elif choice == "backup":
    return _("To make backups, use the /backup command. The bot then will take your stored lists and pack them in a .json file and send this one file to you."
             " This function is also currently being developed, so there will be more functions to this soon.")
  elif choice == "credits":
    return _("Creator: Lunaresk\nCoder: Lunaresk\nHoster: Lunaresk\nProfile Pic: Abdülkadir Coskun\n\nInspired by: @dotobot from @olebedev")
  elif choice == "limitations":
    return _("Due to the way Telegram creates and limits inline buttons, there can't be displayed more than 23 rows of buttons."
             " Therefore, I restricted the items per list to a maximum of 20 items.")
  elif choice == "new":
    return _("If you want to make a new list, use the /new command or the inline function, type in what title you want and that's it.")
  elif choice == "permission":
    return _("This bot uses a permission system. Per default, nobody except you can modify a list."
             " To change this, you have to go to the list settings and press the upper left button (👤)"
             " and the ones you want to work on the list needs to press the corresponding link of the list you shared."
             " Please remember that as long as your list is marked as open, anyone with the link/code can join and manipulate it, so remember to close it again :)")
  elif choice == "settings":
    return _("👤 means, that the list is currently closed and usage is restricted to the owner and users, who already joined the list."
             " Pushing this button will open the list for everyone and will change the icon to 👥.\n"
             "✅⬆ and ✅⬇ will reorder already done tasks to the top/bottom of the list, respectively.\n"
             "↩ to go back to the list.")
  elif choice == "share":
    return _("Sharing a list is made with the inline function of telegram."
             " You can either use the middle button at the bottom of the list or type @do2bot and the name or the code of your list to find and send it.")
  elif choice == "sublist":
    return _("To create a sublist, you have to insert a single item first. Then, reply to this message you just sent and the items will be inserted as subitems for the previously inserted item."
             " Please note! Subitems are under the same restrictions as stated in '/help limitations'.")
  elif choice == "support":
    return _("This bot is open source and the code is available on GitHub. If you need help with anything or the GitHub link, please join @do2chat and ask the creator :3\n\n"
             "If you want to support me, you can do so by donating a bit via the following link:\nhttps://paypal.me/pools/c/8fWVnNBFaS for one-time donations.")
  else:
    text = _("If you need help with something specific, try /help with one of these commands:\n")
    for i in texts.keys():
      text += "\n{0}".format(i)
    text += _("\n\nFor example: /help support")
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

