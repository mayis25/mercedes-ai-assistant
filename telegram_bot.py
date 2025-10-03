import logging
import wikipediaapi
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Токен бота
BOT_TOKEN = "7606597523:AAEsP5mcWb7vSg971B3WT-p9pu92BzFBEDc"

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Команда /start
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = """
🚗 *Добро пожаловать в бот Mercedes-Benz!*

Я найду информацию о любой модели Mercedes!

Просто напишите:
• G-class
• S-class  
• EQS
• C-class
• AMG

*Пример:* напишите `S-class` и я найду информацию!
    """
    await update.message.reply_text(welcome_text, parse_mode='Markdown')

# Улучшенный поиск информации
def search_mercedes_info(model_name):
    try:
        # Пробуем разные варианты названий для поиска
        search_variants = [
            f"Mercedes-Benz {model_name}",
            f"Mercedes {model_name}",
            model_name,
            f"{model_name} (Mercedes-Benz)"
        ]
        
        for search_query in search_variants:
            try:
                # Кодируем запрос для URL
                import urllib.parse
                encoded_query = urllib.parse.quote(search_query)
                
                url = f"https://ru.wikipedia.org/api/rest_v1/page/summary/{encoded_query}"
                response = requests.get(url, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    title = data.get('title', '')
                    summary = data.get('extract', '')
                    
                    if summary and "мерседес" in summary.lower() or "mercedes" in summary.lower():
                        image_url = data.get('thumbnail', {}).get('source') if data.get('thumbnail') else None
                        
                        info_text = f"🔍 *{title}*\n\n{summary}\n\n📖 *Источник: Wikipedia*"
                        return info_text, image_url
                        
            except Exception as e:
                continue
        
        # Если не нашли через API, используем простой текст
        return get_fallback_info(model_name), None
        
    except Exception as e:
        logger.error(f"Search error: {e}")
        return get_fallback_info(model_name), None

# Резервная информация, если Wikipedia не работает
def get_fallback_info(model_name):
    info_dict = {
        'G-Class': """🚙 *Mercedes-Benz G-Class*

Внедорожник класса «люкс», производится с 1979 года. Известен своим культовым дизайном и выдающейся проходимостью.

• Поколения: W460, W461, W463
• Привод: постоянный полный
• Особенности: рамная конструкция, три дифференциала""",

        'S-Class': """🚗 *Mercedes-Benz S-Class*

Флагманский седан бизнес-класса, эталон роскоши и технологий в автомобилестроении.

• Поколения: W223, W222, W221, W220
• Особенности: система автопилота, массажные кресла, технология MBUX""",

        'E-Class': """🚘 *Mercedes-Benz E-Class*

Бизнес-седан, идеально сочетающий комфорт, технологии и стиль.

• Поколения: W214, W213, W212
• Класс: бизнес-класс""",

        'C-Class': """🚖 *Mercedes-Benz C-Class*

Компактный представительский седан для ценителей стиля и технологий.

• Поколения: W206, W205
• Класс: компактный представительский""",

        'EQS': """⚡ *Mercedes-Benz EQS*

Флагманский электромобиль на платформе EVA2 с максимальным запасом хода.

• Запас хода: до 770 км
• Технологии: Hyperscreen, автопилот
• Класс: люкс электромобиль""",

        'AMG': """🏎️ *Mercedes-AMG*

Подразделение высокопроизводительных автомобилей Mercedes-Benz.

• Основан: 1967 год
• Особенности: handcrafted engines, спортивные характеристики"""
    }
    
    return info_dict.get(model_name, f"🔍 *Mercedes {model_name}*\n\nИнформация об этой модели будет добавлена в ближайшее время!")

# Обработчик сообщений
async def handle_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text.lower().strip()
    
    # Игнорируем команды
    if user_message.startswith('/'):
        return
    
    # Словарь моделей для распознавания
    mercedes_models = {
        'g-class': 'G-Class', 'g class': 'G-Class', 'gclass': 'G-Class',
        's-class': 'S-Class', 's class': 'S-Class', 'sclass': 'S-Class',
        'e-class': 'E-Class', 'e class': 'E-Class', 'eclass': 'E-Class',
        'c-class': 'C-Class', 'c class': 'C-Class', 'cclass': 'C-Class',
        'eqs': 'EQS', 'amg': 'AMG', 'мерседес': 'S-Class'
    }
    
    # Ищем модель в сообщении
    detected_model = None
    for key, value in mercedes_models.items():
        if key in user_message:
            detected_model = value
            break
    
    if detected_model:
        await update.message.reply_text("🔍 *Ищу информацию...*", parse_mode='Markdown')
        
        # Ищем информацию
        info_text, image_url = search_mercedes_info(detected_model)
        
        if image_url:
            try:
                await update.message.reply_photo(
                    photo=image_url, 
                    caption=info_text[:1020],
                    parse_mode='Markdown'
                )
            except Exception as e:
                await update.message.reply_text(info_text, parse_mode='Markdown')
        else:
            await update.message.reply_text(info_text, parse_mode='Markdown')
            
    else:
        help_message = """
🚗 *Я не нашел модель Mercedes в вашем сообщении!*

*Попробуйте написать:*
• `G-class` - внедорожник
• `S-class` - флагманский седан  
• `E-class` - бизнес-класс
• `C-class` - компактный представительский
• `EQS` - электромобиль
• `AMG` - спортивные модели
        """
        await update.message.reply_text(help_message, parse_mode='Markdown')

# Запуск бота
def main():
    try:
        application = Application.builder().token(BOT_TOKEN).build()
        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_messages))
        
        print("🤖 Бот Mercedes запущен и готов к работе!")
        print("✅ /start - работает")
        print("✅ Поиск информации - работает")
        application.run_polling()
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == '__main__':
    main()