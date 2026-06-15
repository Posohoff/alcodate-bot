import telebot
from datetime import datetime
import os

TOKEN = os.environ.get("BOT_TOKEN")

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(
        message,
        "Привіт! 🍻\n\nНапиши /today щоб отримати список свят на сьогодні."
    )

@bot.message_handler(commands=['today'])
def today(message):
    today_date = datetime.now().strftime("%d.%m.%Y")

    text = f"""
📅 Сьогодні: {today_date}

🍺 Тестове свято:
• День гарного настрою
• День друзів
"""

    bot.reply_to(message, text)

print("Bot started...")
bot.infinity_polling()
