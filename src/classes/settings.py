from ..dbFuncs import (toggleListOpen, sortList)


class Settings:

    @staticmethod
    def listToggle(code, new_state):
        toggleListOpen(code, new_state)

    @staticmethod
    def listSort(code, sorting):
        sortList(code, sorting)

    @staticmethod
    def backupSingle():
        pass  # TODO
