from telegram import (InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResult, InlineQueryResultArticle, InputTextMessageContent)
from telegram.ext import (CommandHandler, MessageHandler, RegexHandler, CallbackQueryHandler, ConversationHandler, InlineQueryHandler, ChosenInlineResultHandler, Filters)
from telegram.ext.dispatcher import run_async
from telegram.error import BadRequest
from time import sleep
from json import (load as jload, dump as jdump)
from pickle import (load as pload, dump as pdump)
from ..errorCallback import contextCallback
from . import dbFuncs
from . import helpFuncs
import gettext
import logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

SETNAME = range(1)
SETTINGS = range(1)
ListFooter = {"Check": 'c', "Options": 'o', "Remove": 'r', "Exit": 'e', "CheckSub": 's'}
OptionsOrder = ["{0}", "✅⬆", "✅⬇", "↩"]
Options = {OptionsOrder[0]: "open", OptionsOrder[1]: "sortUp", OptionsOrder[2]: "sortDn", OptionsOrder[3]: "back"}
BOTTOKEN = 'do2bot'
workingDir = "/home/shiro/gitProjects/telegramBots/" + BOTTOKEN
backupsDir = workingDir + "/temp"
localeDir = workingDir + "/locales"

def start(update, context):
  message, args, bot, user_data = update.message, context.args, context.bot, context.user_data
  userid = message.from_user['id']
  _ = getTranslation(userid)
  if len(args) == 0:
    message.reply_text(_("welcome"), parse_mode = 'Markdown',
      reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton(text = _("try"), switch_inline_query_current_chat = "")]]))
  else:
    if len(args[0]) != 10:
      if args[0] == "new":
        return new(update, context)
      message.reply_text(_("invalidargs"))
    elif not dbFuncs.isAvailable(args[0]):
      message.reply_text(_("notexisting"))
    elif not dbFuncs.isCoworker(args[0], userid):
      if dbFuncs.isOwner(args[0], userid):
        msgno = dbFuncs.getSpecificMessage(args[0], userid)[0]
        try:
          if helpFuncs.isInt(msgno):
            bot.edit_message_text(chat_id = message.chat_id, message_id = msgno, text = "↓")
          else:
            bot.edit_message_text(inline_message_id = msgno, text = "↓")
        except:
          print("Malicious message number")
        user_data['list'], user_data['current'] = args[0], message.reply_text(listText(args[0]), parse_mode = 'Markdown', disable_web_page_preview = True, reply_markup = createKeyboard(args[0], userid)).message_id
        dbFuncs.toggleAdminKeyboard(args[0])
        dbFuncs.updateOwner(args[0], user_data['current'])
      elif not dbFuncs.isOpen(args[0]):
        message.reply_text(_("notopen"))
      else:
        user_data['list'], user_data['current'] = args[0], message.reply_text(listText(args[0]), parse_mode = 'Markdown', disable_web_page_preview = True, reply_markup = createKeyboard(args[0], userid)).message_id
        dbFuncs.insertCoworker(args[0], userid, message.from_user['first_name'], user_data['current'])
        updateMessages(bot, args[0])
    else:
      user_data['list'], user_data['current'] = args[0], message.reply_text(listText(args[0]), parse_mode = 'Markdown', disable_web_page_preview = True, reply_markup = createKeyboard(args[0], userid)).message_id
      bot.edit_message_text(chat_id = message.chat_id, message_id = dbFuncs.getSpecificMessage(args[0], userid)[0], text = "↓")
      dbFuncs.updateCoworker(args[0], userid, user_data['current'])
  return ConversationHandler.END

def help(update, context):
  message, args = update.message, context.args
  userid = message.from_user['id']
  if len(args) == 0:
    args = [""]
  message.reply_text(helpFuncs.getHelpText(args[0], getTranslation(userid, "help")))

def new(update, context):
  message = update.message
  userid = message.from_user['id']
  _ = getTranslation(userid)
  message.reply_text(_("insertname"))
  return SETNAME

def setName(update, context):
  message, user_data = update.message, context.user_data
  userid = message.from_user['id']
  _ = getTranslation(userid)
  for i in range(10):
    code = helpFuncs.id_generator()
    if not dbFuncs.isAvailable(code):
      break
  if dbFuncs.isAvailable(code):
    message.reply_text(_("notcreated"))
    return ConversationHandler.END
  dbFuncs.insertList(code, message.text, userid, message.from_user['first_name'])
  user_data['list'], user_data['current'] = code, message.reply_text(listText(code), parse_mode="Markdown", disable_web_page_preview = True, reply_markup = createKeyboard(code, userid)).message_id
  dbFuncs.updateOwner(code, user_data['current'])
  return ConversationHandler.END

def blankCode(update, context):
  context.args = [update.message.text[1:]]
  start(update, context)

@run_async
def rcvMessage(update, context):
  message, bot, user_data = update.message, context.bot, context.user_data
  userid = message.from_user['id']
  tester = message.text[-5:]
  if 'tester' in user_data and user_data['tester'] == tester:
    user_data['list'] = message.text.split("/")[-1][:10]
    user_data['old'] = dbFuncs.getSpecificMessage(user_data['list'], userid)[0]
    if helpFuncs.isInt(user_data['old']):
      try:
        bot.edit_message_text(chat_id = userid, message_id = user_data['old'], text = '↓')
      except:
        pass
    else:
      try:
        bot.edit_message_text(inline_message_id = user_data['old'], text = '↓')
      except:
        pass
    count = 2
    while 'imid' not in user_data and count != 0:
      sleep(1)
      count -= 1
    try:
      dbFuncs.updateSpecificMessage(user_data['list'], userid, user_data['imid'])
      dbFuncs.removeInlineMessage(user_data['imid'])
    except:
      pass #TODO
  else:
    _ = getTranslation(userid)
    if 'list' not in user_data:
      message.reply_text(_("notspecified"))
      return
    items = message.text.split("\n")
    if not dbFuncs.insertItems(user_data['list'], items, userid, message.message_id):
      message.reply_text(_("buttonlimit"))
  updateMessages(bot, user_data['list'])
  temp = user_data['list']
  user_data.clear()
  user_data['list'] = temp

def rcvReply(update, context):
  message, replymsg, bot = update.message, update.message.reply_to_message, context.bot
  userid, replyid = message.from_user['id'], replymsg.message_id
  _ = getTranslation(userid)
  corelist = dbFuncs.getItemsByEdit(userid, replyid)[0][1]
  items = message.text.split("\n")
  if not (dbFuncs.isCoworker(corelist, userid) or dbFuncs.isOwner(corelist, userid)):
    message.reply_text(_("notallowed"))
  if not dbFuncs.insertSubItems(replyid, items, userid, message.message_id):
    message.reply_text(_("notunique"))
  else:
    updateMessages(bot, corelist)

def editMessage(update, context):
  message, bot = update.edited_message, context.bot
  try:
    code = dbFuncs.editItems(message.text.split("\n"), message.from_user['id'], message.message_id)
    updateMessages(bot, code)
  except:
    pass #TODO

def updateMessages(bot, code):
  list = dbFuncs.getList(code)
  if not dbFuncs.getAdminTerminal(code):
    try:
      if helpFuncs.isInt(list[4]):
        bot.edit_message_text(chat_id = list[2], message_id = list[4], text = listText(code), parse_mode = 'Markdown', disable_web_page_preview = True, reply_markup = createKeyboard(code, list[2]))
      else:
        bot.edit_message_text(inline_message_id = list[4], text = listText(code), parse_mode = 'Markdown', disable_web_page_preview = True, reply_markup = createKeyboard(code, list[2]))
    except BadRequest as error:
      if str(error) == "Message is not modified":
        pass #ummm... TODO
      else:
        logger.error(error)
  coworkers = dbFuncs.getCoworkers(code)
  for coworker in coworkers:
    try:
      if helpFuncs.isInt(coworker[3]):
        bot.edit_message_text(chat_id = coworker[1], message_id = coworker[3], text = listText(code), parse_mode = 'Markdown', disable_web_page_preview = True, reply_markup = createKeyboard(code, coworker[1]))
      else:
        bot.edit_message_text(inline_message_id = coworker[3], text = listText(code), parse_mode = 'Markdown', disable_web_page_preview = True, reply_markup = createKeyboard(code, coworker[1]))
    except BadRequest as error:
      logger.error(error) #ummm... TODO
  inlines = dbFuncs.getInlineMessages(code)
  for inline in inlines:
    try:
      bot.edit_message_text(inline_message_id = inline[1], text = listText(code), parse_mode = 'Markdown', disable_web_page_preview = True, reply_markup = createKeyboard(code, -1))
    except BadRequest as error:
      if str(error) == "Message_id_invalid":
        dbFuncs.removeInlineMessage(inline[1])
      else:
        logger.error(error)

#TODO Backup function, called with /backup
def backup(update, context):
  message, bot = update.message, context.bot
  userid = message.from_user['id']
  ownlists = dbFuncs.getOwnedLists(userid)
  if not ownlists:
    _ = getTranslation(userid)
    message.reply_text(_("notownedlists"))
  backuplist = []
  for ownlist in ownlists:
    backuplist.append(list(ownlist[1:4]))
    backupitems = dbFuncs.getItems(ownlist[0])
    backuplist[-1].append([])
    for item in backupitems:
      backuplist[-1][-1].append(list(item[2:4]))
      subItems = dbFuncs.getSubItems(item[0])
      print(subItems)
      if subItems:
        backuplist[-1][-1][-1].append([])
        for subitem in subItems:
          backuplist[-1][-1][-1][-1].append(list(subitem[2:4]))
  with open('{0}/do2backup.json'.format(backupsDir), 'w+') as file:
    jdump(backuplist, file)
  with open('{0}/do2backup.json'.format(backupsDir), 'rb') as file:
    bot.send_document(chat_id = message.from_user['id'], document = file)

#TODO Future restore function, called with /restore
def restore(update, context):
  pass

def updateKeyboard(bot, code):
  list = dbFuncs.getList(code)
  try:
    if not dbFuncs.getAdminTerminal(code):
      if helpFuncs.isInt(list[4]):
        bot.edit_message_reply_markup(chat_id = list[2], message_id = list[4], reply_markup = createKeyboard(code, list[2]))
      else:
        bot.edit_message_reply_markup(inline_message_id = list[4], reply_markup = createKeyboard(code, list[2]))
  except BadRequest as error:
    if str(error) == "Message is not modified":
      pass #TODO
  coworkers = dbFuncs.getCoworkers(code)
  for coworker in coworkers:
    try:
      if helpFuncs.isInt(coworker[3]):
        bot.edit_message_reply_markup(chat_id = coworker[1], message_id = coworker[3], reply_markup = createKeyboard(code, coworker[1]))
      else:
        bot.edit_message_reply_markup(inline_message_id = coworker[3], reply_markup = createKeyboard(code, coworker[1]))
    except BadRequest as error:
      pass #TODO
  inlines = dbFuncs.getInlineMessages(code)
  for inline in inlines:
    try:
      bot.edit_message_reply_markup(inline_message_id = inline[1], reply_markup = createKeyboard(code, -1))
    except BadRequest as error:
      if str(error) == "Message_id_invalid":
        dbFuncs.removeInlineMessage(inline[1])

def closeMessages(bot, code):
  list = dbFuncs.getList(code)
  try:
    if helpFuncs.isInt(list[4]):
      bot.edit_message_text(chat_id = list[2], message_id = list[4], text = "Closed")
    else:
      bot.edit_message_text(inline_message_id = list[4], text = "Closed")
  except BadRequest as error:
    pass #TODO
  coworkers = dbFuncs.getCoworkers(code)
  for coworker in coworkers:
    try:
      if helpFuncs.isInt(coworker[3]):
        bot.edit_message_text(chat_id = coworker[1], message_id = coworker[3], text = "Closed")
      else:
        bot.edit_message_text(inline_message_id = coworker[3], text = "Closed")
    except BadRequest as error:
      pass #TODO
  inlines = dbFuncs.getInlineMessages(code)
  for inline in inlines:
    try:
      bot.edit_message_text(inline_message_id = inline[1], text = "Closed")
    except BadRequest as error:
      pass

def pushInline(update, context):
  query, bot, user_data = update.callback_query, context.bot, context.user_data
  userid = query.from_user['id']
  _ = getTranslation(userid)
  action = query.data.split("_")
  if not action[1] == ListFooter["Remove"]:
    user_data.pop('closing', None)
  if not (dbFuncs.isOwner(action[0], userid) or dbFuncs.isCoworker(action[0], userid)):
    bot.answer_callback_query(callback_query_id = query.id, text = _("notallowed"))
    return ConversationHandler.END
  if action[1] == ListFooter["Check"]:
    dbFuncs.updateItem(action[2])
  elif action[1] == ListFooter["CheckSub"]:
    dbFuncs.updateSubItem(action[2])
  elif action[1] == ListFooter["Exit"]:
    bot.edit_message_text(chat_id = userid, message_id = dbFuncs.getSpecificMessage(action[0], userid)[0], text = _("revoked"))
    dbFuncs.removeCoworker(action[0], userid)
    updateMessages(bot, action[0])
    bot.answer_callback_query(callback_query_id = query.id, text = _("leftlist"))
    return ConversationHandler.END
  elif action[1] == ListFooter["Remove"]:
    items = dbFuncs.getItems(action[0])
    check = False
    if items:
      temp = items[0][3]
      for item in items:
        if item[3] != temp:
          check = True
          break
    if check:
        dbFuncs.removeItems(action[0])
    else:
      if 'closing' in user_data and user_data['closing'] == action[0]:
        closeMessages(bot, action[0])
        dbFuncs.removeList(action[0])
        bot.answer_callback_query(callback_query_id = query.id, text = _("listremoved"))
      else:
        user_data['closing'] = action[0]
        bot.answer_callback_query(callback_query_id = query.id, text = _("confirmremove"), show_alert = True)
      return ConversationHandler.END
  elif action[1] == ListFooter["Options"]:
    if query.inline_message_id:
      bot.edit_message_reply_markup(inline_message_id = query.inline_message_id, reply_markup = createAdminKeyboard(action[0], userid))
    else:
      bot.edit_message_reply_markup(chat_id = userid, message_id = query.message.message_id, reply_markup = createAdminKeyboard(action[0], userid))
    dbFuncs.toggleAdminKeyboard(action[0], True)
    bot.answer_callback_query(callback_query_id = query.id)
    return SETTINGS
  else:
    return pushAdmin(update, context)
  updateKeyboard(bot, action[0])
  bot.answer_callback_query(callback_query_id = query.id)
  return ConversationHandler.END

def pushAdmin(update, context):
  query, bot = update.callback_query, context.bot
  userid = query.from_user['id']
  _ = getTranslation(userid)
  if query.message:
    msgid = query.message.message_id
  else:
    msgid = query.inline_message_id
  action = query.data.split("_")
  if action[1] == Options[OptionsOrder[0]]:
    dbFuncs.toggleListOpen(action[0], not dbFuncs.isOpen(action[0]))
    bot.answer_callback_query(callback_query_id = query.id, text = _("listaccess").format(_("open") if dbFuncs.isOpen(action[0]) else _("closed")))
    if helpFuncs.isInt(msgid):
      bot.edit_message_reply_markup(chat_id = userid, message_id = msgid, reply_markup = createAdminKeyboard(action[0], userid))
    else:
      bot.edit_message_reply_markup(inline_message_id = msgid, reply_markup = createAdminKeyboard(action[0], userid))
  elif action[1] == Options[OptionsOrder[1]] or action[1] == Options[OptionsOrder[2]]:
    dbFuncs.sortList(action[0], action[1])
    bot.answer_callback_query(callback_query_id = query.id, text = _("itemsrearranged"))
  elif action[1] == Options[OptionsOrder[3]]:
    if helpFuncs.isInt(msgid):
      bot.edit_message_reply_markup(chat_id = userid, message_id = msgid, reply_markup = createKeyboard(action[0], userid))
    else:
      bot.edit_message_reply_markup(inline_message_id = msgid, reply_markup = createKeyboard(action[0], userid))
    dbFuncs.toggleAdminKeyboard(action[0])
    bot.answer_callback_query(callback_query_id = query.id)
    return ConversationHandler.END
  updateMessages(bot, action[0])
  return SETTINGS

def cancel(update, context):
  context.user_data.clear()
  return ConversationHandler.END

def getTranslation(userID, base = "main"):
  lang = dbFuncs.getUser(userID)[1]
  trans = gettext.translation(base, localedir = localeDir, languages = [lang])
  trans.install()
  return trans.gettext

def inlineQuery(update, context):
  query, user_data = update.inline_query, context.user_data
  userid = query.from_user['id']
  term = query.query
  _ = getTranslation(userid)
  ownLists = []
  user_data['tester'] = helpFuncs.id_generator(size = 5)
  if len(term) == 0:
    ownLists = dbFuncs.getOwnLists(userid)
  else:
    ownLists = dbFuncs.getLikelyLists("%{0}%".format(term), userid)
  resultList = []
  for list in ownLists:
    resultList.append(InlineQueryResultArticle(id = list[0], title = list[1], description = list[0], thumb_url = "http://icons.iconarchive.com/icons/google/noto-emoji-objects/1024/62930-clipboard-icon.png", reply_markup = createKeyboard(list[0], -1), input_message_content = InputTextMessageContent(message_text = listText(list[0]) + " `{0}`".format(user_data['tester']), parse_mode = 'Markdown', disable_web_page_preview = False)))
  query.answer(results = resultList, cache_time = 0, switch_pm_text = _("newlist"), switch_pm_parameter = "new")

@run_async
def chosenQuery(update, context):
  result, bot = update.chosen_inline_result, context.bot
  context.user_data['imid'] = result.inline_message_id
  dbFuncs.insertInlineMessage(result.result_id, result.inline_message_id)
  sleep(1)
  updateMessages(bot, result.result_id)

def createKeyboard(code, user, page = 0):
  keyboard = []
  items = dbFuncs.getItems(code)
  count = 0
  for item in items:
    temp = "◻"
    if item[3] == True:
      count += 1
      temp = "✅"
    keyboard.append([InlineKeyboardButton(text = "{0} {1}{2}".format(temp, item[2][:250], ''.join(["⠀" for _ in range(250-len(item[2]))])), callback_data = u"{0}_{1}_{2}".format(code, ListFooter["Check"], item[0]))])
    if dbFuncs.hasSubItems(item[0]):
      subitems = dbFuncs.getSubItems(item[0])
      for subitem in subitems:
        subtemp = "├"
        if subitem == subitems[-1]:
          subtemp = "└"
        temp2 = "◻"
        if subitem[3] == True:
          temp2 = "✅"
        subtemp += temp2
        keyboard.append([InlineKeyboardButton(text = "{0} {1}{2}".format(subtemp, subitem[2][:249], ''.join(["⠀" for _ in range(249-len(subitem[2]))])), callback_data = u"{0}_{1}_{2}".format(code, ListFooter["CheckSub"], subitem[0]))])
  if dbFuncs.isOwner(code, user):
    temp = "🗑"
    if count == 0 or count == len(items):
      temp = "📥"
    keyboard.append([InlineKeyboardButton(text = temp, callback_data = u"{0}_{1}".format(code, ListFooter["Remove"])),
      InlineKeyboardButton(text = "{0}".format(len(dbFuncs.getInlineMessages(code))), switch_inline_query = code),
      InlineKeyboardButton(text = "⚙", callback_data = "{0}_{1}".format(code, ListFooter["Options"]))])
  elif dbFuncs.isCoworker(code, user):
    keyboard.append([InlineKeyboardButton(text = "🏃", callback_data = "{0}_{1}".format(code, ListFooter["Exit"]))])
  if len(keyboard) == 0:
    keyboard.append([InlineKeyboardButton(text = "➕", url = "https://telegram.me/do2bot?start={0}".format(code))])
  return InlineKeyboardMarkup(keyboard)

def createAdminKeyboard(code, userid):
  keyboard = [[]]
  k = 2
  keyboard[-1].append(InlineKeyboardButton(text = OptionsOrder[0].format("👥" if dbFuncs.isOpen(code) else "👤"), callback_data = u"{0}_{1}".format(code, Options[OptionsOrder[0]])))
  for i in OptionsOrder[1:]:
    if k == 0:
      keyboard.append([])
      k = 3
    keyboard[-1].append(InlineKeyboardButton(text = i, callback_data = u"{0}_{1}".format(code, Options[i])))
    k-=1
  return InlineKeyboardMarkup(keyboard)

def listText(code):
  listDetails = dbFuncs.getList(code)
  text = u"📋 {0}, 🔗[/{1}](https://telegram.me/do2bot?start={1}), 👥 [{2}](tg://user?id={3})".format(listDetails[1], code, listDetails[3], listDetails[2])
  coworkers = dbFuncs.getCoworkers(code)
  for coworker in coworkers:
    text += u", [{0}](tg://user?id={1})".format(coworker[2], coworker[1])
  return text

def sendAll(update, context):
  message, bot = update.message, context.bot
  users = dbFuncs.getUsers()
  for user in users:
    try:
      bot.send_message(chat_id = user[0], text = message.text[len("/send "):])
    except Exception as e:
      logger.info(repr(e))

def main(updater):
  dispatcher = updater.dispatcher

  dbFuncs.initDB()

  newList = ConversationHandler(
    entry_points = [CommandHandler('new', new, Filters.private), CommandHandler('start', start, Filters.private, pass_args = True)],
    states = {
      SETNAME: [MessageHandler(Filters.text&Filters.private, setName)]
    },
    fallbacks = [CommandHandler('cancel', cancel, Filters.private, pass_user_data = True)]
  )

  listHandler = ConversationHandler(
    entry_points = [CallbackQueryHandler(pushInline)],
    states = {
      SETTINGS: [CallbackQueryHandler(pushAdmin)]
    },
    fallbacks = [CallbackQueryHandler(pushInline), CommandHandler('cancel', cancel, Filters.private, pass_user_data = True)],
    per_message = True
  )

  dispatcher.add_handler(newList)
  dispatcher.add_handler(listHandler)
  dispatcher.add_handler(CallbackQueryHandler(pushInline))
  dispatcher.add_handler(CommandHandler('send', sendAll, Filters.private&Filters.chat(chat_id = [114951690])))
  dispatcher.add_handler(CommandHandler('help', help, Filters.private))
  dispatcher.add_handler(CommandHandler('backup', backup, Filters.private))
  dispatcher.add_handler(InlineQueryHandler(inlineQuery))
  dispatcher.add_handler(ChosenInlineResultHandler(chosenQuery))
  dispatcher.add_handler(MessageHandler(Filters.private&Filters.regex(r'^\/.*'), blankCode))
  dispatcher.add_handler(MessageHandler(Filters.text&Filters.private&Filters.update.edited_message, editMessage))
  dispatcher.add_handler(MessageHandler(Filters.private&Filters.text&Filters.reply&(~Filters.update.edited_message), rcvReply))
  dispatcher.add_handler(MessageHandler(Filters.text&Filters.private&(~Filters.update.edited_message), rcvMessage))
  dispatcher.add_error_handler(contextCallback)


  try:
    with open('{0}/userdata'.format(backupsDir), 'rb') as file:
      dispatcher.user_data = pload(file)
  except Exception as e:
    logger.warning(repr(e))
  try:
    with open('{0}/newList'.format(backupsDir), 'rb') as file:
      newList.conversations = pload(file)
  except Exception as e:
    logger.warning(repr(e))
  try:
    with open('{0}/listHandler'.format(backupsDir), 'rb') as file:
      listHandler.conversations = pload(file)
  except Exception as e:
    logger.warning(repr(e))

  updater.start_polling()

  updater.idle()

  try:
    with open('{0}/userdata'.format(backupsDir), 'wb+') as file:
      pdump(dispatcher.user_data, file)
  except Exception as e:
    logger.warning(repr(e))
  try:
    with open('{0}/newList'.format(backupsDir), 'wb+') as file:
      pdump(newList.conversations, file)
  except Exception as e:
    logger.warning(repr(e))
  try:
    with open('{0}/listHandler'.format(backupsDir), 'wb+') as file:
      pdump(listHandler.conversations, file)
  except Exception as e:
    logger.warning(repr(e))


if __name__ == '__main__':
  from ..bottoken import getToken
  main(getToken(BOTTOKEN))
