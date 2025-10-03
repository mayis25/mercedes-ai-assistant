from telegram import Bot
import asyncio

# 🔑 ЗАМЕНИ НА СВОЙ ТОКЕН!
TOKEN = "7606597523:AAEsP5mcWb7vSg971B3WT-p9pu92BzFBEDc"

async def test():
    try:
        bot = Bot(TOKEN)
        me = await bot.get_me()
        print(f"✅ Бот работает! Имя: {me.first_name}")
        print(f"🔗 Ссылка: t.me/{me.username}")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

asyncio.run(test())