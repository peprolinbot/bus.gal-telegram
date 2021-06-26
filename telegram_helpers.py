import telegram
from telegram import KeyboardButton
from telegram import ReplyKeyboardMarkup
from telegram import InlineKeyboardButton
from telegram import InlineKeyboardMarkup
from telegram import ChatAction

from datetime import datetime

from functools import wraps

import prettytable

def send_typing_action(func):
    """Sends typing action while processing func command."""

    @wraps(func)
    def command_func(update, context, *args, **kwargs):
        context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=ChatAction.TYPING)
        return func(update, context,  *args, **kwargs)

    return command_func

#Sets up menus
class SimpleMenu:
    def __init__(self, bot, keyboard, presentation_text, state_function):
        self.bot = bot
        self.keyboard = keyboard
        self.keyboard_obj = ReplyKeyboardMarkup(keyboard)
        self.presentation_text = presentation_text
        self.state_function = state_function
    
    def send(self, update, context, presentation_text=None):
        if presentation_text == None:
            presentation_text = self.presentation_text
        if update.callback_query == None:
            self.bot.sendMessage(chat_id=update.effective_chat.id, text=presentation_text, parse_mode=telegram.ParseMode.MARKDOWN, reply_markup=self.keyboard_obj)
        else:
            update.callback_query.edit_message_text(text=presentation_text, parse_mode=telegram.ParseMode.MARKDOWN)
            self.bot.sendMessage(chat_id=update.effective_chat.id, text=self.presentation_text, parse_mode=telegram.ParseMode.MARKDOWN, reply_markup=self.keyboard_obj)
        self.state_function(update.effective_chat.id)

class UserSpecificMenu:
    def __init__(self, bot, button_text_list_function, presentation_text, state_function, extra_keyboard_at_start=[]):
        self.bot = bot
        self.button_text_list_function = button_text_list_function
        self.presentation_text = presentation_text
        self.state_function = state_function
        self.extra_keyboard_at_start = extra_keyboard_at_start
    
    def _get_keyboard_obj(self, userId):
        keyboard = [self.extra_keyboard_at_start]
        for button_text in self.button_text_list_function(userId):
            keyboard += [[KeyboardButton(button_text)]]
        keyboard_obj = ReplyKeyboardMarkup(keyboard)
        return keyboard_obj
    
    def send(self, update, context, presentation_text=None):
        if presentation_text == None:
            presentation_text = self.presentation_text
        keyboard_obj = self._get_keyboard_obj(update.effective_chat.id)
        self.bot.sendMessage(chat_id=update.effective_chat.id, text=presentation_text, parse_mode=telegram.ParseMode.MARKDOWN, reply_markup=keyboard_obj)
        self.state_function(update.effective_chat.id)


def generate_expeditions_message(expeditions):
    table = prettytable.PrettyTable()
    table.field_names = ["Origen", "Salida", "Destino", "Llegada", "Info"]

    for expedition in expeditions:
        table.add_row([expedition.origin.name, f"*{expedition.departure.strftime('%H:%M')}*", expedition.destination.name, f"*{expedition.arrival.strftime('%H:%M')}*", f"[Más info.]({expedition.url})\n"])
    
    table.border = False
    table.hrules = prettytable.NONE
    table.vrules = prettytable.NONE
    table.align = "l"

    header = table.get_string().split("Info")[0] + "Info"
    message_lines = table.get_string().split("Info")[1].split("\n")
    
    messages = [header, ""]
    message_number = 1 
    for line in message_lines:
        if len(messages[message_number].encode("utf8")) > 4096:
            message_number += 1
            messages.append("")
        messages[message_number] += "\n" + line
        
    return messages
