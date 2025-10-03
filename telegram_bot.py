import logging
import wikipedia
import requests
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Токен бота
BOT_TOKEN = "7606597523:AAEsP5mcWb7vSg971B3WT-p9pu92BzFBEDc"

# Настройка
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
wikipedia.set_lang("ru")
wikipedia.set_rate_limiting(False)  # Отключаем лимиты

# Команда /start
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = """
🚗 *Добро пожаловать в ИИ-бот Mercedes-Benz!*

Я ваш интеллектуальный помощник по автомобилям Mercedes-Benz!

*Просто напишите любой вопрос про Mercedes:*
• "G-class" или "гелик"
• "S-class" или "эска"
• "E-class" или "ешка" 
• "C-class" или "цешка"
• "AMG" или "амега"
• "EQS" или "электрический мерседес"
• "GLC" или "гэлэс"
• "GLE" или "гэлэе"

*Я быстро найду информацию и покажу вам!*
    """
    await update.message.reply_text(welcome_text, parse_mode='Markdown')

# Быстрая база данных Mercedes (мгновенный ответ)
def get_instant_mercedes_info(query):
    query_lower = query.lower().strip()
    
    # База данных с мгновенными ответами
    mercedes_db = {
        # G-Class
        'g-class': """🚙 *Mercedes-Benz G-Class (Гелик)*

*Цена:* от 12 900 000 ₽
*Поколения:* W460, W461, W463
*Двигатели:* 2.0L - 4.0L V8 (до 585 л.с.)
*Привод:* полный 4MATIC
*Особенности:* рамная конструкция, 3 блокируемых дифференциала

*История:* Легендарный внедорожник с 1979 года, символ роскоши и проходимости.""",

        'гелик': """🚙 *Mercedes-Benz G-Class (Гелик)*

*Цена:* от 12 900 000 ₽
*Мощность:* до 585 л.с. (G63 AMG)
*Разгон:* 4.5 сек до 100 км/ч
*Расход:* 13-16 л/100km

*Комплектации:* G350d, G500, G63 AMG""",

        # S-Class
        's-class': """🚗 *Mercedes-Benz S-Class (Эска)*

*Цена:* от 8 900 000 ₽
*Поколения:* W223, W222, W221
*Двигатели:* 2.9L - 4.0L V8 (до 612 л.с.)
*Технологии:* DRIVE PILOT, MBUX Hyperscreen

*Флагман:* Эталон роскоши и технологий с 1972 года.""",

        'эска': """🚗 *Mercedes-Benz S-Class (Эска)*

*Цена:* от 8 900 000 ₽
*Длина:* 5179-5469 мм
*Особенности:* массажные кресла, автопилот, система комфорта

*Модели:* S350d, S450, S500, S580, S680""",

        # E-Class
        'e-class': """🚘 *Mercedes-Benz E-Class (Ешка)*

*Цена:* от 5 200 000 ₽
*Поколения:* W214, W213, W212
*Двигатели:* 2.0L - 3.0L (до 381 л.с.)
*Класс:* бизнес-седан

*Популярность:* Одна из самых продаваемых моделей Mercedes.""",

        'ешка': """🚘 *Mercedes-Benz E-Class (Ешка)*

*Цена:* от 5 200 000 ₽
*Кузова:* седан, универсал, купе
*Особенности:* двойной экран, полуавтономное вождение

*Комплектации:* E200, E300, E450, E53 AMG""",

        # C-Class
        'c-class': """🚖 *Mercedes-Benz C-Class (Цешка)*

*Цена:* от 3 800 000 ₽
*Поколения:* W206, W205
*Двигатели:* 1.5L - 3.0L (до 390 л.с.)
*Класс:* компактный представительский

*Дизайн:* Спортивный и элегантный.""",

        'цешка': """🚖 *Mercedes-Benz C-Class (Цешка)*

*Цена:* от 3 800 000 ₽
*Разгон C43 AMG:* 4.6 сек до 100 км/ч
*Технологии:* MBUX, цифровая приборная панель

*Модели:* C180, C200, C300, C43 AMG""",

        # AMG
        'amg': """🏎️ *Mercedes-AMG (Амега)*

*Цены:* от 6 500 000 ₽
*Основан:* 1967 год
*Модели:* C63, E63, G63, GT
*Мощность:* до 831 л.с. (GT Black Series)

*Философия:* "Один человек - один двигатель".""",

        'амега': """🏎️ *Mercedes-AMG (Амега)*

*Спортивные версии:*
• C63 AMG - 476 л.с.
• E63 AMG - 612 л.с. 
• G63 AMG - 585 л.с.
• GT 63 S - 639 л.с.""",

        # EQS
        'eqs': """⚡ *Mercedes-Benz EQS*

*Цена:* от 9 500 000 ₽
*Запас хода:* до 770 км
*Мощность:* до 524 л.с.
*Разгон:* 4.3 сек до 100 км/ч

*Технологии:* MBUX Hyperscreen, автопилот, рекуперация.""",

        # GLC
        'glc': """🚙 *Mercedes-Benz GLC*

*Цена:* от 4 500 000 ₽
*Класс:* компактный кроссовер
*Объем багажника:* 550 литров
*Привод:* 4MATIC

*На базе:* C-Class""",

        # GLE
        'gle': """🚙 *Mercedes-Benz GLE*

*Цена:* от 6 800 000 ₽
*Класс:* среднеразмерный кроссовер
*Двигатели:* бензин, дизель, гибрид
*Особенности:* просторный салон, E-ACTIVE BODY CONTROL""",

        # Общие запросы
        'мерседес': """🚗 *Mercedes-Benz*

*Основан:* 1926 год
*Штаб-квартира:* Штутгарт, Германия
*Основатели:* Карл Бенц, Готлиб Даймлер

*Современный модельный ряд:*
• Седаны: A, C, E, S-Class
• Внедорожники: GLA, GLB, GLC, GLE, GLS, G-Class
• Электромобили: EQA, EQB, EQC, EQE, EQS
• Спортивные: AMG серии""",

        'мерс': """🚗 *Mercedes-Benz*

*Лозунг:* "Лучшее или ничего"
*Инновации:* Первый автомобиль (1886), ABS, ESP, подушки безопасности

*Текущие технологии:*
• MBUX - мультимедийная система
• 4MATIC - полный привод
• DRIVE PILOT - автопилот
• ENERGIZING - система комфорта"""
    }
    
    # Ищем точное совпадение
    if query_lower in mercedes_db:
        return mercedes_db[query_lower], None
    
    # Ищем частичное совпадение
    for key, value in mercedes_db.items():
        if key in query_lower:
            return value, None
    
    # Если не нашли в базе, используем быстрый поиск
    return fast_wikipedia_search(query)

# Быстрый поиск в Wikipedia
def fast_wikipedia_search(query):
    try:
        # Быстрый поиск только заголовка и краткого описания
        search_results = wikipedia.search(query, results=1)
        if not search_results:
            return "❌ Информация не найдена. Попробуйте другой запрос.", None
        
        page_title = search_results[0]
        # Берем только 3 предложения для скорости
        summary = wikipedia.summary(page_title, sentences=3)
        
        return f"🔍 *{page_title}*\n\n{summary}", None
        
    except Exception as e:
        return f"🔍 *{query}*\n\nК сожалению, не удалось найти подробную информацию. Попробуйте уточнить запрос.", None

# Обработчик сообщений
async def handle_all_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text.strip()
    
    if user_message.startswith('/'):
        return
    
    # Мгновенный ответ
    typing_task = asyncio.create_task(
        update.message.reply_text("⚡ *Ищу информацию...*", parse_mode='Markdown')
    )
    
    # Быстрый поиск
    info_text, image_url = get_instant_mercedes_info(user_message)
    
    # Отменяем сообщение "Ищу информацию..." если оно еще не отправлено
    try:
        typing_task.cancel()
    except:
        pass
    
    await update.message.reply_text(info_text, parse_mode='Markdown')

# Запуск бота
def main():
    try:
        application = Application.builder().token(BOT_TOKEN).build()
        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_all_messages))
        
        print("🤖 ИИ-бот Mercedes запущен!")
        print("✅ Мгновенные ответы на запросы")
        print("✅ Быстрый поиск информации")
        application.run_polling()
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == '__main__':
    main()