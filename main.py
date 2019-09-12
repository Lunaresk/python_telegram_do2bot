from json import load as jload
from telegram.ext import Updater
from src.do2bot import main

BOTTOKEN = "lunaalphabot"
tokenDir = "/home/lunaresk/gitProjects/telegramBots/"
tokenFile = "bottoken.json"


if __name__ == '__main__':
  with open(tokenDir + tokenFile, "r") as file:
    tokens = jload(file)
  thistoken = tokens["bottoken"][BOTTOKEN]
  del tokens
  main(Updater(thistoken, use_context = True))
