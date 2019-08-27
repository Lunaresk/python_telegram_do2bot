from .dbFuncs import getSubItems

class Item:
  def __init__(self, id: int, name: str, done: bool, sub: bool = False):
    self.id = id
    self.name = name
    self.done = done
    self.subitems = []
    subItems = []
    if not sub:
      subItems = getSubItems(id)
    for subItem in subItems:
      self.subitems.append(Item(subItem[0], subItem[2], subItem[3], True))

  def __str__(self):
    return self.name
