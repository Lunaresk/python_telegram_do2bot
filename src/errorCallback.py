from telegram.error import (TelegramError, Unauthorized, BadRequest, TimedOut, ChatMigrated, NetworkError)

def error_callback(bot, update, error):
  try:
    raise error
  except Unauthorized:
    print ('UnauthorizedError >> ' + str(error))
    # remove update.message.chat_id from conversation list
  except BadRequest:
    print ('BadRequestError >> ' + str(error))
    # handle malformed requests - read more below!
  except TimedOut:
    print ('TimedOutError >> ' + str(error))
    # handle slow connection problems
  except NetworkError:
    print ('NetworkError >> ' + str(error))
    # handle other connection problems
  except ChatMigrated as e:
    print ('ChatMigratedError >> ' + str(error))
    # the chat_id of a group has changed, use e.new_chat_id instead
  except TelegramError:
    print ('AnotherError >> ' + str(error))
    # handle all other telegram related errors

def contextCallback(update, context):
  error_callback(context.bot, update, context.error)
