from sys import getsizeof
from threading import Thread
from .itemclass import Item
from .userclass import User
from .dbFuncs import (codeInDB, getList, getItems, getCoworkers, getCoworkerMessage, getCoworkerMessages, getInlineMessages as dbgetInlineMessages, getOwnerMessage, insertCoworker, insertList, removeCoworker, removeItems, removeList)
from .helpFuncs import id_generator

class List:
  def __init__(self, id = "", name = "", owner = 0, ownername = ""):
    self.coworkers = []
    self.items = []
    if name and owner and ownername:
      self.id = id
      self.name = name
      self.owner = User(owner, ownername)
    else:
      listdetails = getList(id)
      if listdetails:
        self.id = listdetails[0]
        self.name = listdetails[1]
        self.owner = User(listdetails[2], listdetails[3])
        coworkers = getCoworkers(self.id)
        for coworker in coworkers:
          self.coworkers.append(User(coworker[1], coworker[2]))
        items = getItems(self.id)
        for item in items:
          self.items.append(Item(item[0], item[2], item[3]))
      else:
        raise KeyError(_("notexisting"))

  def __eq__(self, other):
    if type(other) == str:
      return other == self.id
    return (type(self) == type(other) and self.id == other.id)

  def __iter__(self):
    return ListIterator(self)

  def __repr__(self) -> str:
    text = u"📋 {0}, 🔗[/{1}](https://telegram.me/do2bot?start={1}), 👥 {2}".format(self.name, self.id, str(self.owner))
    for coworker in self.coworkers:
      text += ", " + str(coworker)
    return text

  def __sizeof__(self) -> int:
    total = getsizeof(self.id) + getsizeof(self.name) + getsizeof(self.owner)
    for coworker in self.coworkers:
      total += getsizeof(coworker)
    for item in self.items:
      total += getsizeof(item)
    return total

  def __str__(self) -> str:
    text = u"📋 {0}, 🔗/{1}, 👥 {2}".format(self.name, self.id, str(self.owner))
    for coworker in self.coworkers:
      text += ", " + str(coworker)
    return text

  def addCoworker(self, coworker, coname, msgid):
    self.coworkers.append(User(coworker, coname))
    dbfunc = Thread(target=insertCoworker, args=(self.id, coworker, coname, msgid))
    dbfunc.start()

  def addItems(self, items, fromuser, message, line = 0):
    for item in items:
      if len(self.items) + sum([len(x.subitems) for x in self.items]) < 20:
        self.items.append(Item.new(self.id, item, fromuser, message, line))
        line += 1
      else:
        raise StopIteration("Too many items")

  def addSubItems(self, topitem, items, fromuser, message, line = 0):
    itemindex = self.items.index(topitem)
    for item in items:
      if len(self.items) + len([x for x in self.items.subitems]) < 20:
        self.items[itemindex].newSub(item, fromuser, message, line)
        line += 1
      else:
        raise StopIteration("Too many items")

  def deleteCoworker(self, id):
    try:
      place = self.coworkers.index(id)
    except ValueError as error:
      return False
    coworker = self.coworkers.pop(place)
    dbfunc = Thread(target=removeCoworker, args=(self.id, coworker.id))
    dbfunc.start()

  def deleteDones(self):
    for place, item in enumerate(self.items):
      if item.done:
        self.items.pop(place)
    dbfunc = Thread(target=removeItems, args=(self.id,))
    dbfunc.start()

  def deleteList(self):
    removeList(self.id)

  def getMessage(self):
    return getOwnerMessage(self.id)[0]

  def getCoMessage(self, id):
    return getCoworkerMessage(self.id, id)

  def getCoMessages(self):
    return getCoworkerMessages(self.id)

  def getInlineMessages(self):
    return dbgetInlineMessages(self.id)

  def new(name: str, owner: int, ownerName: str):
    """Creates a new list and stores the details in the database.

    Arguments:
    name -- the title of the list, must not be longer than 100 characters.
    owner -- the telegram id of the owner.
    ownerName -- the name of the owner.

    Returns: A new object of type 'List'.
    """
    if len(name) > 100:
      raise OverflowError(_("nametoolong"))
    accepted = False
    for i in range(10):
      code = id_generator()
      if not codeInDB(code):
        accepted = True
        break
    if not accepted:
      raise NameError(_("notcreated"))
    dbfunc = Thread(target=insertList, args=(code, name, owner, ownerName))
    dbfunc.start()
    return List(code, name, owner, ownerName)

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
      subplace = self.items.index(id)
    except ValueError as error:
      return False
    self.items[place].subitems[subplace].toggle()
    return True


class ListIterator: #dontfuckit
  def __init__(self, _list):
    self._list = _list
    self._index = 0

  def __next__(self):
    if self._index == 0:
      temp = self._list.name
    elif self._index == 1:
      temp = self._list.owner.id
    elif self._index == 2:
      temp = self._list.owner.name
    elif self._index == 3:
      temp = []
      for item in self._list.items:
        temp.append(list(item))
    else:
      raise StopIteration
    self._index += 1
    return temp
