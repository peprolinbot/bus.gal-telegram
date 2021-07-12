import telegram
from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler
from telegram.ext import CallbackQueryHandler
from telegram.ext import Filters
from telegram import KeyboardButton
from telegram import ReplyKeyboardMarkup
from telegram import InlineKeyboardButton
from telegram import InlineKeyboardMarkup

from sqlalchemy import and_, create_engine
from sqlalchemy.orm import sessionmaker

import os

from datetime import datetime

from time import sleep

import json

import busGal_api

from telegram_helpers import send_typing_action, SimpleMenu, UserSpecificMenu, generate_expeditions_message
import database

#Gets configuration values.
try:
    token = os.environ["BUS.GAL_TELEGRAM_TOKEN"]
    bot_name = os.environ["BUS.GAL_BOT_NAME"]
    db_path = os.environ["BUS.GAL_DATABASE_PATH"]
except KeyError:
    with open("config.json") as f:
        data = json.load(f)
    token = data["telegram_token"]
    bot_name = data["bot_name"]
    db_path = data["database_path"]

#Sets up the telegram bot
bot = telegram.Bot(token=token)
updater = Updater(bot.token, use_context=True, request_kwargs={'read_timeout': 6, 'connect_timeout': 7})

#Set up database
engine = create_engine(f"sqlite:///{db_path}")

database.Base.metadata.create_all(bind=engine)

Session = sessionmaker()
Session.configure(bind=engine)
session = Session()

def _set_state_to_main_menu(user_id):
    database.set_state(session, user_id, "main_menu")

main_menu = SimpleMenu(bot, [[KeyboardButton("♥️Paradas favoritas")],
                        [KeyboardButton("🔍Resultados")]], "❓Elige que quieres hacer:", _set_state_to_main_menu)

def _get_favorite_stops_names(user_id):
    names = []
    for stop in database.get_favorite_stops(session, user_id):
        names.append(stop.name)
    return names

def _set_state_to_favorites_menu(user_id):
    database.set_state(session, user_id, "favorites_menu")

all_favorite_stops_menu = UserSpecificMenu(bot, _get_favorite_stops_names, "❓Elige una parada:", _set_state_to_favorites_menu, [KeyboardButton("⬅️Atrás")])

def start(update, context): #Start command. Presents itself and sends an in-keyboard menu
    if database.get_user(session, update.effective_chat.id) is None:
        database.add_user(session, update.effective_chat.id)
    msg = "¡Hola!👋 soy " + bot_name + ", y puedo ayudarte a buscar los horarios para los buses del Transporte Público de Galicia, para información sobre el origen de los datos usa /about. Usa el menu de tú teclado o escribe /help para ver los comandos disponibles."
    main_menu.send(update, context, msg)

def help(update, context): #Help command. Tells what does each command
    context.bot.sendMessage(chat_id=update.effective_chat.id, parse_mode=telegram.ParseMode.MARKDOWN, text='''❓ *Ayuda e información* ❓
👉*Uso básico*
Manda el nombre de una parada o escoge una de tu lsita de favoritas para eligirla como origen y repite para poner otra como destino. En caso de que desees una fecha diferente al día de hoy usa /setdate Día-mes-año, ej. /setdate 27-02-2020. Y recibe los resultados con /result o pulsando el botón 🔍*Resultados*.
👉*Guardar paradas*
Puedes guardar tus paradas favoritas o más usadas en una lista que podrás consultar posteriormente. Para guardar una parada, búscala primero, y a continuación, pulsa sobre el botón *Añadir a favoritos*♥️, justo debajo del mensaje recibido.
Para ver tus paradas guardadas, pulsa en paradas favoritas en el menú de tu teclado. Todas tus paradas guardadas aparecerán en forma de botones, y pulsando sobre ellas podrás eligirlas como origen o destino.
Cuando hagas click sobre una parada, puedes eliminarla haciendo click en el botón *Quitar de favoritos*❌.
ℹ️*Lista completa de comandos disponibles*
🔸/search: Es más cómodo enviar el nombre de una parada directamente, aunque también funciona enviarla como argumento de este comando
🔸/result: Muestra las rutas disponibles con los parámetros especificados
🔸/setdate: Fija la fecha del día del que quieres obtener los horarios de buses
🔸/clear: Borra el destino, origen y fecha que hayas fijado para la ruta
🔸/eraseall: Borra todos tus datos (paradas favoritas) de la base de datos del bot
🔸/help: Este comando🙃
🔸/about: Información sobre el bot
🔸/donate: ¿Cómo puedes colaborar con el mantenimiento de este bot?''')

def about(update, context): #/about command
    context.bot.sendMessage(chat_id=update.effective_chat.id, parse_mode=telegram.ParseMode.MARKDOWN, disable_web_page_preview=True, text='''
🚍*Bus.gal Bot*🚍 es un bot no oficial para consultar las paradas y autobuses de la web bus.gal, los mismos que en la aplicación _Transporte Público de Galicia_ ([Play Store](https://play.google.com/store/apps/details?id=gal.xunta.transportepublico))([App Store](https://itunes.apple.com/es/app/transporte-p%C3%BAblico-de-galicia/id1244036417)), desde Telegram. Se trata de un proyecto personal escrito en Python, de código abierto y sin ánimo de lucro.
*La información proporcionada por este bot puede no ser exacta al 100%* por motivos técnicos propios o ajenos, por lo que su uso no ofrece ninguna garantía.
Creado en Ferrol con ❤️, [Python](https://www.python.org/), [python-telegram-bot](https://python-telegram-bot.org/), [SQLAlchemy](https://www.sqlalchemy.org/), [bus.gal-api](https://github.com/peprolinbot/bus.gal-api)(creada por mí 🙃) y otras fantásticas herramientas y librerías. Inspirado en [VigoBusBot](https://t.me/vigobusbot).
😺[Repositorio GitHub del proyecto](https://github.com/peprolinbot/bus.gal-telegram)
☕️¡Ayuda a mantener este bot en funcionamiento! /donate
_Este proyecto no cuenta con soporte de, no está afiliado con, mantenido por, patrocinado por ni de cualquier otra manera oficialmente conectado con la Xunta de Galicia, los operadores de autobuses o cualquiera de las empresas involucradas en la página web_ [bus.gal](https://www.bus.gal/)_ y su respectiva_ [aplicación](https://play.google.com/store/apps/details?id=gal.xunta.transportepublico)_._''')

def donate(update, context):
    context.bot.sendMessage(chat_id=update.effective_chat.id, parse_mode=telegram.ParseMode.MARKDOWN, disable_web_page_preview=True, text='''
☕️*¡Se necesitan donaciones!*☕️
Al contrario que muchas de las aplicaciones para móvil que existen para ver los horarios de los autobuses, los bots de Telegram necesitan funcionar en un servidor de forma constante para que puedan ser utilizados por el público.
Además, ciertas aplicaciones no oficiales, sin sufrir ningún gasto en servidores ni mantenimiento, contienen anuncios y publicidad embebida, que este bot no incluye de ninguna de sus maneras.
Cualquier aportación es de gran ayuda para sufragar el coste que supone mantener el servidor y, por tanto, el bot en funcionamiento, y así mantener este y otros proyectos a flote.
😊¡Gracias!
[PayPal](https://www.paypal.me/peprolinbot)
[BuyMeACofee](https://www.buymeacoffee.com/peprolinbot)
    ''')

@send_typing_action
def result(update, context): #/result command
    expedition = database.get_expedition(session, update.effective_chat.id)
    if expedition is None or expedition.origin is None:
        context.bot.sendMessage(chat_id=update.effective_chat.id, text="❌No se espicificó la ruta. Hazlo con el menú del teclado o mandándome el nombre de una parada. Para más información manda /help")
        return
    elif expedition.destination is None:
        context.bot.sendMessage(chat_id=update.effective_chat.id, text="❌No se espicificó la ruta al completo. Pon un destino usando el menú del teclado o mandándome el nombre de una parada. Para más información manda /help")
        return

    trip = busGal_api.Trip(expedition.origin, expedition.destination, expedition.date or datetime.now())
    expeditions = trip.expeditions
    database.delete_expedition(session, update.effective_chat.id)
    database.delete_all_cached_stops(session, update.effective_chat.id)
    if trip.expeditions == []:
        context.bot.sendMessage(chat_id=update.effective_chat.id, text="❌No se encontró ninguna ruta con los parámetros especificados😭")
    else:
        result = generate_expeditions_message(expeditions)
        for msg in result:
            context.bot.sendMessage(chat_id=update.effective_chat.id, text=msg, parse_mode=telegram.ParseMode.MARKDOWN)

def _text_manager(update, context):
    state = database.get_state(session, update.effective_chat.id)
    if state == "search_menu" or state == "favorites_menu":
        stop = None
        for favorite_stop in database.get_favorite_stops(session, update.effective_chat.id):
            if favorite_stop.name == update.message.text:
                stop = favorite_stop
                break
        if stop is None:
            stop = None
            for cached_stop in database.get_cached_stops(session, update.effective_chat.id):
                if cached_stop.name == update.message.text:
                    stop = cached_stop
                    break
            if stop is None:
                search(update, context)
                return
            else:
                favorite_button_text = "Añadir a favoritos♥️"
                favorite_button_callback = "add_favorite;" + str(stop.id)
        else:
            favorite_button_text = "Quitar de favoritos❌"
            favorite_button_callback = "rm_favorite;" + str(stop.id)
        database.add_cached_stop(session, update.effective_chat.id, stop)
        keyboard = [[InlineKeyboardButton(favorite_button_text, callback_data=favorite_button_callback)], [InlineKeyboardButton("Seleccionar parada📍", callback_data="select;" + str(stop.id))]]
        keyboard_obj = InlineKeyboardMarkup(keyboard)
        bot.send_message(chat_id=update.effective_chat.id, text="❓¿Qué quieres hacer con esta parada?", reply_markup=keyboard_obj)
    else:
        search(update, context)

def _callback_query_handler(update, context):
    query = update.callback_query
    query.answer()
    action = query.data.split(";")[0]
    arg = query.data.replace(action+';', '', 1)
    for cached_stop in database.get_cached_stops(session, update.effective_chat.id):
        if str(cached_stop.id) == arg:
            stop = cached_stop
            break
    if action == "select":
        _select_stop(update, context, stop)
    elif action == "add_favorite":
        database.add_favorite_stop(session, update.effective_chat.id, stop)
        main_menu.send(update, context, presentation_text="✅Parada *añadida* a favoritos.")
    elif action == "rm_favorite":
        database.delete_favorite_stop(session, update.effective_chat.id, stop)
        main_menu.send(update, context, presentation_text="✅Parada *eliminada* de favoritos.")

@send_typing_action
def search(update, context):
    query = update.message.text
    if query.split()[0] == "/search":
        query = ' '.join(query.split()[1:])

    stops = busGal_api.search_stop(query)
    database.add_multiple_cached_stops(session, update.effective_chat.id, stops)
    if stops == []:
        bot.send_message(chat_id=update.effective_chat.id, text="❌No se encontraron paradas para tu búsqueda😭")
        return
    keyboard = [[KeyboardButton("⬅️Atrás")]]
    for stop in stops:
        keyboard += [[KeyboardButton(stop.name)]]

    def _set_state_to_search_menu(user_id):
        database.set_state(session, user_id, "search_menu")

    results_menu = SimpleMenu(bot, keyboard, "✅Estos son los resultados de tu búsqueda:", _set_state_to_search_menu)
    results_menu.send(update, context)

def _select_stop(update, context, stop):
    expedition = database.get_expedition(session, update.effective_chat.id)
    if expedition is None or expedition.origin is None:
        database.insert_to_expedition(session, update.effective_chat.id, origin=stop)
        main_menu.send(update, context, presentation_text="✅Parada *fijada* como origen.")
    elif expedition.destination is None:
        database.insert_to_expedition(session, update.effective_chat.id, destination=stop)
        main_menu.send(update, context, presentation_text="✅Parada *fijada* como destino.\nUsa /result o el botón 🔍*Resultados* para ver los viajes disponibles.\n\nSi no quieres las paradas para el día de hoy, selecciona la fecha con /setdate Día-mes-año.")
    else:
        main_menu.send(update, context, presentation_text="❌Ya has puesto todos los valores. Para las fechas se usa /setdate.")

def select_date(update, context, date=None):
    date = update.message.text.split()[1:]
    date= ' '.join(date)
    space_char = ''.join([i for i in date if not i.isdigit()])[0]
    date = date.replace(space_char, "-")
    date = datetime.strptime(date, "%d-%m-%Y")

    database.insert_to_expedition(session, update.effective_chat.id, date=date)

    bot.send_message(chat_id=update.effective_chat.id, text="✅Fecha fijada.\nUsa /result o el botón 🔍*Resultados* para ver los viajes disponibles",  parse_mode=telegram.ParseMode.MARKDOWN)

def clear_expedition(update, context):
    database.delete_expedition(session, update.effective_chat.id)
    bot.send_message(chat_id=update.effective_chat.id, text="✅*Eliminada* la ruta actual.", parse_mode=telegram.ParseMode.MARKDOWN)

def erase_all(update, context):
    database.delete_everything_from_user(session, update.effective_chat.id)
    database.add_user(session, update.effective_chat.id) # This is needed to prevents errors if the user decides to use again the bot without running /start
    bot.send_message(chat_id=update.effective_chat.id, text="✅*Borrado*. Ya no sé nada sobre tí.🙃", parse_mode=telegram.ParseMode.MARKDOWN)

#Defining handlers
start_handler = CommandHandler('start', start)
help_handler = CommandHandler('help', help)
about_handler = CommandHandler('about', about)
donate_handler = CommandHandler('donate', donate)
erase_all_handler = CommandHandler('eraseall', erase_all)
select_date_handler = CommandHandler('setdate', select_date)
search_handler = CommandHandler('search', search)
result_handler = CommandHandler('result', result)
clear_handler = CommandHandler('clear', clear_expedition)

btn_search_buses_handler = MessageHandler(Filters.regex(r"^"+"🔍Resultados"+"$"), result)
btn_favorite_stops_handler = MessageHandler(Filters.regex(r"^"+"♥️Paradas favoritas"+"$"), all_favorite_stops_menu.send)
btn_back_handler = MessageHandler(Filters.regex(r"^"+"⬅️Atrás"+"$"), main_menu.send)
all_msg_handler = MessageHandler(Filters.all, _text_manager)

callback_query_handler = CallbackQueryHandler(_callback_query_handler)

dispatcher = updater.dispatcher

import logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)

#Adding handlers
dispatcher.add_handler(start_handler)
dispatcher.add_handler(help_handler)
dispatcher.add_handler(about_handler)
dispatcher.add_handler(donate_handler)
dispatcher.add_handler(erase_all_handler)
dispatcher.add_handler(select_date_handler)
dispatcher.add_handler(search_handler)
dispatcher.add_handler(result_handler)
dispatcher.add_handler(clear_handler)
dispatcher.add_handler(btn_search_buses_handler)
dispatcher.add_handler(btn_favorite_stops_handler)
dispatcher.add_handler(btn_back_handler)
dispatcher.add_handler(all_msg_handler)
dispatcher.add_handler(callback_query_handler)

updater.start_polling()
