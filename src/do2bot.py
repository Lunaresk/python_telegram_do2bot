import gettext
import logging

from json import (load as jload, dump as jdump)
from pickle import (load as pload, dump as pdump)
from sys import getsizeof
from telegram import (InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResult, InlineQueryResultArticle, InputTextMessageContent)
from telegram.ext import (Updater, CommandHandler, MessageHandler, RegexHandler, CallbackQueryHandler, ConversationHandler, InlineQueryHandler, ChosenInlineResultHandler, Filters)
from telegram.ext.dispatcher import run_async
from telegram.error import BadRequest
from time import sleep

from . import dbFuncs
from . import helpFuncs
from .errorCallback import contextCallback
from .classes.todolist import Todolist
from .classes.keyboard import Keyboard

logging.basicConfig(format='%(asctime)s - %(name)s - Function[%(funcName)s] - Line[%(lineno)s] - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

SETNAME = range(1)
SETTINGS, LANGUAGE, NOTIFICATION = range(3)
ListFooter = Keyboard.ListFooter
OptionsOrder = Keyboard.OptionsOrder
Options = Keyboard.Options
workingDir = "/home/lunaresk/gitProjects/telegramBots/do2bot"
backupsDir = workingDir + "/temp"
localeDir = workingDir + "/locales"
patterns = Keyboard.patterns

activelists = [] #For future speed boost

def start(update, context):
  logger.info("Start triggered")
  message, args, bot, user_data = update.message, context.args, context.bot, context.user_data
  userid = message.from_user['id']
  _ = getTranslation(userid)
  if not args:
    message.reply_text(_("welcome"), parse_mode = 'Markdown')
  else:
    if len(args[0]) != 10:
      if args[0] == "new":
        return new(update, context)
      message.reply_text(_("invalidargs"))
      return ConversationHandler.END
    try:
      todolist = Todolist(args[0])
    except KeyError as error:
      message.reply_text(_(str(error)))
    else:
      code = todolist.id
      if userid not in todolist.coworkers:
        if userid == todolist.owner:
          deleteMessages(bot, chatId = message.chat_id, messageId = dbFuncs.getSpecificMessage(code, userid)[0])
          user_data['list'], user_data['current'] = code, message.reply_text(str(todolist), parse_mode = 'Markdown', disable_web_page_preview = True, reply_markup = Keyboard.userKeyboard(todolist, userid)).message_id
          dbFuncs.toggleAdminKeyboard(code)
          dbFuncs.updateOwner(code, user_data['current'])
        elif not dbFuncs.isOpen(code):
          message.reply_text(_("notopen"))
        else:
          user_data['list'], user_data['current'] = code, message.reply_text(str(todolist), parse_mode = 'Markdown', disable_web_page_preview = True, reply_markup = Keyboard.userKeyboard(todolist, userid)).message_id
          todolist.addCoworker(userid, message.from_user['first_name'], user_data['current'])
          updateMessages(bot, todolist)
      else:
        user_data['list'], user_data['current'] = code, message.reply_text(str(todolist), parse_mode = 'Markdown', disable_web_page_preview = True, reply_markup = Keyboard.userKeyboard(todolist, userid)).message_id
        try:
          bot.delete_message(chat_id = message.chat_id, message_id = dbFuncs.getSpecificMessage(code, userid)[0])
        except Exception as e:
          try:
            bot.edit_message_text(chat_id = message.chat_id, message_id = dbFuncs.getSpecificMessage(code, userid)[0], text = "↓")
          except Exception as e2:
            logger.warn(repr(e2))
        dbFuncs.updateCoworker(code, userid, user_data['current'])
  return ConversationHandler.END

def help(update, context):
  message, args = update.message, context.args
  userid = message.from_user['id']
  if len(args) == 0:
    args = [""]
  message.reply_text(helpFuncs.getHelpText(args[0], getTranslation(userid, "help")), parse_mode = "Markdown")

def settings(update, context): #TODO Continue Settings
  message = update.message
  _ = getTranslation(message.from_user['id'])
  message.reply_text(_("settings"), reply_markup = Keyboard.settingsKeyboard())
  return SETTINGS

def settings_main(update, context):
  query, settings = update.callback_query, Keyboard.Settings
  action = getAction(query.data)[0]
  if action == settings['Language']:
    query.edit_message_text("Language Selection", reply_markup = Keyboard.languageKeyboard())
    query.answer()
    return LANGUAGE
  elif action == settings['Notifications']:
    query.answer("Not implemented yet. Stay tuned.")
  return SETTINGS

def settings_language(update, context):
  query, bot = update.callback_query, context.bot
  action = getAction(query.data)[0]
  userid = query.from_user['id']
  if not action == "back":
    dbFuncs.editUser(userid, action) #TODO Finish this
  query.edit_message_text(_("settings"), reply_markup = Keyboard.settingsKeyboard())
  return SETTINGS

def settings_notification(update, context):
  pass #TODO

def new(update, context):
  message = update.message
  _ = getTranslation(message.from_user['id'])
  message.reply_text(_("insertname"))
  return SETNAME

def setName(update, context):
  message, user_data = update.message, context.user_data
  try:
    newList = Todolist.new(message.text, message.from_user['id'], message.from_user['first_name'])
  except OverflowError as error:
    message.reply_text(str(error))
    return SETNAME
  except NameError as error:
    message.reply_text(str(error))
    return ConversationHandler.END
  except Exception as error:
    logger.warn(repr(error))
    return SETNAME
  user_data['list'], user_data['current'] = newList.id, message.reply_text(str(newList), parse_mode="Markdown", disable_web_page_preview = True, reply_markup = Keyboard.userKeyboard(newList, newList.owner.id)).message_id
  dbFuncs.updateOwner(newList.id, user_data['current'])
  return ConversationHandler.END

def blankCode(update, context):
  context.args = [update.message.text[1:]]
  start(update, context)

def deleteMessages(bot, chatId, messageId):
  if helpFuncs.isInt(messageId):
    try:
      bot.delete_message(chat_id = chatId, message_id = messageId)
    except Exception as e:
      try:
        bot.edit_message_text(chat_id = chatId, message_id = messageId, text = '↓')
      except Exception as e2:
        logger.info(repr(e2))
  else:
    privateInline = dbFuncs.getPrivateInline(messageId)
    if privateInline:
      try:
        bot.delete_message(chat_id = chatId, message_id = privateInline[1])
      except Exception as e:
        logger.info(repr(e))
      finally:
        dbFuncs.removePrivateInline(messageId)
    else:
      try:
        bot.edit_message_text(inline_message_id = messageId, text = '↓')
      except Exception as e2:
        logger.info(repr(e2))

@run_async
def rcvMessage(update, context):
  message, bot, user_data = update.message, context.bot, context.user_data
  userid = message.from_user['id']
  tester = message.text[-5:]
  if 'tester' in user_data and user_data['tester'] == tester:
    user_data['list'] = message.text.split("/")[-1][:10]
    todolist = Todolist(user_data['list'])
    user_data['old'] = dbFuncs.getSpecificMessage(user_data['list'], userid)[0]
    deleteMessages(bot, chatId = userid, messageId = user_data['old'])
    count = 2
    while 'imid' not in user_data and count != 0:
      sleep(1)
      count -= 1
    try:
      dbFuncs.updateSpecificMessage(user_data['list'], userid, user_data['imid'])
      dbFuncs.insertPrivateInline(user_data['imid'], message.message_id)
      dbFuncs.removeInlineMessage(user_data['imid'])
    except Exception as e:
      logger.info(repr(e))
    temp = user_data['list']
    user_data.clear()
    user_data['list'] = temp
    return
  else:
    _ = getTranslation(userid)
    if 'list' not in user_data:
      message.reply_text(_("notspecified"))
      return
    todolist = Todolist(user_data['list'])
    items = message.text.split("\n")
    try:
      todolist.addItems(items, userid, message.message_id)
    except StopIteration as error:
      message.reply_text(_("buttonlimit"))
  updateMessages(bot, todolist)

@run_async
def rcvReply(update, context):
  message, replymsg, bot = update.message, update.message.reply_to_message, context.bot
  userid, replyid = message.from_user['id'], replymsg.message_id
  _ = getTranslation(userid)
  items_from_reply = dbFuncs.getItemsByEdit(userid, replyid)
  if len(items_from_reply) > 1:
    message.reply_text(_("notunique"))
    return ConversationHandler.END
  corelist = Todolist(items_from_reply[0][1])
  items = message.text.split("\n")
  if not userid in corelist.coworkers and not userid == corelist.owner:
    message.reply_text(_("notallowed"))
    return ConversationHandler.END
  try:
    corelist.addSubItems(items_from_reply[0][0], items, userid, replyid)
  except StopIteration as error:
    message.reply_text(text = error)
  updateMessages(bot, corelist)

@run_async
def editMessage(update, context):
  message, bot = update.edited_message, context.bot
  if message.reply_markup:
    return
  try:
    code = dbFuncs.editItems(message.text.split("\n"), message.from_user['id'], message.message_id)
    updateMessages(bot, Todolist(code))
  except Exception as e:
    logger.info(repr(e))

def updateMessages(bot, todolist, msgtext = ""):
  inlinetext = msgtext
  if msgtext != "Closed":
    msgtext, inlinetext = str(todolist), repr(todolist)
  if not dbFuncs.getAdminTerminal(todolist.id):
    ownermsg = todolist.getMessage()
    try:
      if helpFuncs.isInt(ownermsg):
        bot.edit_message_text(chat_id = todolist.owner.id, message_id = ownermsg, text = msgtext, parse_mode = 'Markdown', disable_web_page_preview = True, reply_markup = (Keyboard.userKeyboard(todolist, todolist.owner.id) if msgtext != "Closed" else None))
      else:
        bot.edit_message_text(inline_message_id = ownermsg, text = msgtext, parse_mode = 'Markdown', disable_web_page_preview = True, reply_markup = (Keyboard.userKeyboard(todolist, todolist.owner.id) if msgtext != "Closed" else None))
    except BadRequest as error:
      if str(error) == "Message is not modified":
        logger.info(repr(error))
      else:
        logger.error(repr(error))
  if todolist.coworkers:
    for coworker in todolist.getCoMessages():
      try:
        if helpFuncs.isInt(coworker[1]):
          bot.edit_message_text(chat_id = coworker[0], message_id = coworker[1], text = msgtext, parse_mode = 'Markdown', disable_web_page_preview = True, reply_markup = (Keyboard.userKeyboard(todolist, coworker[0]) if msgtext != "Closed" else None))
        else:
          bot.edit_message_text(inline_message_id = coworker[1], text = msgtext, parse_mode = 'Markdown', disable_web_page_preview = True, reply_markup = (Keyboard.userKeyboard(todolist, coworker[0]) if msgtext != "Closed" else None))
      except BadRequest as error:
        logger.error(error) #ummm... TODO
  inlines = todolist.getInlineMessages()
  if inlines:
    for inline in inlines:
      try:
        bot.edit_message_text(inline_message_id = inline[1], text = inlinetext, parse_mode = 'Markdown', disable_web_page_preview = True, reply_markup = (Keyboard.userKeyboard(todolist, -1) if msgtext != "Closed" else None))
      except BadRequest as error:
        if str(error) == "Message_id_invalid":
          dbFuncs.removeInlineMessage(inline[1])
        else:
          logger.error(error)

@run_async
def backup(update, context):
  message, bot = update.message, context.bot
  userid = message.from_user['id']
  logger.info("Backing up lists for {}".format(userid))
  ownlists = dbFuncs.getOwnedLists(userid)
  if not ownlists:
    _ = getTranslation(userid)
    message.reply_text(_("notownedlists"))
  backuplist = []
  for ownlist in ownlists:
    backuplist.append(list(Todolist(ownlist[0])))
  with open('{0}/do2backup.json'.format(backupsDir), 'w+') as file:
    jdump(backuplist, file)
  with open('{0}/do2backup.json'.format(backupsDir), 'rb') as file:
    bot.send_document(chat_id = message.from_user['id'], document = file)

def backupSingle(bot, todolist):
  with open('{0}/do2backup.json'.format(backupsDir), 'w+') as file:
    jdump([list(todolist)], file)
  with open('{0}/do2backup.json'.format(backupsDir), 'rb') as file:
    bot.send_document(chat_id = todolist.owner.id, document = file)

#TODO Future restore function, called with /restore
def restore(update, context):
  pass

def getAction(querydata):
  action = querydata.split("_")
  action[0] = action[0].split(":")[1]
  return action

def pushInline(update, context):
  query, bot, user_data = update.callback_query, context.bot, context.user_data
  print(query.data)
  userid = query.from_user['id']
  _ = getTranslation(userid)
  action = getAction(query.data)
  logger.info(str(action))
  todolist = Todolist(action[0])
  if not action[1] == ListFooter["Remove"]:
    user_data.pop('closing', None)
  if not userid == todolist.owner and userid not in todolist.coworkers:
    query.answer(text = _("notallowed"))
    return ConversationHandler.END
  if action[1] == ListFooter["Check"]:
    if not todolist.toggleItem(int(action[2])):
      logger.warn("Item {} in list {} not toggled".format(action[2], action[0])) #Do something when this doesn't work
  elif action[1] == ListFooter["CheckSub"]:
    if not todolist.toggleSubItem(int(action[2])):
      logger.warn("Subitem {} in list {} not toggled".format(action[2], action[0])) #Do something when this doesn't work
  elif action[1] == ListFooter["Exit"]:
    query.edit_message_text(text = _("revoked"))
    todolist.deleteCoworker(userid)
    updateMessages(bot, todolist)
    query.answer(text = _("leftlist"))
    return ConversationHandler.END
  elif action[1] == ListFooter["Remove"]:
    check = False
    if todolist.items:
      temp = todolist.items[0].done
      for item in todolist.items:
        if item.done != temp:
          check = True
          break
    if check:
      todolist.deleteDones()
    else:
      if 'closing' in user_data and user_data['closing'] == action[0]:
        updateMessages(bot, todolist, "Closed")
        todolist.deleteList()
        query.answer(text = _("listremoved"))
      else:
        user_data['closing'] = action[0]
        query.answer(text = _("confirmremove"), show_alert = True)
      return ConversationHandler.END
  elif action[1] == ListFooter["Options"]:
    query.edit_message_reply_markup(reply_markup = Keyboard.adminKeyboard(action[0], userid))
    dbFuncs.toggleAdminKeyboard(action[0], True)
    query.answer()
    return SETTINGS
  else:
    return pushAdmin(update, context)
  updateMessages(bot, todolist)
  query.answer()
  return ConversationHandler.END

def pushAdmin(update, context):
  query, bot = update.callback_query, context.bot
  userid = query.from_user['id']
  _ = getTranslation(userid)
  action = getAction(query.data)
  todolist = Todolist(action[0])
  if action[1] == Options[OptionsOrder[0]]:
    dbFuncs.toggleListOpen(action[0], not dbFuncs.isOpen(action[0]))
    query.answer(text = _("listaccess").format(_("open") if dbFuncs.isOpen(action[0]) else _("closed")))
    query.edit_message_reply_markup(reply_markup = Keyboard.adminKeyboard(action[0], userid))
  elif action[1] == Options[OptionsOrder[1]] or action[1] == Options[OptionsOrder[2]]:
    dbFuncs.sortList(action[0], action[1])
    query.answer(text = _("itemsrearranged"))
  elif action[1] == Options[OptionsOrder[3]]:
    backupSingle(bot, todolist)
    return SETTINGS
  elif action[1] == Options[OptionsOrder[4]]:
    query.edit_message_reply_markup(reply_markup = Keyboard.userKeyboard(todolist, userid))
    dbFuncs.toggleAdminKeyboard(action[0])
    query.answer()
    return ConversationHandler.END
  updateMessages(bot, todolist)
  return SETTINGS

def cancel(update, context):
  context.user_data.clear()
  update.message.reply_text("Action cancelled")
  return ConversationHandler.END

#Might need to rework that. Again...
def getTranslation(userID, base = "main"):
  lang = dbFuncs.getUser(userID)[1]
  trans = gettext.translation(base, localedir = localeDir, languages = [lang])
  trans.install()
  return trans.gettext

#>>>>>KINDA REWROTE,NEED REVISION
@run_async
def inlineQuery(update, context):
  logger.info("Receiving inline query")
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
  threads = []
  listcodes = [x[0] for x in ownLists]
  logger.info("Retrieving lists")
  listobjects = []
  for listcode in listcodes:
    listobjects.append(Todolist(listcode))
  logger.info("Created {} Lists for Inline Query".format(len(listobjects)))
  for temp in listobjects:
    resultList.append(InlineQueryResultArticle(id = temp.id, title = temp.name, description = temp.id,
                                               thumb_url = "http://icons.iconarchive.com/icons/google/noto-emoji-objects/1024/62930-clipboard-icon.png",
                                               reply_markup = Keyboard.tempKeyboard(),
                                               input_message_content = InputTextMessageContent(message_text = repr(temp) + " `{0}`".format(user_data['tester']),
                                                                                               parse_mode = 'Markdown',
                                                                                               disable_web_page_preview = False)))
  logger.info("Appended to result lists. Answering query")
  query.answer(results = resultList, cache_time = 0, switch_pm_text = _("newlist"), switch_pm_parameter = "new")
  logger.info("Query answered")

@run_async
def chosenQuery(update, context):
  result, bot = update.chosen_inline_result, context.bot
  context.user_data['imid'] = result.inline_message_id
  logger.info("Inline Message ID equals {}".format(result.inline_message_id))
  dbFuncs.insertInlineMessage(result.result_id, result.inline_message_id)
  sleep(1)
  updateMessages(bot, Todolist(result.result_id))

def sendAll(update, context):
  message, bot = update.message, context.bot
  users = dbFuncs.getUsers()
  for user in users:
    try:
      bot.send_message(chat_id = user[0], text = message.text[len("/send "):])
    except Exception as e:
      logger.info(repr(e))

def fixButtons(update, context):
  query = update.callback_query
  if "_" in query.data:
    query.edit_message_reply_markup(Keyboard.userKeyboard(Todolist(query.data.split("_")[0]), query.message.chat.id))
  elif query.data in list(Keyboard.Options.values()):
    query.edit_message_reply_markup(Keyboard.adminKeyboard(query.data.split("_")[0], query.message.chat.id))
  elif query.data in list(Keyboard.Settings.values()):
    query.edit_message_reply_markup(Keyboard.settingsKeyboard())
  query.answer("Something went wrong. Please try again.")

def main(updater):
  dispatcher = updater.dispatcher

  dbFuncs.initDB()

  newcomm = CommandHandler('new', new, Filters.private)
  startcomm = CommandHandler('start', start, Filters.private, pass_args = True)
  cancelcomm = CommandHandler('cancel', cancel, Filters.private, pass_user_data = True)
  sendcomm = CommandHandler('send', sendAll, Filters.private&Filters.chat(chat_id = [114951690]))
  helpcomm = CommandHandler('help', help, Filters.private)
  backupcomm = CommandHandler('backup', backup, Filters.private)
  settingscomm = CommandHandler('settings', settings, Filters.private)
  pushinlinecall = CallbackQueryHandler(pushInline, pattern = r"^"+patterns[0])
  pushadmincall = CallbackQueryHandler(pushAdmin, pattern = r"^"+patterns[1])
  settingsmaincall = CallbackQueryHandler(settings_main, pattern = r"^"+patterns[2])
  settingslangcall = CallbackQueryHandler(settings_language, pattern = r"^"+patterns[3])
  setnamemess = MessageHandler(Filters.text&Filters.private, setName)
  blankcodemess = MessageHandler(Filters.private&Filters.regex(r'^\/.*'), blankCode)
  editmessagemess = MessageHandler(Filters.private&Filters.text&Filters.update.edited_message, editMessage)
  rcvreplymess = MessageHandler(Filters.private&Filters.text&Filters.reply&(~Filters.update.edited_message), rcvReply)
  rcvmessagemess = MessageHandler(Filters.private&Filters.text&(~Filters.update.edited_message), rcvMessage)

  newlistconv = ConversationHandler(
    entry_points = [newcomm, startcomm],
    states = {
      SETNAME: [setnamemess]
    },
    fallbacks = [cancelcomm],
    persistent = True, name = "newlist"
  )

  listhandlerconv = ConversationHandler(
    entry_points = [pushinlinecall],
    states = {
      SETTINGS: [pushadmincall]
    },
    fallbacks = [pushinlinecall, cancelcomm],
    persistent = True, name = "listhandler", per_message = True
  )

  settingshandlerconv = ConversationHandler(
    entry_points = [settingsmaincall],
    states = {
      SETTINGS: [settingsmaincall],
      LANGUAGE: [settingslangcall]
    },
    fallbacks = [cancelcomm],
    persistent = True, name = "settingshandler", per_message = True
  )

  dispatcher.add_handler(newlistconv)
  dispatcher.add_handler(listhandlerconv)
  dispatcher.add_handler(settingshandlerconv)
  dispatcher.add_handler(pushinlinecall)
  dispatcher.add_handler(CallbackQueryHandler(fixButtons))
  dispatcher.add_handler(sendcomm)
  dispatcher.add_handler(helpcomm)
  dispatcher.add_handler(backupcomm)
  dispatcher.add_handler(settingscomm)
  dispatcher.add_handler(InlineQueryHandler(inlineQuery))
  dispatcher.add_handler(ChosenInlineResultHandler(chosenQuery))
  dispatcher.add_handler(blankcodemess)
  dispatcher.add_handler(editmessagemess)
  dispatcher.add_handler(rcvreplymess)
  dispatcher.add_handler(rcvmessagemess)
  dispatcher.add_error_handler(contextCallback)

  updater.start_polling()

  updater.idle()
