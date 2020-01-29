from telegram import (InlineKeyboardButton, InlineKeyboardMarkup)

from ..dbFuncs import (getInlineMessages, isOpen)


class Keyboard:
    ListFooterNames = ["Check", "Options", "Remove", "Exit", "CheckSub"]
    ListFooter = {ListFooterNames[0]: 'c', ListFooterNames[1]: 'o', ListFooterNames[2]: 'r', ListFooterNames[3]: 'e',
                  ListFooterNames[4]: 's'}
    ManagerOptionsNames = ["{0}", "✅⬆", "✅⬇", "Backup", "Delete List", "Notifications", "↩"]
    ManagerOptions = {ManagerOptionsNames[0]: 'open', ManagerOptionsNames[1]: "sortUp",
                      ManagerOptionsNames[2]: "sortDn", ManagerOptionsNames[3]: "backup",
                      ManagerOptionsNames[4]: "delete", ManagerOptionsNames[5]: "notify",
                      ManagerOptionsNames[-1]: "back"}
    MemberOptions = -2
    Settings = {"Language": 'lang', "Notifications": 'noti'}
    patterns = ["user", "admi", "sett", "lang"]

    @staticmethod
    def listKeyboard(todolist, user):
        list_footer = Keyboard.ListFooter
        code, items = todolist.id, todolist.items
        keyboard = []
        pattern = Keyboard.patterns[0]
        for item in items:
            temp = "◻"
            if item.done:
                temp = "✅"
            keyboard.append([InlineKeyboardButton(
                text="{0} {1}{2}".format(temp, item.name[:250], ''.join(["⠀" for _ in range(250 - len(item.name))])),
                callback_data=pattern + u":{0}_{1}_{2}".format(code, list_footer["Check"], item.id))])
            for subitem in item.subitems[:-1]:
                temp2 = "├◻"
                if subitem.done:
                    temp2 = "├✅"
                keyboard.append([InlineKeyboardButton(text="{0} {1}{2}".format(temp2, subitem.name[:249], ''.join(
                    ["⠀" for _ in range(249 - len(subitem.name))])),
                                                      callback_data=pattern + u":{0}_{1}_{2}".format(code, list_footer[
                                                          "CheckSub"], subitem.id))])
            if item.subitems:
                subitem = item.subitems[-1]
                temp2 = "└◻"
                if subitem.done:
                    temp2 = "└✅"
                keyboard.append([InlineKeyboardButton(text="{0} {1}{2}".format(temp2, subitem.name[:249], ''.join(
                    ["⠀" for _ in range(249 - len(subitem.name))])),
                                                      callback_data=pattern + u":{0}_{1}_{2}".format(code, list_footer[
                                                          "CheckSub"], subitem.id))])
        if todolist.manager == user:
            keyboard.append([InlineKeyboardButton(text="🗑", callback_data=pattern + u":{0}_{1}".format(code,
                                                                                                        list_footer[
                                                                                                            "Remove"])),
                             InlineKeyboardButton(text="{0}".format(len(getInlineMessages(code))),
                                                  switch_inline_query=code),
                             InlineKeyboardButton(text="⚙", callback_data=pattern + ":{0}_{1}".format(code, list_footer[
                                 "Options"]))])
        elif user in todolist.members:
            keyboard.append([InlineKeyboardButton(text="🗑", callback_data=pattern + u":{0}_{1}".format(code,
                                                                                                        list_footer[
                                                                                                            "Remove"])),
                             InlineKeyboardButton(text="🏃",
                                                  callback_data=pattern + ":{0}_{1}".format(code,
                                                                                            list_footer["Exit"])),
                             InlineKeyboardButton(text="⚙", callback_data=pattern + ":{0}_{1}".format(code, list_footer[
                                 "Options"]))])
        if len(keyboard) == 0:
            keyboard.append([InlineKeyboardButton(text="➕", url="https://telegram.me/do2bot?start={0}".format(code))])
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def managerKeyboard(code):
        manager_options, pattern = dict(Keyboard.ManagerOptions), Keyboard.patterns[1]
        for key, value in manager_options.items():
            manager_options[key] = str(code) + "_" + value
        keyboard = [[]]
        keyboard[-1].append(InlineKeyboardButton(text=("👥" if isOpen(code) else "👤"),
                                                 callback_data=pattern + u":{0}".format(
                                                     manager_options.pop(Keyboard.ManagerOptionsNames[0]))))
        keyboard.extend(Keyboard.customKeyboard(manager_options, pattern, k=2))
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def memberKeyboard(code):
        member_options, pattern, member_border = dict(Keyboard.ManagerOptions), Keyboard.patterns[1],\
                                                  Keyboard.MemberOptions
        for key in dict(member_options):
            if key not in Keyboard.ManagerOptionsNames[member_border:]:
                member_options.pop(key)
        for key, value in member_options.items():
            member_options[key] = str(code) + "_" + value
        return InlineKeyboardMarkup(Keyboard.customKeyboard(member_options, pattern))

    @staticmethod
    def settingsKeyboard():
        settings = {"Language": 'lang', "Notifications": 'noti'}
        return InlineKeyboardMarkup(Keyboard.customKeyboard(settings, Keyboard.patterns[2]))

    @staticmethod
    def languageKeyboard():
        languages = {"English": 'en'}
        return InlineKeyboardMarkup(Keyboard.customKeyboard(languages, Keyboard.patterns[3]))

    @staticmethod
    def customKeyboard(dictionary: dict, pattern, k=3):
        keyboard = [[]]
        for i in dictionary:
            if k <= 0:
                keyboard.append([])
                k = 3
            keyboard[-1].append(InlineKeyboardButton(text=i, callback_data=pattern + u":{0}".format(dictionary[i])))
            k -= 1
        return keyboard

    @staticmethod
    def tempKeyboard():
        return InlineKeyboardMarkup([[InlineKeyboardButton(text="Loading...", callback_data=" ")]])
