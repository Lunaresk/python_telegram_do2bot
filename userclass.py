from sys import getsizeof

class User:
  def __init__(self, id, name, lang = 'en'):
    self.id = id
    self.name = name
    self.lang = lang

  def __eq__(self, other):
    if type(other) == int:
      return self.id == other
    return (type(self) == type(other) and self.id == other.id)

  def __sizeof__(self):
    return getsizeof(self.id) + getsizeof(self.name) + getsizeof(self.lang)

  def __str__(self) -> str:
    return "[{0}](tg://user?id={1})".format(self.name, self.id)
