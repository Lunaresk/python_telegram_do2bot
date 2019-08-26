from .dbFuncs import getSubItems

class Item:
  def __init__(self, id: int, name: str, done: bool, sub: bool = False):
    self.id = id
    self.name = name
    self.done = done
    subItems = []
    if not sub:
      subItems = getSubItems(id)
    if len(subItems) > 0:
    self.subitems = []
      for subItem in subItems:
        self.subitems.append(Item())
