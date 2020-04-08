from json import load as jload
from psycopg2 import connect as psyconn
from .helpFuncs import rearrangeList as hFRearrange

BOTTOKEN = "do2bot"
tokenDir = "/home/lunaresk/gitProjects/telegramBots/"
tokenFile = "bottoken.json"

conn = None


def getConn():
    with open(tokenDir + tokenFile, "r") as file:
        temp = jload(file)
    dblogin = temp["psyconn"][BOTTOKEN]
    global conn
    conn = psyconn(host=dblogin[0], database=dblogin[1], user=dblogin[2], password=dblogin[3])


def getCur():
    try:
        cur = conn.cursor()
        cur.execute("SELECT 1;")
        cur.fetchall()
    except Exception as error:
        getConn()
        return conn.cursor()
    return cur


def initDB():
    with getCur() as cur:
        cur.execute("CREATE TABLE IF NOT EXISTS Users(TId BIGINT PRIMARY KEY NOT NULL, "
                    "Lang CHAR(2) NOT NULL DEFAULT 'en');")
        cur.execute("CREATE TABLE IF NOT EXISTS Lists(Code TEXT PRIMARY KEY NOT NULL, Title TEXT NOT NULL, "
                    "Owner BIGINT NOT NULL REFERENCES Users(Tid) ON UPDATE CASCADE ON DELETE CASCADE, "
                    "Name TEXT NOT NULL, Message TEXT NOT NULL DEFAULT '0', Open BOOLEAN NOT NULL DEFAULT False);")
        cur.execute("CREATE TABLE IF NOT EXISTS InSettings("
                    "List TEXT NOT NULL REFERENCES Lists(Code) ON UPDATE CASCADE ON DELETE CASCADE, "
                    "Member BIGINT NOT NULL REFERENCES Users(TId) ON UPDATE CASCADE ON DELETE CASCADE);")
        cur.execute("CREATE TABLE IF NOT EXISTS Notify("
                    "List TEXT NOT NULL REFERENCES Lists(Code) ON UPDATE CASCADE ON DELETE CASCADE, "
                    "Member BIGINT NOT NULL REFERENCES Users(TId) ON UPDATE CASCADE ON DELETE CASCADE);")
        cur.execute("CREATE TABLE IF NOT EXISTS Items(ID BIGSERIAL PRIMARY KEY NOT NULL, "
                    "List TEXT NOT NULL REFERENCES Lists(Code) ON UPDATE CASCADE ON DELETE CASCADE, "
                    "Item TEXT NOT NULL, Done BOOLEAN NOT NULL DEFAULT FALSE, FromUser BIGINT NOT NULL DEFAULT -1, "
                    "MessageID BIGINT NOT NULL DEFAULT -1, Line SMALLINT NOT NULL DEFAULT 0);")
        cur.execute("CREATE TABLE IF NOT EXISTS Subitems(ID BIGSERIAL PRIMARY KEY NOT NULL, "
                    "TopItem BIGINT NOT NULL REFERENCES Items(Id) ON UPDATE CASCADE ON DELETE CASCADE, "
                    "Item TEXT NOT NULL, Done BOOLEAN NOT NULL DEFAULT FALSE, FromUser BIGINT NOT NULL DEFAULT -1, "
                    "MessageID BIGINT NOT NULL DEFAULT -1, Line SMALLINT NOT NULL DEFAULT 0);")
        cur.execute("CREATE TABLE IF NOT EXISTS Coworkers("
                    "List TEXT NOT NULL REFERENCES Lists(Code) ON UPDATE CASCADE ON DELETE CASCADE, "
                    "Worker BIGINT NOT NULL REFERENCES Users(Tid) ON UPDATE CASCADE ON DELETE CASCADE, "
                    "Name TEXT NOT NULL, Message TEXT NOT NULL DEFAULT '0');")
        cur.execute("CREATE TABLE IF NOT EXISTS InlineMessages("
                    "List TEXT NOT NULL REFERENCES Lists(Code) ON UPDATE CASCADE ON DELETE CASCADE, "
                    "InlineID TEXT NOT NULL);")
        cur.execute("CREATE TABLE IF NOT EXISTS PrivateInlines(InlineID TEXT PRIMARY KEY NOT NULL, "
                    "MessageID BIGINT NOT NULL);")
        cur.connection.commit()


# Insert functions for the Database

def insertCoworker(code, user, name, message):
    with getCur() as cur:
        cur.execute("INSERT INTO Coworkers(List, Worker, Name, Message) VALUES(%s, %s, %s, %s);",
                    (code, user, name, str(message)))
        cur.connection.commit()


def insertInlineMessage(code, message):
    with getCur() as cur:
        cur.execute("INSERT INTO InlineMessages(List, InlineID) VALUES(%s, %s);", (code, str(message)))
        cur.connection.commit()


def insertItem(code, item, fromuser=-1, message=-1, line=0):
    with getCur() as cur:
        cur.execute("SELECT * FROM Items WHERE List = %s;", (code,))
        templen = len(cur.fetchall())
        cur.execute("SELECT * FROM Subitems WHERE TopItem in (SELECT Id FROM Items WHERE List = %s);", (code,))
        templen += len(cur.fetchall())
        if templen < 20:
            cur.execute(
                "INSERT INTO Items(List, Item, FromUser, MessageID, Line) VALUES(%s, %s, %s, %s, %s) RETURNING Id;",
                (code, item, fromuser, message, line))
            cur.connection.commit()
            return cur.fetchone()
        return False


def insertItems(code, items, fromuser=-1, message=-1, line=0):
    templist = []
    for item in items:
        temp = insertItem(code, item, fromuser, message, line)
        if temp:
            line += 1
            templist.append(temp)
        else:
            templist.append(False)
            break
    return templist


# TODO rewrite for nested lists
# def insertItems(code, items, fromuser = -1, message = -1, line = 0):
#  topitem = 0
#  for item in items:
#    if not item[0] == '-':
#      insertItem(code, item, fromuser, message, line)
#      topitem = getItems(code)[-1][0]
#    elif topitem:
#      insertSubItem(topitem, item[1:], fromuser, message, line)
#    else:
#      insertItem(code, item, fromuser, message, line)
#    line += 1

def insertList(code, title, owner, name):
    with getCur() as cur:
        cur.execute("INSERT INTO Lists(Code, Title, Owner, Name) VALUES(%s, %s, %s, %s);", (code, title, owner, name))
        cur.connection.commit()


def insertPrivateInline(inlineId, messageId):
    with getCur() as cur:
        cur.execute("INSERT INTO PrivateInlines(InlineId, MessageId) VALUES(%s, %s);", (inlineId, messageId))
        cur.connection.commit()


def insertSubItem(topitem, item, fromuser=-1, message=-1, line=0):
    with getCur() as cur:
        cur.execute(
            "INSERT INTO Subitems(TopItem, Item, FromUser, MessageID, Line) VALUES(%s, %s, %s, %s, %s) RETURNING Id;",
            (topitem, item, fromuser, message, line))
        cur.connection.commit()
        return cur.fetchone()


def insertSubItems(repliedmsg, items, fromuser=-1, message=-1, line=0):
    temp = getItemsByEdit(fromuser, repliedmsg)
    if not len(temp) == 1:
        return False
    topitem = temp[0][0]
    for item in items:
        insertSubItem(topitem, item, fromuser, message, line)
        line += 1
    return True


def insertUser(tid, lang='en'):
    with getCur() as cur:
        cur.execute("INSERT INTO Users(Tid, Lang) VALUES(%s, %s);", (tid, lang))
        cur.connection.commit()


# Select functions for the Database

def codeInDB(code):
    with getCur() as cur:
        cur.execute("SELECT Code FROM Lists WHERE Code = %s;", (code,))
        if cur.fetchone():
            return True
        return False


def getCodeByEdit(fromuser, msgID):
    with getCur() as cur:
        cur.execute("SELECT List FROM Items WHERE FromUser = %s AND MessageID = %s;", (fromuser, msgID))
        temp = cur.fetchone()
    try:
        temp = temp[0]
    except:
        temp = ""
    return temp


def getCoworkers(code):
    with getCur() as cur:
        cur.execute("SELECT * FROM Coworkers WHERE List = %s;", (code,))
        return cur.fetchall()


def getCoworkerMessage(code, user):
    with getCur() as cur:
        cur.execute("SELECT Message FROM Coworkers WHERE List = %s AND Worker = %s;", (code, user))
        return cur.fetchone()


def getCoworkerMessages(code):
    with getCur() as cur:
        cur.execute("SELECT Worker, Message FROM Coworkers WHERE List = %s;", (code,))
        return cur.fetchall()


def getInlineMessages(code):
    with getCur() as cur:
        cur.execute("SELECT * FROM InlineMessages WHERE List = %s;", (code,))
        return cur.fetchall()


def getInSettings(code):
    with getCur() as cur:
        cur.execute("SELECT Member FROM InSettings WHERE List = %s;", (code,))
        return cur.fetchall()


def getItem(id):
    with getCur() as cur:
        cur.execute("SELECT * FROM Items WHERE Id = %s;", (id,))
        return cur.fetchone()


def getItemByEdit(fromuser, msgID, line):
    with getCur() as cur:
        cur.execute("SELECT * FROM Items WHERE FromUser = %s AND MessageID = %s AND Line = %s;",
                    (fromuser, msgID, line))
        return cur.fetchone()


def getItems(code):
    with getCur() as cur:
        cur.execute("SELECT * FROM Items WHERE List = %s ORDER BY Id ASC;", (code,))
        return cur.fetchall()


def getItemsByEdit(fromuser, msgID):
    with getCur() as cur:
        cur.execute("SELECT * FROM Items WHERE FromUser = %s AND MessageID = %s;", (fromuser, msgID))
        return cur.fetchall()


def getList(code):
    with getCur() as cur:
        cur.execute("SELECT * FROM Lists WHERE Code = %s;", (code,))
        return cur.fetchone()


def getJoinStatus(code: str):
    with getCur() as cur:
        cur.execute("SELECT Open FROM Lists WHERE Code = %s;", (code,))
        return cur.fetchone()


def getLikelyLists(pattern, user):
    with getCur() as cur:
        cur.execute("""SELECT * FROM Lists WHERE
      Owner = %s AND Title LIKE %s
      OR Owner = %s AND Code LIKE %s
      OR Code IN (SELECT Code FROM Coworkers WHERE
      Worker = %s AND Code IN (SELECT Code FROM Lists WHERE
      Code LIKE %s OR Title LIKE %s))
      ORDER BY Message DESC;""", (user, pattern, user, pattern, user, pattern, pattern))
        return cur.fetchall()


def getNotify(code):
    with getCur() as cur:
        cur.execute("SELECT Member FROM Notify WHERE List = %s;", (code,))
        return cur.fetchall()


def getNotifyByUser(user, code=""):
    with getCur() as cur:
        if code:
            cur.execute("SELECT * FROM Notify WHERE List = %s AND Member = %s;", (code, user))
        else:
            cur.execute("SELECT List FROM Notify WHERE Member = %s;", (user,))
        return cur.fetchall()


def getOwnedLists(user):
    with getCur() as cur:
        cur.execute("SELECT * FROM Lists WHERE Owner = %s;", (user,))
        return cur.fetchall()


def getOwnerMessage(code):
    with getCur() as cur:
        cur.execute("SELECT Message FROM Lists WHERE Code = %s;", (code,))
        return cur.fetchone()


def getOwnLists(user):
    with getCur() as cur:
        cur.execute("""SELECT * FROM Lists WHERE Owner = %s
    OR Code IN (SELECT List FROM Coworkers WHERE Worker = %s);""", (user, user))
        return cur.fetchall()


def getPrivateInline(inlineId):
    with getCur() as cur:
        cur.execute("SELECT * FROM PrivateInlines WHERE InlineId = %s", (inlineId,))
        return cur.fetchone()


def getRecentList(user):
    with getCur() as cur:
        cur.execute("SELECT * FROM Lists WHERE Owner = %s ORDER BY Message DESC;", (user,))
        list1 = cur.fetchone()
        cur.execute("SELECT * FROM Coworkers WHERE Worker = %s ORDER BY Message DESC;", (user,))
        list2 = cur.fetchone()
        if list1 == None:
            return list2
        if list2 == None:
            return list1
        return (list1 if list1[4] > list2[3] else list2)


def getSettingsTerminal(code):
    with getCur() as cur:
        cur.execute("SELECT * FROM InSettings WHERE List = %s;", (code,))
        return cur.fetchall()


def getSettingsTerminalByUser(code, userid):
    with getCur() as cur:
        cur.execute("SELECT * FROM InSettings WHERE List = %s AND Member = %s;", (code, userid))
        return cur.fetchall()


def getSpecificMessage(code, user):
    return getCoworkerMessage(code, user) or getOwnerMessage(code)


def getSubItem(id):
    with getCur() as cur:
        cur.execute("SELECT * FROM Subitems WHERE Id = %s;", (id,))
        return cur.fetchone()


def getSubItemByEdit(fromuser, msgID, line):
    with getCur() as cur:
        cur.execute("SELECT * FROM Subitems WHERE FromUser = %s AND MessageID = %s AND Line = %s;",
                    (fromuser, msgID, line))
        return cur.fetchone()


def getSubItems(topitem):
    with getCur() as cur:
        cur.execute("SELECT * FROM Subitems WHERE TopItem = %s ORDER BY Id ASC;", (topitem,))
        return cur.fetchall()


def getSubItemsByEdit(fromuser, msgID):
    with getCur() as cur:
        cur.execute("SELECT * FROM Subitems WHERE FromUser = %s AND MessageID = %s;", (fromuser, msgID))
        return cur.fetchall()


def getTopItemByEdit(fromuser, msgID):
    with getCur() as cur:
        cur.execute("SELECT TopItem FROM Subitems WHERE FromUser = %s AND MessageID = %s;", (fromuser, msgID))
        temp = cur.fetchone()
        if temp:
            if type(temp) == type(tuple()):
                return temp[0]
        return 0


def getUser(tid):
    with getCur() as cur:
        cur.execute("SELECT * FROM Users WHERE Tid = %s;", (tid,))
        temp = cur.fetchone()
    if temp:
        return temp
    insertUser(tid)
    return (tid, 'en')


def getUsers():
    with getCur() as cur:
        cur.execute("SELECT * FROM Users;")
        return cur.fetchall()


def hasSubItems(topitem):
    with getCur() as cur:
        cur.execute("SELECT Id FROM Subitems WHERE TopItem = %s;", (topitem,))
        return cur.fetchone()


def isCoworker(code, user):
    with getCur() as cur:
        cur.execute("SELECT List FROM Coworkers WHERE List = %s AND Worker = %s;", (code, user))
        if cur.fetchone():
            return True
        return False


def isOpen(code):
    with getCur() as cur:
        cur.execute("SELECT Open FROM Lists WHERE Code = %s;", (code,))
        return cur.fetchone()[0]


def isOwner(code, user):
    with getCur() as cur:
        cur.execute("SELECT Code FROM Lists WHERE Code = %s AND Owner = %s;", (code, user))
        if cur.fetchone():
            return True
        return False


# Delete functions for the Database

def removeCoworker(code, user):
    with getCur() as cur:
        cur.execute("DELETE FROM Coworkers WHERE List = %s AND Worker = %s;", (code, user))
        cur.connection.commit()


def removeExcessItems(fromuser, msgID, line):
    with getCur() as cur:
        cur.execute("DELETE FROM Items WHERE FromUser = %s AND MessageID = %s AND Line >= %s;", (fromuser, msgID, line))
        cur.connection.commit()


def removeExcessSubItems(fromuser, msgID, line):
    with getCur() as cur:
        cur.execute("DELETE FROM Subitems WHERE FromUser = %s AND MessageID = %s AND Line >= %s;",
                    (fromuser, msgID, line))
        cur.connection.commit()


def removeInlineMessage(inline_id):
    with getCur() as cur:
        cur.execute("DELETE FROM InlineMessages WHERE InlineId = %s;", (inline_id,))
        cur.connection.commit()


def removeItems(id):
    with getCur() as cur:
        cur.execute("DELETE FROM Subitems WHERE TopItem in (SELECT Id FROM Items WHERE List = %s AND Done = True);",
                    (id,))
        cur.execute("DELETE FROM Items WHERE List = %s AND Done = True;", (id,))
        cur.connection.commit()


def removeList(code):
    with getCur() as cur:
        cur.execute("DELETE FROM Subitems WHERE TopItem IN (SELECT Id FROM Items WHERE List = %s);", (code,))
        cur.execute("DELETE FROM Items WHERE List = %s;", (code,))
        cur.execute("DELETE FROM Coworkers WHERE List = %s;", (code,))
        cur.execute("DELETE FROM InlineMessages WHERE List = %s;", (code,))
        cur.execute("DELETE FROM Lists WHERE Code = %s;", (code,))
        cur.connection.commit()


def removePrivateInline(inlineId):
    with getCur() as cur:
        cur.execute("DELETE FROM PrivateInlines WHERE InlineId = %s;", (inlineId,))
        cur.connection.commit()


# Update functions for the Database

def editItem(item, fromuser, msgID, line=0):
    if not getItemByEdit(fromuser, msgID, line):
        return False
    with getCur() as cur:
        cur.execute("UPDATE Items SET Item = %s WHERE FromUser = %s AND MessageID = %s AND Line = %s;",
                    (item, fromuser, msgID, line))
        cur.connection.commit()
    return True


def editSubItem(item, fromuser, msgID, line=0):
    if not getSubItemByEdit(fromuser, msgID, line):
        return False
    with getCur() as cur:
        cur.execute("UPDATE Subitems SET Item = %s WHERE FromUser = %s AND MessageID = %s AND Line = %s;",
                    (item, fromuser, msgID, line))
        cur.connection.commit()
    return True


def editUser(tid, lang):
    with getCur() as cur:
        cur.execute("UPDATE Users SET Lang = %s WHERE Tid = %s;", (lang, tid))
        cur.connection.commit()


def toggleListOpen(code, state=False):
    with getCur() as cur:
        cur.execute("UPDATE Lists SET Open = %s WHERE Code = %s;", (state, code))
        cur.connection.commit()


def updateCoworker(code, user, message):
    with getCur() as cur:
        cur.execute("UPDATE Coworkers SET Message = %s WHERE List = %s AND Worker = %s;", (str(message), code, user))
        cur.connection.commit()


def updateItem(id, done=False):
    with getCur() as cur:
        cur.execute("UPDATE Items SET Done = NOT Done WHERE Id = %s;", (id,))
        if hasSubItems(id):
            cur.execute("UPDATE Subitems SET Done = (SELECT Done FROM Items WHERE Id = %s) WHERE TopItem = %s",
                        (id, id))
        cur.connection.commit()


def updateOwner(code, message):
    with getCur() as cur:
        cur.execute("UPDATE Lists SET Message = %s WHERE Code = %s;", (str(message), code))
        cur.connection.commit()


def updateSubItem(id, done=False):
    with getCur() as cur:
        cur.execute("UPDATE Subitems SET Done = NOT Done WHERE Id = %s;", (id,))
        cur.execute(
            "SELECT * FROM Subitems WHERE Done = False AND TopItem = (SELECT TopItem FROM Subitems WHERE Id = %s);",
            (id,))
        if cur.fetchone():
            cur.execute("UPDATE Items SET Done = False WHERE Id = (SELECT TopItem FROM Subitems WHERE Id = %s);", (id,))
        else:
            cur.execute("UPDATE Items SET Done = True WHERE Id = (SELECT TopItem FROM Subitems WHERE Id = %s);", (id,))
        cur.connection.commit()


# Other/combined functions for the Database

def editItems(items, fromuser, msgID, line=0):
    code = getCodeByEdit(fromuser, msgID)
    if code:
        for item in items:
            if not item[0] == '-':
                if editItem(item, fromuser, msgID, line):
                    line += 1
                else:
                    break
            elif editSubItem(item, fromuser, msgID, line):
                line += 1
        if len(items) > line:
            for item in items[line:]:
                insertItem(code, item, fromuser, msgID, line)
                line += 1
        else:
            removeExcessItems(fromuser, msgID, line)
    else:
        topitem = getTopItemByEdit(fromuser, msgID)
        for item in items:
            if editSubItem(item, fromuser, msgID, line):
                line += 1
            else:
                break
        if len(items) > line:
            for item in items[line:]:
                insertSubItem(topitem, item, fromuser, msgID, line)
                line += 1
        else:
            removeExcessSubItems(fromuser, msgID, line)
    return code


def toggleNotify(code, user, state=False):
    with getCur() as cur:
        if state:
            cur.execute("INSERT INTO Notify(List, Member) VALUES(%s, %s);", (code, user))
        else:
            cur.execute("DELETE FROM Notify WHERE List = %s AND Member = %s;", (code, user))
        cur.connection.commit()


def toggleSettingsTerminal(code, user, state=False):
    with getCur() as cur:
        if state:
            cur.execute("INSERT INTO InSettings(List, Member) VALUES(%s, %s);", (code, user))
        else:
            cur.execute("DELETE FROM InSettings WHERE List = %s AND Member = %s;", (code, user))
        cur.connection.commit()


def updateSpecificMessage(code, user, message):
    if getCoworkerMessage(code, user):
        updateCoworker(code, user, message)
    else:
        updateOwner(code, message)


def sortList(code, sorting):
    with getCur() as cur:
        cur.execute("SELECT * FROM Items WHERE List = %s ORDER BY ID;", (code,))
        items = cur.fetchall()
        newSort = hFRearrange(items, sorting)
        cur.execute("UPDATE Items SET Id = -Id WHERE List = %s;", (code,))
        for item in items:
            cur.execute("UPDATE Items SET Id = %s WHERE Id = %s;", (item[0], -newSort.pop(0)))
        cur.connection.commit()


def defragTables():
    pass
