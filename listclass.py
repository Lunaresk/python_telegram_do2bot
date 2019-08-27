from .itemclass import Item
from .userclass import User
from .dbFuncs import (getList, getItems, getCoworkers)

class List:
  def __init__(self, id):
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
