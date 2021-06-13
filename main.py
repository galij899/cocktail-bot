import telebot
from telebot import types
import cocktail_api
import google_trends
import sqlite3

conn = sqlite3.connect('languages.db', check_same_thread=False)
cursor = conn.cursor()

try:
    query = "CREATE TABLE \"languages\" (\"chat_id\" INTEGER UNIQUE, \"language\" TEXT, PRIMARY KEY (\"chat_id\"))"
    cursor.execute(query)
except:
    pass

token = "1730668231:AAE5CQy_R0YOk2MjjzMMQuSSqMvMUXdXQEY"

bot = telebot.TeleBot(token)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.from_user.id, text="Hello, I am CocktailBot!")
    help_text = """You can ask anything by using a keyboard. Just click on buttons. For help type /help"""

    bot.send_message(message.from_user.id, text=help_text)
    send_keyboard(message.from_user.id)

@bot.message_handler(commands=['help'])
def help(message):
    help_text = """You can ask anything by using a keyboard. Just click on buttons.

I can:
· Random cocktail - suggest a random cocktail
· Search cocktail - find a cocktail by name or it's part
· Search by ingredient - find cocktails that contain it
· Get drink statistics - how often it is searched on the web
· Change language - select preferable recipe language (not bot's)"""

    bot.send_message(message.from_user.id, text=help_text)
    send_keyboard(message.from_user.id)


@bot.message_handler(content_types=["audio", "document", "photo", "sticker", "video", "video_note", "voice"])
def handle_text(message):
    send_keyboard(message, text="I don't know what you want, please use the keyboard")


def send_keyboard(chat_id, text="What can I get for you?"):
    keyboard = types.ReplyKeyboardMarkup(row_width=1)
    but1 = types.KeyboardButton('Random cocktail', )
    but2 = types.KeyboardButton('Search cocktail')
    but3 = types.KeyboardButton('Search by ingredient')
    but4 = types.KeyboardButton('Get drink statistics')
    but5 = types.KeyboardButton('Change language')
    but6 = types.KeyboardButton('Bye')
    keyboard.add(but1)
    keyboard.add(but2)
    keyboard.add(but3)
    keyboard.add(but4)
    keyboard.add(but5)
    keyboard.add(but6)

    msg = bot.send_message(chat_id,
                           text=text, reply_markup=keyboard)

    bot.register_next_step_handler(msg, callback_worker)


def search_results(msg):
    msg = show_results(msg)
    if msg:
        bot.register_next_step_handler(msg, search_callback)


def language_toggle(chat_id):
    lang = get_language(chat_id)
    language = lang if lang else "EN"

    keyboard = types.ReplyKeyboardMarkup(row_width=2)
    keyboard.add(types.KeyboardButton("EN"), row_width=1)
    keyboard.add(types.KeyboardButton("ES"), types.KeyboardButton("DE"))
    keyboard.add(types.KeyboardButton("FR"), types.KeyboardButton("IT"))

    msg = bot.send_message(chat_id, text=f"Your selected language is {language}", reply_markup=keyboard)
    bot.register_next_step_handler(msg, select_language)


def select_language(call):
    if call.text in ["EN", "ES", "DE", "FR", "IT"]:
        query = f"INSERT OR IGNORE INTO languages (chat_id, language) VALUES (\"{call.chat.id}\", \"{call.text}\");"
        cursor.execute(query)
        query2 = f"UPDATE languages SET language = \"{call.text}\" WHERE chat_id=\"{call.chat.id}\";"
        cursor.execute(query2)
        conn.commit()
        bot.send_message(call.chat.id, text=f"Now your language is set to {call.text}")
        bot.send_message(call.chat.id, text=f"Translation only applies on drink instructions (if not available, defaults to EN)")
    else:
        bot.send_message(call.chat.id, text=f"That language is not available, select from keyboard")
    send_keyboard(call.chat.id, text="Something else I can help you with?")


def get_language(chat_id):
    query = f"SELECT language FROM languages WHERE chat_id=={chat_id}"
    cursor.execute(query)
    lang = cursor.fetchone()
    return lang[0] if lang else "EN"


def search_results_by_ingredients(msg):
    results = cocktail_api.search_by_ingredient(msg.text)
    if not results:
        send_keyboard(msg.chat.id, text="Nothing was found")
        send_keyboard(msg.chat.id, text="Something else I can help you with?")
    else:
        keyboard = types.ReplyKeyboardMarkup(row_width=1)
        for res in results.keys():
            but = types.KeyboardButton(res)
            keyboard.add(but)

        text = "See what we've got!"

        msg = bot.send_message(msg.chat.id,
                               text=text, reply_markup=keyboard)

        bot.register_next_step_handler(msg, search_callback)


def search_callback(call):
    name, ingredients, instructions = cocktail_api.get_by_name(call.text, get_language(call.chat.id))
    bot.send_message(call.chat.id, f"Recipe for {name}")
    bot.send_message(call.chat.id, ingredients)
    bot.send_message(call.chat.id, instructions)
    send_keyboard(call.chat.id, text="Something else I can help you with?")


def show_results(msg):
    results = cocktail_api.search_by_name(msg.text)
    if not results:
        bot.send_message(msg.chat.id, text="Nothing was found")
        send_keyboard(msg.chat.id, text="Something else I can help you with?")
    else:
        keyboard = types.ReplyKeyboardMarkup(row_width=1)
        for res in results.keys():
            but = types.KeyboardButton(res)
            keyboard.add(but)

        text = "Select what exact cocktail you wanted"

        msg = bot.send_message(msg.chat.id,
                               text=text, reply_markup=keyboard)
        return msg

def statistic_select(msg):
    msg = show_results(msg)
    if msg:
        bot.register_next_step_handler(msg, statistics)


def statistics(msg):
    try:
        image, line1, line2 = google_trends.get_trends(msg.text)
        image.seek(0)
        bot.send_message(msg.chat.id, text=line1)
        bot.send_message(msg.chat.id, text=line2)
        bot.send_photo(msg.chat.id, image)
    except Exception:
        bot.send_message(msg.chat.id, text="Nothing was found, try again")
    send_keyboard(msg.chat.id, text="Something else I can help you with?")


def callback_worker(call):
    if call.text == "Random cocktail":
        try:
            name, ingredients, instructions = cocktail_api.get_random_cocktail(get_language(call.chat.id))
            bot.send_message(call.chat.id, f'You should definitely try {name}')
            bot.send_message(call.chat.id, ingredients)
            bot.send_message(call.chat.id, instructions)
        except Exception:
            bot.send_message(call.chat.id, text="Something went wrong, but I'm still here")
        send_keyboard(call.chat.id, text="Something else I can help you with?")
    elif call.text == "Search cocktail":
        msg = bot.send_message(call.chat.id, 'Type cocktail name')
        try:
            bot.register_next_step_handler(msg, search_results)
        except Exception:
            bot.send_message(call.chat.id, text="Something went wrong, but I'm still here")
            send_keyboard(call.chat.id, text="Something else I can help you with?")
    elif call.text == "Search by ingredient":
        msg = bot.send_message(call.chat.id, 'Type ingredient name')
        try:
            bot.register_next_step_handler(msg, search_results_by_ingredients)
        except Exception:
            bot.send_message(call.chat.id, text="Something went wrong, but I'm still here")
            send_keyboard(call.chat.id, text="Something else I can help you with?")
    elif call.text == "Get drink statistics":
        msg = bot.send_message(call.chat.id, 'Type cocktail name')
        try:
            bot.register_next_step_handler(msg, statistic_select)
        except Exception:
            bot.send_message(call.chat.id, text="Something went wrong, but I'm still here")
            send_keyboard(call.chat.id, text="Something else I can help you with?")
    elif call.text == "Change language":
        try:
            language_toggle(call.chat.id)
        except Exception:
            bot.send_message(call.chat.id, text="Something went wrong, but I'm still here")
            send_keyboard(call.chat.id, text="Something else I can help you with?")
    elif call.text == "Bye":
        bot.send_message(call.chat.id, text="Goodbye for now, to continue type /start")
    elif call.text == "/help":
        help(call)
    else:
        bot.send_message(call.chat.id, "I don't know what you want, please use the keyboard")
        send_keyboard(call.chat.id)


bot.polling(none_stop=True)
