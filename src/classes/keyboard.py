from telegram import (InlineKeyboardButton, InlineKeyboardMarkup)

from ..dbFuncs import (getInlineMessages, isOpen)

class Keyboard:
  ListFooterNames = ["Check", "Options", "Remove", "Exit", "CheckSub"]
  ListFooter = {ListFooterNames[0]: 'c', ListFooterNames[1]: 'o', ListFooterNames[2]: 'r', ListFooterNames[3]: 'e', ListFooterNames[4]: 's'}
  OwnerOptions, UserOptions = OrderedDict(), OrderedDict()
  OwnerOptionsNames = ["{0}", "✅⬆", "✅⬇", "Backup", "Delete List", "Notifications", "↩"]
  temp = [["{0}", 'open'], ["✅⬆", "sortUp"], ["✅⬇", "sortDn"], ["Backup", "backup"], ["Delete List", "delete"], ["Notifications", "notify"], ["↩", "back"]]
  for k, v in temp:
    OwnerOptions[k] = v
  temp = [["Notifications", "notify"], ["↩", "back"]]
  for k, v in temp:
    UserOptions[k] = v
  del temp
  OptionsOrder = ["{0}", "✅⬆", "✅⬇", "Backup", "Delete List", "↩"]
  Options = {OptionsOrder[0]: "open", OptionsOrder[1]: "sortUp", OptionsOrder[2]: "sortDn", OptionsOrder[3]: "backup", OptionsOrder[4]: "delete", OptionsOrder[-1]: "back"}
  UserOptions = []
  Settings = {"Language": 'lang', "Notifications": 'noti'}
  patterns = ["user", "admi", "sett", "lang"]

  def listKeyboard(todolist, user):
    ListFooter = Keyboard.ListFooter
    code, items = todolist.id, todolist.items
    keyboard = []
    pattern = Keyboard.patterns[0]
    for item in items:
      temp = "◻"
      if item.done == True:
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
      keyboard.append([InlineKeyboardButton(text = "🗑", callback_data = pattern + u":{0}_{1}".format(code, ListFooter["Remove"])),
        InlineKeyboardButton(text = "{0}".format(len(getInlineMessages(code))), switch_inline_query = code),
        InlineKeyboardButton(text = "⚙", callback_data = pattern + ":{0}_{1}".format(code, ListFooter["Options"]))])
    elif user in todolist.coworkers:
      keyboard.append([InlineKeyboardButton(text = "🗑", callback_data = pattern + u":{0}_{1}".format(code, ListFooter["Remove"])),
        InlineKeyboardButton(text = "🏃", callback_data = pattern + ":{0}_{1}".format(code, ListFooter["Exit"]))])
    if len(keyboard) == 0:
      keyboard.append([InlineKeyboardButton(text = "➕", url = "https://telegram.me/do2bot?start={0}".format(code))])
    return InlineKeyboardMarkup(keyboard)

  def managerKeyboard(code):
    OwnerOptions, pattern = OrderedDict(Keyboard.OwnerOptions), Keyboard.patterns[1]
    for key, value in OwnerOptions:
      OwnerOptions[key] = str(code)+"_"+value
    keyboard = [[]]
    keyboard[-1].append(InlineKeyboardButton(text = ("👥" if isOpen(code) else "👤"), callback_data = pattern + u":{0}".format(OwnerOptions.popitem(last = False)[1])))
    keyboard.extend(Keyboard.customKeyboard(OwnerOptions, pattern, k=2))
    return InlineKeyboardMarkup(keyboard)

  def memberKeyboard(code):
    pass

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
