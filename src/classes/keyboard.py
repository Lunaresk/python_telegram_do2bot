from telegram import (InlineKeyboardButton, InlineKeyboardMarkup)
from ..dbFuncs import (getInlineMessages, isOpen)

class Keyboard:
  ListFooter = {"Check": 'c', "Options": 'o', "Remove": 'r', "Exit": 'e', "CheckSub": 's'}
  OptionsOrder = ["{0}", "✅⬆", "✅⬇", "Backup", "↩"]
  Options = {OptionsOrder[0]: "open", OptionsOrder[1]: "sortUp", OptionsOrder[2]: "sortDn", OptionsOrder[3]: "backup", OptionsOrder[4]: "back"}
  Settings = {"Language": 'lang', "Notifications": 'noti'}
  patterns = ["user", "admi", "sett", "lang"]

  def getListFooter():
    return {"Check": 'c', "Options": 'o', "Remove": 'r', "Exit": 'e', "CheckSub": 's'}

  def getSettings():
    return {"Language": 'lang', "Notifications": 'noti'}

  def getPatterns():
    return ["user", "admi", "sett", "lang"]

  def getOptionsOrder():
    return ["{0}", "✅⬆", "✅⬇", "Backup", "↩"]

  def getOptions():
    OptionsOrder = Keyboard.getOptionsOrder()
    return {OptionsOrder[0]: "open", OptionsOrder[1]: "sortUp", OptionsOrder[2]: "sortDn", OptionsOrder[3]: "backup", OptionsOrder[4]: "back"}

  def userKeyboard(todolist, user):
    ListFooter = Keyboard.ListFooter
    code, items = todolist.id, todolist.items
    keyboard = []
    pattern = Keyboard.patterns[0]
    count = 0
    for item in items:
      temp = "◻"
      if item.done == True:
        count += 1
        temp = "✅"
      keyboard.append([InlineKeyboardButton(text = "{0} {1}{2}".format(temp, item.name[:250], ''.join(["⠀" for _ in range(250-len(item.name))])), callback_data = pattern + u":{0}_{1}_{2}".format(code, ListFooter["Check"], item.id))])
      for subitem in item.subitems[:-1]:
        temp2 = "├◻"
        if subitem.done == True:
          temp2 = "├✅"
        keyboard.append([InlineKeyboardButton(text = "{0} {1}{2}".format(temp2, subitem.name[:249], ''.join(["⠀" for _ in range(249-len(subitem.name))])), callback_data = pattern + u":{0}_{1}_{2}".format(code, ListFooter["CheckSub"], subitem.id))])
      if item.subitems:
        subitem = item.subitems[-1]
        temp2 = "└◻"
        if subitem.done == True:
          temp2 = "└✅"
        keyboard.append([InlineKeyboardButton(text = "{0} {1}{2}".format(temp2, subitem.name[:249], ''.join(["⠀" for _ in range(249-len(subitem.name))])), callback_data = pattern + u":{0}_{1}_{2}".format(code, ListFooter["CheckSub"], subitem.id))])
    if todolist.owner == user:
      temp = "🗑"
      if count == 0 or count == len(items):
        temp = "📥"
      keyboard.append([InlineKeyboardButton(text = temp, callback_data = pattern + u":{0}_{1}".format(code, ListFooter["Remove"])),
        InlineKeyboardButton(text = "{0}".format(len(getInlineMessages(code))), switch_inline_query = code),
        InlineKeyboardButton(text = "⚙", callback_data = pattern + ":{0}_{1}".format(code, ListFooter["Options"]))])
    elif user in todolist.coworkers:
      keyboard.append([InlineKeyboardButton(text = "🏃", callback_data = pattern + ":{0}_{1}".format(code, ListFooter["Exit"]))])
    if len(keyboard) == 0:
      keyboard.append([InlineKeyboardButton(text = "➕", url = "https://telegram.me/do2bot?start={0}".format(code))])
    return InlineKeyboardMarkup(keyboard)

  def adminKeyboard(code, userid):
    Options, OptionsOrder, pattern = dict(Keyboard.Options), Keyboard.OptionsOrder, Keyboard.patterns[1]
    for key in Options:
      Options[key] = str(code)+"_"+Options[key]
    keyboard = [[]]
    keyboard[-1].append(InlineKeyboardButton(text = ("👥" if isOpen(code) else "👤"), callback_data = pattern + u":{0}".format(Options[OptionsOrder[0]])))
    del Options[OptionsOrder[0]]
    keyboard.extend(Keyboard.customKeyboard(Options, pattern, k=2))
    return InlineKeyboardMarkup(keyboard)

  def settingsKeyboard():
    Settings = {"Language": 'lang', "Notifications": 'noti'}
    return InlineKeyboardMarkup(Keyboard.customKeyboard(Settings, Keyboard.patterns[2]))

  def languageKeyboard():
    Languages = {"English": 'en'}
    return InlineKeyboardMarkup(Keyboard.customKeyboard(Languages, Keyboard.patterns[3]))

  def customKeyboard(dictionary, pattern, k = 3):
    keyboard = [[]]
    for i in dictionary:
      if k <= 0:
        keyboard.append([])
        k = 3
      keyboard[-1].append(InlineKeyboardButton(text = i, callback_data = pattern + u":{0}".format(dictionary[i])))
      k-=1
    return keyboard

  def tempKeyboard():
    return InlineKeyboardMarkup([[InlineKeyboardButton(text = "Loading...", callback_data = " ")]])
