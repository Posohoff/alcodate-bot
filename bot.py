import telebot
import os
import json
import requests
from datetime import datetime

# ---------------- TOKEN ----------------
TOKEN = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

# ---------------- LOAD UA HOLIDAYS ----------------
with open("holidays.json", "r", encoding="utf-8") as f:
    UA_HOLIDAYS = json.load(f)

# ---------------- UA API (official holidays) ----------------
def get_api_holidays(date_obj):
    year = date_obj.year
    url = f"https://date.nager.at/api/v3/PublicHolidays/{year}/UA"

    try:
        r = requests.get(url, timeout=5)
        data = r.json()

        target_date = date_obj.strftime("%Y-%m-%d")

        return [
            item["localName"]
            for item in data
            if item["date"] == target_date
        ]
    except:
        return []

# ---------------- INTERNATIONAL FALLBACK ----------------
def get_international(date_obj):
    key = date_obj.strftime("%d-%m")

    intl = {
        "14-02": ["День Святого Валентина ❤️", "International Book Giving Day 📚"],
        "21-03": ["International Day of Forests 🌳"],
        "22-03": ["World Water Day 💧"],
        "05-06": ["World Environment Day 🌍"],
        "21-09": ["International Day of Peace 🕊️"],
        "10-10": ["World Mental Health Day 🧠"]
    }

    return intl.get(key, [])

# ---------------- MAIN LOGIC ----------------
def get_holidays(date_obj):
    key = date_obj.strftime("%d-%m")

    results = []

    # UA JSON
    results += UA_HOLIDAYS.get(key, [])

    # API holidays
    results += get_api_holidays(date_obj)

    # International
    results += get_international(date_obj)

    if not results:
        results = ["Сьогодні немає офіційних свят, але день все одно хороший 🍀"]

    return results

# ---------------- START ----------------
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "Привіт! 🍻\n\nКоманди:\n/today - сьогодні\n/tomorrow - завтра\nАбо напиши дату (14-02)"
    )

# ---------------- TODAY ----------------
@bot.message_handler(commands=['today'])
def today(message):
    date = datetime.now()
    holidays = get_holidays(date)

    bot.send_message(
        message.chat.id,
        "📅 Сьогодні:\n\n" + "\n".join("• " + h for h in holidays)
    )

# ---------------- TOMORROW ----------------
@bot.message_handler(commands=['tomorrow'])
def tomorrow(message):
    from datetime import timedelta

    date = datetime.now() + timedelta(days=1)
    holidays = get_holidays(date)

    bot.send_message(
        message.chat.id,
        "📅 Завтра:\n\n" + "\n".join("• " + h for h in holidays)
    )

# ---------------- DATE INPUT ----------------
@bot.message_handler(content_types=['text'])
def handle_text(message):
    text = message.text.strip()

    # ignore commands
    if text.startswith("/"):
        return

    # normalize format
    text = text.replace(".", "-")

    try:
        date = datetime.strptime(text, "%d-%m")
        date = date.replace(year=datetime.now().year)
    except:
        return

    holidays = get_holidays(date)

    bot.send_message(
        message.chat.id,
        f"🔎 {text}:\n\n" + "\n".join("• " + h for h in holidays)
    )

# ---------------- RUN ----------------
print("Bot started...")
bot.infinity_polling()
