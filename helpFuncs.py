from random import choice
from string import (ascii_lowercase, ascii_uppercase, digits)

def id_generator(size=10, chars = ascii_lowercase + ascii_uppercase + digits):
  return ''.join(choice(chars) for _ in range(size))

def isInt(tester):
  try:
    int(tester)
    return True
  except:
    return False
