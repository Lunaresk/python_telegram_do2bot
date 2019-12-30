from telegram.utils.helpers import mention_markdown
from sys import getsizeof


class User:
    def __init__(self, id, name, lang='en'):
        self.id = id
        self.name = name
        self.lang = lang

    def __eq__(self, other):
        if type(other) == int:
            return self.id == other
        return type(self) == type(other) and self.id == other.id

    def __sizeof__(self):
        return getsizeof(self.id) + getsizeof(self.name) + getsizeof(self.lang)

    def __str__(self) -> str:
        return mention_markdown(self.id, self.name)

#    def __getattr__(self, item):
#        if item == "id":
#            return self.id
#        elif item == "name":
#            return self.name
#        elif item == "lang":
#            return self.lang
#        else:
#            raise ValueError("{0} not in class".format(item))
