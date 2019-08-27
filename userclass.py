from sys import getsizeof

class User:
  def __init__(self, id, name):
    self.id = id
    self.name = name

  def __str__(self) -> str:
    return "[{0}](tg://user?id={1})".format(self.name, self.id)

  def __sizeof__(self):
    return getsizeof(self.id) + getsizeof(self.name)
