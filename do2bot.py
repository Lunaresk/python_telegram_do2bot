from telegram import (InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResult, InlineQueryResultArticle, InputTextMessageContent)
from telegram.ext import (CommandHandler, MessageHandler, RegexHandler, CallbackQueryHandler, ConversationHandler, InlineQueryHandler, ChosenInlineResultHandler, Filters)
from telegram.ext.dispatcher import run_async
from telegram.error import BadRequest
from time import sleep
from json import (load as jload, dump as jdump)
from pickle import (load as pload, dump as pdump)
from tempfile import NamedTemporaryFile
from ..errorCallback import contextCallback
from . import dbFuncs
from . import helpFuncs
import logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

SETNAME = range(1)
SETTINGS = range(1)
ListFooter = {"Check": "c", "Options": "o", "Remove": "r", "Exit": "e"}
Options = {"👤🔄👥": "open", "✅⬆": "sortUp", "✅⬇": "sortDn", "↩": "back"}
OptionsOrder = ["👤🔄👥", "✅⬆", "✅⬇", "↩"]
BOTTOKEN = 'do2bot'
backupsDir = "/home/shiro/gitProjects/telegramBots/do2bot/temp"

def start(update, context):
  message, args, bot, user_data = update.message, context.args, context.bot, context.user_data
  if len(args) == 0:
    message.reply_text("Welcome to your new Do To Bot. This bot can be controlled via inline method. So just type '`@do2bot `' in your chat and wait a moment.", parse_mode = 'Markdown', reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton(text = "Try it now", switch_inline_query_current_chat = "")]]))
  else:
    if len(args[0]) != 10:
      if args[0] == "new":
        return new(update, context)
      message.reply_text("The argument is invalid. The link provided for you might be incorrect. Please ask the owner of the list for the code of his list.")
    elif not dbFuncs.isAvailable(args[0]):
      message.reply_text("The list you are searching for is not existing.")
    elif not dbFuncs.isCoworker(args[0], message.from_user['id']):
      if dbFuncs.isOwner(args[0], message.from_user['id']):
        msgno = dbFuncs.getSpecificMessage(args[0], message.from_user['id'])[0]
        try:
          if helpFuncs.isInt(msgno):
            bot.edit_message_text(chat_id = message.chat_id, message_id = msgno, text = "↓")
          else:
            bot.edit_message_text(inline_message_id = msgno, text = "↓")
        except:
          print("Malicious message number")
        user_data['list'], user_data['current'] = args[0], message.reply_text(listText(args[0]), parse_mode = 'Markdown', disable_web_page_preview = True, reply_markup = createKeyboard(args[0], update.message.from_user['id'])).message_id
        dbFuncs.toggleAdminKeyboard(args[0])
        dbFuncs.updateOwner(args[0], user_data['current'])
      elif not dbFuncs.isOpen(args[0]):
        message.reply_text("The list you are searching is not open. Please contact the list owner.")
      else:
        user_data['list'], user_data['current'] = args[0], message.reply_text(listText(args[0]), parse_mode = 'Markdown', disable_web_page_preview = True, reply_markup = createKeyboard(args[0], message.from_user['id'])).message_id
        dbFuncs.insertCoworker(args[0], message.from_user['id'], message.from_user['first_name'], user_data['current'])
        updateMessages(bot, args[0])
    else:
      user_data['list'], user_data['current'] = args[0], message.reply_text(listText(args[0]), parse_mode = 'Markdown', disable_web_page_preview = True, reply_markup = createKeyboard(args[0], message.from_user['id'])).message_id
      bot.edit_message_text(chat_id = message.chat_id, message_id = dbFuncs.getSpecificMessage(args[0], message.from_user['id'])[0], text = "↓")
      dbFuncs.updateCoworker(args[0], message.from_user['id'], user_data['current'])
  return ConversationHandler.END

def help(update, context):
  message, args = update.message, context.args
  if len(args) == 0:
    message.reply_text("To create a new list, use /new. Then enter a title for this list. When you're done, you can send a list of things here and this bot will insert it to the list.\nThe lower right button on the owner's list indicates whether the list is open or not. Only the owner can switch if the list is open. When open, other people who enters the unique code of your list will be added as operator for your list. This will grant them the possibility to add items to the list and recall the list with the inline function.\n\nIf you need help with something specific, try this one out: `/help commands`\n\nThis bot is usable via inline mode. To see a list of your current lists, just type the bots name in the chat like '`@do2bot `'.", parse_mode = 'Markdown', reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton(text = "Try it now", switch_inline_query_current_chat = "")]]))
  else:
    message.reply_text(helpFuncs.getHelpText(args[0]))

def new(update, context):
  update.message.reply_text("Please insert a name for the new list.")
  return SETNAME

def setName(update, context):
  message, user_data = update.message, context.user_data
  for i in range(10):
    code = helpFuncs.id_generator()
    if not dbFuncs.isAvailable(code):
      break
  if dbFuncs.isAvailable(code):
    message.reply_text("I wasn't able to create a new list. I'm sorry, please try again.")
    return ConversationHandler.END
  dbFuncs.insertList(code, message.text, message.from_user['id'], message.from_user['first_name'])
  user_data['list'], user_data['current'] = code, message.reply_text(listText(code), parse_mode="Markdown", disable_web_page_preview = True, reply_markup = createKeyboard(code, message.from_user['id'])).message_id
  dbFuncs.updateOwner(code, user_data['current'])
  return ConversationHandler.END

def blankCode(update, context):
  context.args = [update.message.text[1:]]
  start(update, context)

@run_async
def rcvMessage(update, context):
  message, bot, user_data = update.message, context.bot, context.user_data
  tester = message.text[-5:]
  if 'tester' in user_data and user_data['tester'] == tester:
    user_data['list'] = message.text.split("/")[-1][:10]
    user_data['old'] = dbFuncs.getSpecificMessage(user_data['list'], message.from_user['id'])[0]
    if helpFuncs.isInt(user_data['old']):
      try:
        bot.edit_message_text(chat_id = message.from_user['id'], message_id = user_data['old'], text = '↓')
      except:
        pass
    else:
      try:
        bot.edit_message_text(inline_message_id = user_data['old'], text = '↓')
      except:
        pass
    count = 2
    while 'imid' not in user_data:
      sleep(1)
      count -= 1
      if count == 0:
        break
    try:
      dbFuncs.updateSpecificMessage(user_data['list'], message.from_user['id'], user_data['imid'])
      dbFuncs.removeInlineMessage(user_data['imid'])
    except:
      pass #TODO
  else:
    if 'list' not in user_data:
      message.reply_text("No list specified. Please choose one or create a list first.")
      return
    items = message.text.split("\n")
    dbFuncs.insertItems(user_data['list'], items, message.from_user['id'], message.message_id)
  updateMessages(bot, user_data['list'])
  temp = user_data['list']
  user_data.clear()
  user_data['list'] = temp

def editMessage(update, context):
  message, bot = update.edited_message, context.bot
  code = dbFuncs.editItems(message.text.split("\n"), message.from_user['id'], message.message_id)
  updateMessages(bot, code)

def updateMessages(bot, code):
  list = dbFuncs.getList(code)
  if not list[6]:
    try:
      if helpFuncs.isInt(list[4]):
        bot.edit_message_text(chat_id = list[2], message_id = list[4], text = listText(code), parse_mode = 'Markdown', disable_web_page_preview = True, reply_markup = createKeyboard(code, list[2]))
      else:
        bot.edit_message_text(inline_message_id = list[4], text = listText(code), parse_mode = 'Markdown', disable_web_page_preview = True, reply_markup = createKeyboard(code, list[2]))
    except BadRequest as error:
      if str(error) == "Message is not modified":
        pass #ummm... TODO
  coworkers = dbFuncs.getCoworkers(code)
  for coworker in coworkers:
    try:
      if helpFuncs.isInt(coworker[3]):
        bot.edit_message_text(chat_id = coworker[1], message_id = coworker[3], text = listText(code), parse_mode = 'Markdown', disable_web_page_preview = True, reply_markup = createKeyboard(code, coworker[1]))
      else:
        bot.edit_message_text(inline_message_id = coworker[3], text = listText(code), parse_mode = 'Markdown', disable_web_page_preview = True, reply_markup = createKeyboard(code, coworker[1]))
    except BadRequest as error:
      pass #ummm... TODO
  inlines = dbFuncs.getInlineMessages(code)
  for inline in inlines:
    try:
      bot.edit_message_text(inline_message_id = inline[1], text = listText(code), parse_mode = 'Markdown', disable_web_page_preview = True, reply_markup = createKeyboard(code, -1))
    except BadRequest as error:
      if str(error) == "Message_id_invalid":
        dbFuncs.removeInlineMessage(inline[1])

#TODO Future backup function, called with /backup
def backup(update, context):
  message, bot = update.message, context.bot
  lists = dbFuncs.getOwnedLists(message.from_user['id'])
  if len(lists[0]) == 0:
    message.reply_text("You own no lists. There is no need for a backup.")
  backuplist = []
  for list in lists:
    backuplist.append([])
    backuplist[-1].extend(list[1:4])
    backupitems = dbFuncs.getItems(list[0])
    backuplist[-1].append([])
    for item in backupitems:
      backuplist[-1][-1].append(item[2:4])
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
    if not list[6]:
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
  action = query.data.split("_")
  if not action[1] == ListFooter["Remove"]:
    user_data.pop('closing', None)
  if not (dbFuncs.isOwner(action[0], query.from_user['id']) or dbFuncs.isCoworker(action[0], query.from_user['id'])):
    bot.answer_callback_query(callback_query_id = query.id, text = "You are not allowed to do that.")
    return ConversationHandler.END
  if action[1] == ListFooter["Check"]:
    dbFuncs.updateItem(action[2])
  elif action[1] == ListFooter["Exit"]:
    bot.edit_message_text(chat_id = query.from_user['id'], message_id = dbFuncs.getSpecificMessage(action[0], query.from_user['id'])[0], text = "Revoked")
    dbFuncs.removeCoworker(action[0], query.from_user['id'])
    updateMessages(bot, action[0])
    bot.answer_callback_query(callback_query_id = query.id, text = "Left the list")
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
        bot.answer_callback_query(callback_query_id = query.id, text = "List removed")
      else:
        user_data['closing'] = action[0]
        bot.answer_callback_query(callback_query_id = query.id, text = "If you really want to close the list, press again.", show_alert = True)
      return ConversationHandler.END
  elif action[1] == ListFooter["Options"]:
    bot.edit_message_reply_markup(chat_id = query.from_user['id'], message_id = query.message.message_id, reply_markup = createAdminKeyboard(action[0], query.from_user["id"]))
    dbFuncs.toggleAdminKeyboard(action[0], True)
    return SETTINGS
  updateKeyboard(bot, action[0])
  bot.answer_callback_query(callback_query_id = query.id)
  return ConversationHandler.END

def pushAdmin(update, context):
  query, bot = update.callback_query, context.bot
  action = query.data.split("_")
  if action[1] == Options["👤🔄👥"]:
    dbFuncs.toggleListOpen(action[0], not dbFuncs.isOpen(action[0]))
    bot.answer_callback_query(callback_query_id = query.id, text = "List access set to {0}".format("Open" if dbFuncs.isOpen(action[0]) else "Closed"))
  elif action[1] == Options["✅⬆"] or action[1] == Options["✅⬇"]:
    dbFuncs.sortList(action[0], action[1])
    bot.answer_callback_query(callback_query_id = query.id, text = "List items rearranged")
  elif action[1] == Options["↩"]:
    bot.edit_message_reply_markup(chat_id = query.from_user['id'], message_id = query.message.message_id, reply_markup = createKeyboard(action[0], query.from_user["id"]))
    dbFuncs.toggleAdminKeyboard(action[0])
    return ConversationHandler.END
  updateMessages(bot, action[0])
  return SETTINGS

def cancel(update, context):
  context.user_data.clear()
  return ConversationHandler.END

def inlineQuery(update, context):
  query, user_data = update.inline_query, context.user_data
  term = query.query
  ownLists = []
  user_data['tester'] = helpFuncs.id_generator(size = 5)
  if len(term) == 0:
    ownLists = dbFuncs.getOwnLists(query.from_user['id'])
  else:
    ownLists = dbFuncs.getLikelyLists("%{0}%".format(term), query.from_user['id'])
  resultList = []
  for list in ownLists:
    resultList.append(InlineQueryResultArticle(id = list[0], title = list[1], description = list[0], thumb_url = "http://icons.iconarchive.com/icons/google/noto-emoji-objects/1024/62930-clipboard-icon.png", reply_markup = createKeyboard(list[0], -1), input_message_content = InputTextMessageContent(message_text = listText(list[0]) + " `{0}`".format(user_data['tester']), parse_mode = 'Markdown', disable_web_page_preview = False)))
  query.answer(results = resultList, cache_time = 0, switch_pm_text = "Create new list", switch_pm_parameter = "new")

@run_async
def chosenQuery(update, context):
  result = update.chosen_inline_result
  context.user_data['imid'] = result.inline_message_id
  dbFuncs.insertInlineMessage(result.result_id, result.inline_message_id)

def createKeyboard(code, user):
  keyboard = []
  items = dbFuncs.getItems(code)
  count = 0
  for item in items:
    temp = "◻"
    if item[3] == True:
      count += 1
      temp = "✅"
    keyboard.append([InlineKeyboardButton(text = "{0} {1}{2}".format(temp, item[2][:255], ''.join(["⠀" for _ in range(255-len(item[2]))])), callback_data = u"{0}_{1}_{2}".format(code, ListFooter["Check"], item[0]))])
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

def createAdminKeyboard(code, user):
  keyboard = []
  k = 0
  for i in OptionsOrder:
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
    fallbacks = [CallbackQueryHandler(pushInline)],
    per_message = True
  )

  dispatcher.add_handler(newList)
  dispatcher.add_handler(listHandler)
  dispatcher.add_handler(CommandHandler('help', help, Filters.private))
  dispatcher.add_handler(CommandHandler('backup', backup, Filters.private))
  dispatcher.add_handler(InlineQueryHandler(inlineQuery))
  dispatcher.add_handler(ChosenInlineResultHandler(chosenQuery))
  dispatcher.add_handler(MessageHandler(Filters.private&Filters.regex(r'^\/.*'), blankCode))
  dispatcher.add_handler(MessageHandler(Filters.text&Filters.private&(~Filters.update.edited_message), rcvMessage))
  dispatcher.add_handler(MessageHandler(Filters.text&Filters.private&Filters.update.edited_message, editMessage))
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
