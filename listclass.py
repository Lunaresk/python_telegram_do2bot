from sys import getsizeof
from .itemclass import Item
from .userclass import User
from .dbFuncs import (getList, getItems, getCoworkers, codeInDB, insertList)
from .helpFuncs import id_generator

class List:
  def __init__(self, id = "D2AwdfuybG"):
    listdetails = getList(id)
    if listdetails:
      self.id = listdetails[0]
      self.name = listdetails[1]
      self.owner = User(listdetails[2], listdetails[3])
      self.coworkers = []
      self.items = []
      coworkers = getCoworkers(self.id)
      for coworker in coworkers:
        self.coworkers.append(User(coworker[1], coworker[2]))
      items = getItems(self.id)
      for item in items:
        self.items.append(Item(item[0], item[2], item[3]))

  def __str__(self) -> str:
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
    for i in range(10):
      code = id_generator()
      if not codeInDB(code):
        break
    if codeInDB(code):
      raise NameError(_("notcreated"))
    insertList(code, name, owner, ownerName)
    return List(code)

  def upload(self):
    pass #TODO
