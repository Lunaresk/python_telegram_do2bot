class User:
  def __init__(self, id, name):
    self.id = id
    self.name = name

  def linkedString(self) -> str:
    return "[{0}](tg://user?id={1})".format(self.name, self.id)
