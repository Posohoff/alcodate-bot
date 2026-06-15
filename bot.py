import telebot
import os
import json
import requests
from datetime import datetime, timedelta

TOKEN = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

# ---------- LOCAL UA BASE ----------
with open("holidays.json", "r", encoding="utf-8") as f:
    UA_HOLIDAYS = json.load(f)

# ---------- API ----------
def get_api_holidays(date_obj):
    year = date_obj.year
    url = f"https://date.nager.at/api/v3/PublicHolidays/{year}/UA"

    try:
        r = requests.get(url, timeout=5)
        data = r.json()

        key = date_obj.strftime("%Y-%m-%d")

        return [
            item["localName"]
            for item in data
            if item["date"] == key
        ]
    except:
        return []

# ---------- INTERNATIONAL DAYS (fallback) ----------
def get_international(date_obj):
    month_day = date_obj.strftime("%d-%m")

    extra = {
        "14-02": ["International Book Giving Day 📚"],
        "21-03": ["International Day of Forests 🌳"],
        "22-03": ["World Water Day 💧"],
        "05-06": ["World Environment Day 🌍"],
        "21-09": ["International Day of Peace 🕊️"],
        "10-10": ["World Mental Health Day 🧠"]
    }

    return extra.get(month_day, [])

# ---------- CORE LOGIC ----------
def get_holidays(date_obj):
    key = date_obj.strftime("%d-%m")

    results = []

    # 1. UA local JSON
    results += UA_HOLIDAYS.get(key, [])

    # 2. API holidays
    results += get_api_holidays(date_obj)

    # 3. international days
    results += get_international(date_obj)

    if not results:
        results = ["Сьогодні немає офіційних свят, але день все одно хороший 🍀"]

    return results

# ---------- COMMANDS ----------
@bot.message_handler(commands=['start'])
def start(m):
    bot.send_message(m.chat.id, "Привіт! 🍻 Напиши /today або дату (25-12)")

@bot.message_handler(commands=['today'])
def today(m):
    date = datetime.now()
    holidays = get_holidays(date)

    text = "📅 Сьогодні:\n\n" + "\n".join("• " + h for h in holidays)
    bot.send_message(m.chat.id, text)

@bot.message_handler(commands=['tomorrow'])
def tomorrow(m):
    date = datetime.now() + timedelta(days=1)
    holidays = get_holidays(date)

    text = "📅 Завтра:\n\n" + "\n".join("• " + h for h in holidays)
    bot.send_message(m.chat.id, text)

@bot.message_handler(func=lambda m: True)
def date_input(m):
    text = m.text.strip().replace(".", "-")

    try:
        date = datetime.strptime(text, "%d-%m")
        date = date.replace(year=datetime.now().year)
    except:
        return

    holidays = get_holidays(date)

    reply = f"🔎 {text}:\n\n" + "\n".join("• " + h for h in holidays)
    bot.send_message(m.chat.id, reply)

print("Bot started...")
bot.infinity_polling()
