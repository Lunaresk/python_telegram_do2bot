from sys import getsizeof
from threading import Thread

from ..dbFuncs import (codeInDB, editItems as dbeditItems, getList, getItems, getItemsByEdit, getTopItemByEdit,
                       getSubItemsByEdit, getCoworkers, getCoworkerMessage, getCoworkerMessages,
                       getInlineMessages as dbgetInlineMessages, getOwnerMessage, insertCoworker, insertList,
                       removeCoworker, removeItems, removeList)
from ..helpFuncs import id_generator
from .itemclass import Item
from .userclass import User


class Todolist:
    def __init__(self, id="", name="", owner=0, ownername=""):
        self.members = []
        self.items = []
        if name and owner and ownername:
            self.id = id
            self.name = name
            self.manager = User(owner, ownername)
        else:
            listdetails = getList(id)
            if listdetails:
                self.id = listdetails[0]
                self.name = listdetails[1]
                self.manager = User(listdetails[2], listdetails[3])
                members = getCoworkers(self.id)
                for coworker in members:
                    self.members.append(User(coworker[1], coworker[2]))
                items = getItems(self.id)
                for item in items:
                    self.items.append(Item(item[0], item[2], item[3]))
            else:
                raise KeyError(("notexisting"))

    def __eq__(self, other):
        if type(other) == str:
            return other == self.id
        return (type(self) == type(other) and self.id == other.id)

    def __iter__(self):
        return ListIterator(self)

    def __repr__(self) -> str:
        text = u"📋 {0}, 🔗[/{1}](https://telegram.me/do2bot?start={1}), 👥 {2}".format(self.name, self.id,
                                                                                        str(self.manager))
        for coworker in self.members:
            text += ", " + str(coworker)
        return text

    def __sizeof__(self) -> int:
        total = getsizeof(self.id) + getsizeof(self.name) + getsizeof(self.manager)
        for coworker in self.members:
            total += getsizeof(coworker)
        for item in self.items:
            total += getsizeof(item)
        return total

    def __str__(self) -> str:
        text = u"📋 {0}, 🔗/{1}, 👥 {2}".format(self.name, self.id, str(self.manager))
        for coworker in self.members:
            text += ", " + str(coworker)
        return text

    def addCoworker(self, coworker, coname, msgid):
        self.members.append(User(coworker, coname))
        dbfunc = Thread(target=insertCoworker, args=(self.id, coworker, coname, msgid))
        dbfunc.start()

    def addItems(self, items, fromuser, message, line=0):
        for item in items:
            if len(self.items) + sum([len(x.subitems) for x in self.items]) < 20:
                self.items.append(Item.new(self.id, item, fromuser, message, line))
                line += 1
            else:
                raise StopIteration("Too many items")

    def addSubItems(self, topitem, items, fromuser, message, line=0):
        itemindex = self.items.index(topitem)
        for item in items:
            if len(self.items) + sum([len(x.subitems) for x in self.items]) < 20:
                self.items[itemindex].newSub(item, fromuser, message, line)
                line += 1
            else:
                raise StopIteration("Too many items")

    def anyItemChecked(self):
        checked = False
        for item in self.items:
            if item.subitems:
                for subitem in item.subitems:
                    if subitem.done:
                        checked = True
                        break
            if item.done:
                checked = True
            if checked:
                break
        return checked

    def deleteCoworker(self, id):
        try:
            place = self.members.index(id)
        except ValueError as error:
            return False
        coworker = self.members.pop(place)
        dbfunc = Thread(target=removeCoworker, args=(self.id, coworker.id))
        dbfunc.start()

    def deleteDones(self):
        for item in self.items[:]:
            if item.done:
                self.items.pop(self.items.index(item))
            if item.subitems:
                for subitem in item.subitems[:]:
                    if subitem.done:
                        item.subitems.pop(item.subitems.index(subitem))
        dbfunc = Thread(target=removeItems, args=(self.id,))
        dbfunc.start()

    def deleteList(self):
        removeList(self.id)

    def difference(self, other):
        if type(self) != type(other):
            raise TypeError("Type mismatch")
        changes = ["Changes in /{0}".format(self.id)]
        if self.name != other.name:
            changes.append("Name changed: '{1}' -> '{2}'".format(other.id, self.name, other.name))
        if self.manager != other.manager:
            changes.append("New manager: '{1}' -> '{2}'".format(other.id, self.manager, other.manager))
        for selfitem in self.items:
            try:
                otheritem = other.items[other.items.index(selfitem)]
            except ValueError as error:
                changes.append("➖ {0}".format(selfitem.name))
            else:
                if otheritem.name != selfitem.name:
                    changes.append("Item name changed: '{0}' -> '{1}'".format(selfitem.name, otheritem.name))
                if otheritem.done != selfitem.done:
                    ticked = ["◻", "✅"]
                    changes.append("{0} {1}".format(ticked[otheritem.done], otheritem.name))
        for otheritem in other.items:
            if otheritem not in self.items:
                changes.append("➕ {0}".format(otheritem.name))
        for selfworker in self.members:
            try:
                otherworker = other.members[other.members.index(selfworker)]
            except ValueError as error:
                changes.append("Left the List: {0}".format(selfworker.name))
            else:
                if otherworker.name != selfworker.name:
                    changes.append("Member name changed: '{0}' -> '{1}'".format(selfworker.name, otherworker.name))
        for otherworker in other.members:
            if otherworker not in self.members:
                changes.append("Member joined: {0}".format(otherworker.name))
        return changes

    # TODO revision needed
    def editItems(self, newItems, userID, messageID):
        topItem = getTopItemByEdit(userID, messageID)
        if topItem:
            itemindex = self.items.index(topItem)
            oldItems = getSubItemsByEdit(userID, messageID)
            for i in range(len(oldItems))[::-1]:
                subindex = self.items[itemindex].subitems.index(oldItems[i][0])
                try:
                    self.items[itemindex].subitems[subindex].name = newItems[i]
                except:
                    del self.items[itemindex].subitems[subindex]
            if len(oldItems) < len(newItems):
                self.addSubItems(topItem, newItems[len(oldItems):], userID, messageID, len(oldItems))
        else:
            oldItems = getItemsByEdit(userID, messageID)
            for i in range(len(oldItems))[::-1]:
                itemindex = self.items.index(oldItems[i][0])
                try:
                    self.items[itemindex].name = newItems[i]
                except:
                    del self.items[itemindex]
            if len(oldItems) < len(newItems):
                self.addItems(newItems[len(oldItems):], userID, messageID, len(oldItems))
        dbeditItems(newItems, userID, messageID)

    def getMessage(self):
        return getOwnerMessage(self.id)[0]

    def getCoMessage(self, id):
        return getCoworkerMessage(self.id, id)

    def getCoMessages(self):
        return getCoworkerMessages(self.id)

    def getInlineMessages(self):
        return dbgetInlineMessages(self.id)

    @staticmethod
    def new(name: str, owner: int, owner_name: str):
        """Creates a new list and stores the details in the database.

    Arguments:
    name -- the title of the list, must not be longer than 100 characters.
    owner -- the telegram id of the owner.
    ownerName -- the name of the owner.

    Returns: A new object of type 'List'.
    """
        if len(name) > 64:
            raise OverflowError(("nametoolong"))
        accepted = False
        try:
            for i in range(10):
                code = id_generator()
                if not codeInDB(code):
                    accepted = True
                    break
            if not accepted:
                raise NameError(("notcreated"))
        except NameError as e:
            pass
        else:
            dbfunc = Thread(target=insertList, args=(code, name, owner, owner_name))
            dbfunc.start()
            return Todolist(code, name, owner, owner_name)

    def toggleItem(self, id):
        try:
            place = self.items.index(id)
        except ValueError as error:
            return False
        self.items[place].toggle()
        return True

    def toggleSubItem(self, id):
        for place, value in enumerate(self.items):
            if id in value.subitems:
                break
        try:
            subplace = self.items[place].subitems.index(id)
        except ValueError as error:
            return False
        else:
            self.items[place].subitems[subplace].toggle()
            return True


class ListIterator:
    def __init__(self, _list):
        self._list = _list
        self._index = 0

    def __next__(self):
        if self._index == 0:
            temp = self._list.name
        elif self._index == 1:
            temp = self._list.manager.id
        elif self._index == 2:
            temp = self._list.manager.name
        elif self._index == 3:
            temp = []
            for item in self._list.items:
                temp.append(list(item))
        else:
            raise StopIteration
        self._index += 1
        return temp
