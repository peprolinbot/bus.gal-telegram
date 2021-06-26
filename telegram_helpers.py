import telegram
from telegram import KeyboardButton
from telegram import ReplyKeyboardMarkup
from telegram import InlineKeyboardButton
from telegram import InlineKeyboardMarkup
from telegram import ChatAction
from datetime import datetime
from functools import wraps

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

    longest_expedition_text = 0
    for expedition in expeditions:
        expedition_text = f"{expedition.origin.name}➡️{expedition.destination.name}"
        if len(expedition_text) > longest_expedition_text:
            longest_expedition_text = len(expedition_text)

    result = [""]
    page=0
    for expedition in expeditions:
        departure_str = expedition.departure.strftime("%H:%M")
        arrival_str = expedition.arrival.strftime("%H:%M")

        expedition_text = f"{expedition.origin.name}➡️{expedition.destination.name}"
        if len(expedition_text) < longest_expedition_text:
            for i in range((longest_expedition_text - len(expedition_text)) * 3):
                expedition_text += " "
        if len(result[page].encode("utf8")) > 4096 and page != 0:
            result.append("")
            page += 1
        result[page] += f"{expedition_text}    {departure_str}    {arrival_str}    *{expedition.code}* - {expedition.operator.name}    [Ruta]({expedition.url})\n\n" 
    spacing=""
    for i in range(longest_expedition_text):
        spacing+=" "
    spacing += "           " + "    "
    if result != [""]:
        result.insert(0, f"*Nombre{spacing}Salida    Llegada    Línea    Ruta*\n")
    else:
        result = None
    return result 
