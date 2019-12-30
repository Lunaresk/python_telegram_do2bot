from json import load as jload
from telegram.ext import (Updater, PicklePersistence)
from src.do2bot import main

BOTTOKEN = "do2bot"
tokenDir = "/home/lunaresk/gitProjects/telegramBots/"
tokenFile = "bottoken.json"
persDir = tokenDir + BOTTOKEN + "/temp/"
persFile = "persFile"

if __name__ == '__main__':
    persObj = PicklePersistence(filename=persDir + persFile)
    with open(tokenDir + tokenFile, "r") as file:
        tokens = jload(file)
    thistoken = tokens["bottoken"][BOTTOKEN]
    del tokens
    main(Updater(thistoken, persistence=persObj, use_context=True))
