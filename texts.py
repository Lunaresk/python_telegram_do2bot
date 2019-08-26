import gettext

def getText(lang, choice):
  trans = gettext.translation('texts', localedir = 'locales', languages = [lang, 'en'])
  trans.install()
  _ = trans.gettext
  if choice == "buttonlimit":
    return _("I wasn't able to insert every item due to restrictions in the length of the Inlinebuttons. I'm sorry.")
  elif choice == "closed":
    return _("Closed")
  elif choice == "confirmremove":
    return _("If you really want to close the list, press again.")
  elif choice == "help":
    return _("To create a new list, use /new. Then enter a title for this list. When you're done, you can send a list of things here and this bot will insert it to the list.\n"
            "The lower right button on the owner's list indicates whether the list is open or not. Only the owner can switch if the list is open."
            " When open, other people who enters the unique code of your list will be added as operator for your list."
            " This will grant them the possibility to add items to the list and recall the list with the inline function.\n\n"
            "If you need help with something specific, try this one out: `/help commands`\n\n"
            "This bot is usable via inline mode. To see a list of your current lists, just type the bots name in the chat like '`@do2bot `'.")
  elif choice == "helpbackup":
    return _("To make backups, use the /backup command. The bot then will take your stored lists and pack them in a .json file and send this one file to you." 
             " This function is also currently being developed, so there will be more functions to this soon.")
  elif choice == "helpcommands1":
    return _("If you need help with something specific, try /help with one of these commands:\n")
  elif choice == "helpcommands1":
    return _("\n\nFor example: /help support")
  elif choice == "helpcredits":
    return _("Creator: Lunaresk\nCoder: Lunaresk\nHoster: Lunaresk\nProfile Pic: Abdülkadir Coskun\n\nInspired by: @dotobot from @olebedev")
  elif choice == "helplimitations":
    return _("Due to the way Telegram creates and limits inline buttons, there can't be displayed more than 23 rows of buttons."
             " Therefore, I restricted the items per list to a maximum of 20 items.")
  elif choice == "helpnew":
    return _("If you want to make a new list, use the /new command or the inline function, type in what title you want and that's it.")
  elif choice == "helppermission":
    return _("This bot uses a permission system. Per default, nobody except you can modify a list."
             " To change this, you have to go to the list settings and press the upper left button (👤)"
             " and the ones you want to work on the list needs to press the corresponding link of the list you shared."
             " Please remember that as long as your list is marked as open, anyone with the link/code can join and manipulate it, so remember to close it again :)")
  elif choice == "helpsettings":
    return _("👤 means, that the list is currently closed and usage is restricted to the owner and users, who already joined the list."
             " Pushing this button will open the list for everyone and will change the icon to 👥.\n"
             "✅⬆ and ✅⬇ will reorder already done tasks to the top/bottom of the list, respectively.\n"
             "↩ to go back to the list.")
  elif choice == "helpshare":
    return _("Sharing a list is made with the inline function of telegram."
             " You can either use the middle button at the bottom of the list or type @do2bot and the name or the code of your list to find and send it.")
  elif choice == "helpsublist":
    return _("To create a sublist, you have to insert a single item first. Then, reply to this message you just sent and the items will be inserted as subitems for the previously inserted item."
             " Please note! Subitems are under the same restrictions as stated in '/help limitations'.")
  elif choice == "helpsupport":
    return _("This bot is open source and the code is available on GitHub. If you need help with anything or the GitHub link, please join @do2chat and ask the creator :3\n\n"
             "If you want to support me, you can do so by donating a bit via the following link:\nhttps://paypal.me/pools/c/8fWVnNBFaS for one-time donations.")
  elif choice == "insertname":
    return _("Please insert a name for the new list.")
  elif choice == "itemsrearranged":
    return _("List items rearranged")
  elif choice == "invalidargs":
    return _("The argument is invalid. The link provided for you might be incorrect. Please ask the owner of the list for the code of his list.")
  elif choice == "langselect":
    return _("Language selection")
  elif choice == "listaccess":
    return _("List access set to {0}")
  elif choice == "newlist":
    return _("Create new list")
  elif choice == "notallowed":
    return _("You're not allowed to do that.")
  elif choice == "notcreated":
    return _("I wasn't able to create a new list. I'm sorry, please try again.")
  elif choice == "notexisting":
    return _("The list you are searching for is not existing.")
  elif choice == "notopen":
    return _("The list you are searching is not open. Please contact the list owner.")
  elif choice == "notownedlists":
    return _("You own no lists. There is no need for a backup.")
  elif choice == "notspecified":
    return _("No list specified. Please choose one or create a list first.")
  elif choice == "notunique":
    return _("The message you replied to is not showing an unique item of your list. It is not clear which item I should append the subitems to.")
  elif choice == "open":
    return _("Open")
  elif choice == "listremoved":
    return _("List removed")
  elif choice == "revoked":
    return _("Revoked")
  elif choice == "settings":
    return _("Settings")
  elif choice == "tobeimplemented":
    return _("To be implemented")
  elif choice == "try":
    return _("Try it now")
  elif choice == "welcome":
    return _("Welcome to your new Do To Bot. This bot can be controlled via inline method. So just type '`@do2bot `' in your chat and wait a moment.")
  elif choice == "Language":
    return _("Language")
  elif choice == "Notification":
    return _("Notification")
  else:
    return choice
