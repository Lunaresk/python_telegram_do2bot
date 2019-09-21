from telegram import (InlineKeyboardButton, InlineKeyboardMarkup)
from ..dbFuncs import (getInlineMessages, isOpen)

class Keyboard:
  ListFooter = {"Check": 'c', "Options": 'o', "Remove": 'r', "Exit": 'e', "CheckSub": 's'}
  OptionsOrder = ["{0}", "✅⬆", "✅⬇", "Backup", "↩"]
  Options = {OptionsOrder[0]: "open", OptionsOrder[1]: "sortUp", OptionsOrder[2]: "sortDn", OptionsOrder[3]: "backup", OptionsOrder[4]: "back"}

  def userKeyboard(todolist, user):
    ListFooter = Keyboard.ListFooter
    code, items = todolist.id, todolist.items
    keyboard = []
    count = 0
    for item in items:
      temp = "◻"
      if item.done == True:
        count += 1
        temp = "✅"
      keyboard.append([InlineKeyboardButton(text = "{0} {1}{2}".format(temp, item.name[:250], ''.join(["⠀" for _ in range(250-len(item.name))])), callback_data = u"{0}_{1}_{2}".format(code, ListFooter["Check"], item.id))])
      for subitem in item.subitems:
        subtemp = "├"
        if subitem == item.subitems[-1]:
          subtemp = "└"
        temp2 = "◻"
        if subitem.done == True:
          temp2 = "✅"
        subtemp += temp2
        keyboard.append([InlineKeyboardButton(text = "{0} {1}{2}".format(subtemp, subitem.name[:249], ''.join(["⠀" for _ in range(249-len(subitem.name))])), callback_data = u"{0}_{1}_{2}".format(code, ListFooter["CheckSub"], subitem.id))])
    if todolist.owner == user:
      temp = "🗑"
      if count == 0 or count == len(items):
        temp = "📥"
      keyboard.append([InlineKeyboardButton(text = temp, callback_data = u"{0}_{1}".format(code, ListFooter["Remove"])),
        InlineKeyboardButton(text = "{0}".format(len(getInlineMessages(code))), switch_inline_query = code),
        InlineKeyboardButton(text = "⚙", callback_data = "{0}_{1}".format(code, ListFooter["Options"]))])
    elif user in todolist.coworkers:
      keyboard.append([InlineKeyboardButton(text = "🏃", callback_data = "{0}_{1}".format(code, ListFooter["Exit"]))])
    if len(keyboard) == 0:
      keyboard.append([InlineKeyboardButton(text = "➕", url = "https://telegram.me/do2bot?start={0}".format(code))])
    return InlineKeyboardMarkup(keyboard)

  def adminKeyboard(code, userid):
    Options, OptionsOrder = Keyboard.Options, Keyboard.OptionsOrder
    keyboard = [[]]
    k = 2
    keyboard[-1].append(InlineKeyboardButton(text = OptionsOrder[0].format("👥" if isOpen(code) else "👤"), callback_data = u"{0}_{1}".format(code, Options[OptionsOrder[0]])))
    for i in OptionsOrder[1:]:
      if k == 0:
        keyboard.append([])
        k = 3
      keyboard[-1].append(InlineKeyboardButton(text = i, callback_data = u"{0}_{1}".format(code, Options[i])))
      k-=1
    return InlineKeyboardMarkup(keyboard)

  def tempKeyboard():
    return InlineKeyboardMarkup([[InlineKeyboardButton(text = "Loading...", callback_data = " ")]])


