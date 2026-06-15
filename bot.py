import telebot
import os
import json
from datetime import datetime, timedelta
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

# ---------- LOAD JSON ----------
with open("holidays.json", "r", encoding="utf-8") as f:
    HOLIDAYS = json.load(f)

# ---------- GET HOLIDAYS ----------
def get_holidays(date_obj):
    key = date_obj.strftime("%d-%m")  # стабільний формат
    return HOLIDAYS.get(key, ["Свят немає 😢"])

# ---------- MENU ----------
def main_menu():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("📅 Сьогодні", callback_data="today"))
    markup.add(InlineKeyboardButton("📆 Завтра", callback_data="tomorrow"))
    markup.add(InlineKeyboardButton("🔎 Дата", callback_data="date"))
    return markup

# ---------- START ----------
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "Привіт! 🍻\n\nОбери дію:",
        reply_markup=main_menu()
    )

# ---------- CALLBACK ----------
@bot.callback_query_handler(func=lambda call: True)
def callback(call):

    if call.data == "today":
        date = datetime.now()
        holidays = get_holidays(date)

        text = "📅 Сьогодні:\n\n" + "\n".join("• " + h for h in holidays)
        bot.send_message(call.message.chat.id, text)

    elif call.data == "tomorrow":
        date = datetime.now() + timedelta(days=1)
        holidays = get_holidays(date)

        text = "📆 Завтра:\n\n" + "\n".join("• " + h for h in holidays)
        bot.send_message(call.message.chat.id, text)

    elif call.data == "date":
        bot.send_message(call.message.chat.id, "Напиши дату у форматі 25-12")

# ---------- TEXT DATE ----------
@bot.message_handler(func=lambda m: True)
def handle_text(message):
    text = message.text.strip()

    try:
        date = datetime.strptime(text, "%d-%m")
    except:
        try:
            date = datetime.strptime(text, "%d.%m")
        except:
            return

    date = date.replace(year=datetime.now().year)

    holidays = get_holidays(date)

    text = f"🔎 {message.text}:\n\n" + "\n".join("• " + h for h in holidays)
    bot.send_message(message.chat.id, text)

    except:
        pass

# ---------- RUN ----------
print("Bot started...")
bot.infinity_polling()
