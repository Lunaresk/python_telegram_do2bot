from .dbFuncs import (getSubItems, updateItem)
from sys import getsizeof

class Item:
  def __init__(self, id: int, name: str, done: bool, sub: bool = False):
    self.id = id
    self.name = name
    self.done = done
    self.issub = sub
    self.subitems = []
    subItems = []
    if not sub:
      subItems = getSubItems(id)
    for subItem in subItems:
      self.subitems.append(Item(subItem[0], subItem[2], subItem[3], True))

  def __str__(self):
    return self.name

  def __sizeof__(self):
    total = getsizeof(self.id) + getsizeof(self.name) + getsizeof(self.done) + getsizeof(self.issub)
    for subitem in self.subitems:
      total += getsizeof(subitem)
    return total

  def toggle(self):
    self.done = not self.done
    for subitem in self.subitems:
      subitem.done = self.done
    updateItem(self.id, self.done)
