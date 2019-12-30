from .keyboard import Keyboard
from ..dbFuncs import (getJoinStatus, getNotifyByUser)


class Message:
    def __init__(self, text="", keyboard=None):
        self.text = text
        self.keyboard = keyboard

    def createInlineListMessage(self, todolist):
        self.text = repr(todolist)
        self.keyboard = Keyboard.listKeyboard(todolist, -1)

    def createManagerSettingsMessage(self, todolist):
        self.text = Message.settingsText(todolist)
        self.keyboard = Keyboard.managerKeyboard(todolist.id)

    def createMemberSettingsMessage(self, todolist):
        self.text = Message.settingsText(todolist)
        self.keyboard = Keyboard.memberKeyboard(todolist.id)

    def createUserListMessage(self, todolist, user):
        self.text = str(todolist)
        self.keyboard = Keyboard.listKeyboard(todolist, user)

    @staticmethod
    def inlineListMessage(todolist):
        return Message(repr(todolist), Keyboard.listKeyboard(todolist, -1))

    @staticmethod
    def managerSettingsMessage(todolist):
        return Message(Message.settingsText(todolist), Keyboard.managerKeyboard(todolist.id))

    @staticmethod
    def memberSettingsMessage(todolist):
        return Message(Message.settingsText(todolist), Keyboard.memberKeyboard(todolist.id))

    @staticmethod
    def userListMessage(todolist, user):
        return Message(str(todolist), Keyboard.listKeyboard(todolist, user))

    @staticmethod
    def settingsText(todolist):
        text = "ID: /{0}".format(str(todolist.id))
        text += "\nManager: {0}".format(str(todolist.manager))
        if todolist.members:
            text += "\nMembers: {0}".format(str(todolist.members[0]))
        for member in todolist.members[1:]:
            text += str(member)
        joinStatus = getJoinStatus(todolist.id)
        text += "\nNotifications: {0}".format(
            str(True) if getNotifyByUser(todolist.owner.id, todolist.id) else str(False))
        text += "\n\nCan people join the list: {0}".format("Open" if joinStatus == True else "Closed")
        text += "\nWho can check/uncheck items: "
        if joinStatus == True:  # have to rewrite soon from this point on
            text += "Everyone"
        else:
            text += "Members and Manager"
        text += "\nWho can add/remove items: "
        if joinStatus == True:
            text += "Everyone"
        else:
            text += "Members and Manager"
        return text