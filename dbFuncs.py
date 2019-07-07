from ..bottoken import getConn
from . import helpFuncs

dblogin = 'do2bot'

def initDB():
  with getConn(dblogin) as conn:
    cur = conn.cursor()
    conn.rollback()
    cur.execute("CREATE TABLE IF NOT EXISTS Lists(Code TEXT PRIMARY KEY NOT NULL, Title TEXT NOT NULL, Owner BIGINT NOT NULL, Name TEXT NOT NULL, Message TEXT NOT NULL DEFAULT '0', Open BOOLEAN NOT NULL DEFAULT FALSE, AdminTerminal BOOLEAN NOT NULL DEFAULT FALSE);")
    cur.execute("CREATE TABLE IF NOT EXISTS Items(ID BIGSERIAL PRIMARY KEY NOT NULL, List TEXT REFERENCES Lists(Code), Item TEXT NOT NULL, Done BOOLEAN NOT NULL DEFAULT FALSE, FromUser BIGINT NOT NULL DEFAULT -1, MessageID BIGINT NOT NULL DEFAULT -1, Line SMALLINT NOT NULL DEFAULT 0);")
    cur.execute("CREATE TABLE IF NOT EXISTS Coworkers(List TEXT NOT NULL REFERENCES Lists(Code), Worker BIGINT NOT NULL, Name TEXT NOT NULL, Message TEXT NOT NULL DEFAULT '0');")
    cur.execute("CREATE TABLE IF NOT EXISTS InlineMessages(List TEXT NOT NULL REFERENCES Lists(Code), InlineID TEXT NOT NULL);")
    cur.execute("CREATE TABLE IF NOT EXISTS Subitems(Subitem BIGINT PRIMARY KEY NOT NULL, Item BIGINT NOT NULL REFERENCES Items(ID));")
    conn.commit()

def insertList(code, title, owner, name):
  with getConn(dblogin) as conn:
    cur = conn.cursor()
    cur.execute("INSERT INTO Lists(Code, Title, Owner, Name) VALUES(%s, %s, %s, %s);", (code, title, owner, name))
    conn.commit()

def insertItem(code, item, fromuser = -1, message = -1, line = 0):
  with getConn(dblogin) as conn:
    cur = conn.cursor()
    cur.execute("INSERT INTO Items(List, Item, FromUser, MessageID, Line) VALUES(%s, %s, %s, %s, %s);", (code, item, fromuser, message, line))
    conn.commit()

def insertItems(code, items, fromuser = -1, message = -1, line = 0):
  for item in items:
    insertItem(code, item, fromuser, message, line)
    line += 1

def insertCoworker(code, user, name, message):
  with getConn(dblogin) as conn:
    cur = conn.cursor()
    cur.execute("INSERT INTO Coworkers(List, Worker, Name, Message) VALUES(%s, %s, %s, %s);", (code, user, name, str(message)))
    conn.commit()

def insertInlineMessage(code, message):
  with getConn(dblogin) as conn:
    cur = conn.cursor()
    cur.execute("INSERT INTO InlineMessages(List, InlineID) VALUES(%s, %s);", (code, str(message)))
    conn.commit()

def updateOwner(code, message):
  with getConn(dblogin) as conn:
    cur = conn.cursor()
    cur.execute("UPDATE Lists SET Message = %s WHERE Code = %s;", (str(message), code))
    conn.commit()

def editItem(item, fromuser, msgID, line = 0):
  if not getItemByEdit(fromuser, msgID, line):
    return False
  with getConn(dblogin) as conn:
    cur = conn.cursor()
    cur.execute("UPDATE Items SET Item = %s WHERE FromUser = %s AND MessageID = %s AND Line = %s;", (item, fromuser, msgID, line))
    conn.commit()
  return True

def getItemByEdit(fromuser, msgID, line):
  with getConn(dblogin) as conn:
    cur = conn.cursor()
    cur.execute("SELECT * FROM Items WHERE FromUser = %s AND MessageID = %s AND Line = %s;", (fromuser, msgID, line))
    return cur.fetchone()

def editItems(items, fromuser, msgID, line = 0):
  code = getCodeByEdit(fromuser, msgID)
  for item in items:
    if editItem(item, fromuser, msgID, line):
      line += 1
    else:
      break;
  if len(items) > line:
    if code:
      for item in items[line:]:
        insertItem(code, item, fromuser, msgID, line)
        line += 1
  else:
    removeExcessItems(fromuser, msgID, line)
  return code

def getCodeByEdit(fromuser, msgID):
  with getConn(dblogin) as conn:
    cur = conn.cursor()
    cur.execute("SELECT List FROM Items WHERE FromUser = %s AND MessageID = %s;", (fromuser, msgID))
    temp = cur.fetchone()
    if temp:
      if type(temp) == type(tuple()):
        return temp[0]
    return ""

def getItemsByEdit(fromuser, msgID):
  with getConn(dblogin) as conn:
    cur = conn.cursor()
    cur.execute("SELECT * FROM Items WHERE FromUser = %s AND MessageID = %s;", (fromuser, msgID))
    return cur.fetchall()

def removeExcessItems(fromuser, msgID, line):
  with getConn(dblogin) as conn:
    cur = conn.cursor()
    cur.execute("DELETE FROM Items WHERE FromUser = %s AND MessageID = %s AND Line >= %s;", (fromuser, msgID, line))
    conn.commit()

def toggleListOpen(code, state = False):
  with getConn(dblogin) as conn:
    cur = conn.cursor()
    cur.execute("UPDATE Lists SET Open = %s WHERE Code = %s;", (state, code))
    conn.commit()

def toggleAdminKeyboard(code, state = False):
  with getConn(dblogin) as conn:
    cur = conn.cursor()
    cur.execute("UPDATE Lists SET AdminTerminal = %s WHERE Code = %s", (state, code))
    conn.commit()

def updateItem(id):
  with getConn(dblogin) as conn:
    cur = conn.cursor()
    cur.execute("UPDATE Items SET Done = NOT Done WHERE Id = %s;", (id,))
    conn.commit()

def updateCoworker(code, user, message):
  with getConn(dblogin) as conn:
    cur = conn.cursor()
    cur.execute("UPDATE Coworkers SET Message = %s WHERE List = %s AND Worker = %s;", (str(message), code, user))
    conn.commit()

def updateSpecificMessage(code, user, message):
  if getCoworkerMessage(code, user):
    updateCoworker(code, user, message)
  else:
    updateOwner(code, message)

def removeList(code):
  with getConn(dblogin) as conn:
    cur = conn.cursor()
    cur.execute("DELETE FROM Items WHERE List = %s;", (code,))
    cur.execute("DELETE FROM Coworkers WHERE List = %s;", (code,))
    cur.execute("DELETE FROM InlineMessages WHERE List = %s;", (code,))
    cur.execute("DELETE FROM Lists WHERE Code = %s;", (code,))
    conn.commit()

def removeCoworker(code, user):
  with getConn(dblogin) as conn:
    cur = conn.cursor()
    cur.execute("DELETE FROM Coworkers WHERE List = %s AND Worker = %s;", (code, user))
    conn.commit()

def removeItems(id):
  with getConn(dblogin) as conn:
    cur = conn.cursor()
    cur.execute("DELETE FROM Items WHERE List = %s AND Done = True;", (id,))
    conn.commit()

def removeInlineMessage(inline_id):
  with getConn(dblogin) as conn:
    cur = conn.cursor()
    cur.execute("DELETE FROM InlineMessages WHERE InlineId = %s;", (inline_id,))
    conn.commit()

def getList(code):
  with getConn(dblogin) as conn:
    cur = conn.cursor()
    cur.execute("SELECT * FROM Lists WHERE Code = %s;", (code,))
    return cur.fetchone()

def getRecentList(user):
  with getConn(dblogin) as conn:
    cur = conn.cursor()
    cur.execute("SELECT * FROM Lists WHERE Owner = %s ORDER BY Message DESC;", (user,))
    list1 = cur.fetchone()
    cur.execute("SELECT * FROM Coworkers WHERE Worker = %s ORDER BY Message DESC;", (user,))
    list2 = cur.fetchone()
    if list1 == None:
      return list2
    if list2 == None:
      return list1
    return(list1 if list1[4] > list2[3] else list2)

def getOwnLists(user):
  with getConn(dblogin) as conn:
    cur = conn.cursor()
    cur.execute("""SELECT * FROM Lists WHERE Owner = %s
    OR Code IN (SELECT Code FROM Coworkers WHERE Worker = %s);""", (user, user))
    return cur.fetchall()

def getOwnedLists(user):
  with getConn(dblogin) as conn:
    cur = conn.cursor()
    cur.execute("SELECT * FROM Lists WHERE Owner = %s;", (user,))
    return cur.fetchall()

def getOwnerMessage(code):
  with getConn(dblogin) as conn:
    cur = conn.cursor()
    cur.execute("SELECT Message FROM Lists WHERE Code = %s;", (code,))
    return cur.fetchone()

def getItem(id):
  with getConn(dblogin) as conn:
    cur = conn.cursor()
    cur.execute("SELECT * FROM Items WHERE Id = %s;", (id,))
    return cur.fetchone()

def getItems(code):
  with getConn(dblogin) as conn:
    cur = conn.cursor()
    cur.execute("SELECT * FROM Items WHERE List = %s ORDER BY Id ASC;", (code,))
    return cur.fetchall()

def getCoworkers(code):
  with getConn(dblogin) as conn:
    cur = conn.cursor()
    cur.execute("SELECT * FROM Coworkers WHERE List = %s;", (code,))
    return cur.fetchall()

def getCoworkerMessage(code, user):
  with getConn(dblogin) as conn:
    cur = conn.cursor()
    cur.execute("SELECT Message FROM Coworkers WHERE List = %s AND Worker = %s;", (code, user))
    return cur.fetchone()

def getInlineMessages(code):
  with getConn(dblogin) as conn:
    cur = conn.cursor()
    cur.execute("SELECT * FROM InlineMessages WHERE List = %s;", (code,))
    return cur.fetchall()

def getSpecificMessage(code, user):
  return getCoworkerMessage(code, user) or getOwnerMessage(code)

def getLikelyLists(pattern, user):
  with getConn(dblogin) as conn:
    cur = conn.cursor()
    cur.execute("""SELECT * FROM Lists WHERE
      Owner = %s AND Title LIKE %s
      OR Owner = %s AND Code LIKE %s
      OR Code IN (SELECT Code FROM Coworkers WHERE
      Worker = %s AND Code IN (SELECT Code FROM Lists WHERE
      Code LIKE %s OR Title LIKE %s))
      ORDER BY Message DESC;""", (user, pattern, user, pattern, user, pattern, pattern))
    return cur.fetchall()

def sortList(code, sorting):
  with getConn(dblogin) as conn:
    cur = conn.cursor()
    cur.execute("SELECT * FROM Items WHERE List = %s ORDER BY ID;", (code,))
    items = cur.fetchall()
    newSort = helpFuncs.rearrangeList(items, sorting)
    cur.execute("UPDATE Items SET Id = -Id WHERE List = %s;", (code,))
    for item in items:
      cur.execute("UPDATE Items SET Id = %s WHERE Id = %s;", (item[0], -newSort.pop(0)))
    conn.commit()

def isAvailable(code):
  with getConn(dblogin) as conn:
    cur = conn.cursor()
    cur.execute("SELECT Code FROM Lists WHERE Code = %s;", (code,))
    if evaluateOne(cur.fetchone()) != None:
      return True
    return False

def isOpen(code):
  with getConn(dblogin) as conn:
    cur = conn.cursor()
    cur.execute("SELECT Open FROM Lists WHERE Code = %s;", (code,))
    return cur.fetchone()[0]

def isOwner(code, user):
  with getConn(dblogin) as conn:
    cur = conn.cursor()
    cur.execute("SELECT Code FROM Lists WHERE Code = %s AND Owner = %s;",(code, user))
    if cur.fetchone() == None:
      return False
    return True

def isCoworker(code, user):
  with getConn(dblogin) as conn:
    cur = conn.cursor()
    cur.execute("SELECT List FROM Coworkers WHERE List = %s AND Worker = %s;",(code, user))
    if cur.fetchone() == None:
      return False
    return True

def evaluateList(datas):
  list = []
  for i in datas:
    list.append(i[0])
  return list

def evaluateOne(data):
  if data != None:
    if data[0] != None:
      return data[0]
  return None

