from ..dbFuncs import (toggleListOpen, sortList)

class Settings:


  def listToggle(code, newState):
    toggleListOpen(code, newState)

  def listSort(code, sorting):
    sortList(code, sorting)

  def backupSingle():
    pass #TODO
