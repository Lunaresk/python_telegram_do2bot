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
      coworkers = getCoworkers()
#TODO      self.coworkers = coworkers
#TODO      self.items = items

  def headstr(self) -> str:
    text = u"📋 {0}, 🔗[/{1}](https://telegram.me/do2bot?start={1}), 👥 {2}".format(self.name, self.id, self.owner.linkedString())
    for coworker in self.coworkers:
      text += u", [{0}](tg://user?id={1})".format(coworker.name, coworker.id)
    return text
