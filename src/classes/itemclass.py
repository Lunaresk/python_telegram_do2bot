from functools import total_ordering
from sys import getsizeof
from threading import Thread

from ..dbFuncs import (getSubItems, insertSubItem, insertItem, updateItem, updateSubItem)


@total_ordering
class Item:
    def __init__(self, id: int, name: str, done: bool = False, sub: bool = False):
        self.id = id
        self.name = name
        self.done = done
        self.issub = sub
        self.subitems = []
        sub_items = []
        if not sub:
            sub_items = getSubItems(id)
        for subItem in sub_items:
            self.subitems.append(Item(subItem[0], subItem[2], subItem[3], True))

    def __eq__(self, other):
        if type(other) == int:
            return other == self.id
        return type(self) == type(other) and self.issub == other.issub and self.id == other.id

    def __iter__(self):
        return ItemIterator(self)

    def __lt__(self, other):
        if type(self) != type(other):
            raise TypeError("Type mismatch")
        return self.issub == other.issub and self.id < other.id

    def __sizeof__(self):
        total = getsizeof(self.id) + getsizeof(self.name) + getsizeof(self.done) + getsizeof(self.issub)
        for subitem in self.subitems:
            total += getsizeof(subitem)
        return total

    def __str__(self):
        return self.name

    @staticmethod
    def new(code, itemname, fromuser, message, line):
        return Item(insertItem(code, itemname[:255], fromuser, message, line)[0], itemname, False)

    def newSub(self, itemname, fromuser, message, line):
        self.subitems.append(
            Item(insertSubItem(self.id, itemname[:255], fromuser, message, line)[0], itemname, False, True))

    def toggle(self):
        self.done = not self.done
        if self.issub:
            dbfunc = Thread(target=updateSubItem, args=(self.id, self.done))
        else:
            for subitem in self.subitems:
                subitem.done = self.done
            dbfunc = Thread(target=updateItem, args=(self.id, self.done))
        dbfunc.start()


class ItemIterator:
    def __init__(self, _item):
        self._item = _item
        self._index = 0

    def __next__(self):
        if self._index == 0:
            temp = self._item.name
        elif self._index == 1:
            temp = self._item.done
        elif self._index == 2:
            if self._item.issub:
                raise StopIteration
            if self._item.subitems:
                temp = []
                for subitem in self._item.subitems:
                    temp.append(list(subitem))
            else:
                raise StopIteration
        else:
            raise StopIteration
        self._index += 1
        return temp
