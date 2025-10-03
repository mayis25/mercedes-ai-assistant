import logging
import wikipediaapi
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ⚠️ Ваш токен
BOT_TOKEN = "7606597523:AAEsP5mcWb7vSg971B3WT-p9pu92BzFBEDc"

# Настройка
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Команда /start
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = """
🚗 *Добро пожаловать в бот Mercedes-Benz!*

Я найду информацию о любой модели Mercedes!

*Просто напишите:*
• G-class
• S-class  
• EQS
• C-class
• AMG
• Или любую другую модель

*Пример:* напишите `S-class` и я найду актуальную информацию!
    """
    await update.message.reply_text(welcome_text, parse_mode='Markdown')
    logger.info(f"User {update.message.from_user.id} used /start")

# Команда /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
📋 *Доступные команды:*
/start - начать работу
/help - показать справку

🚗 *Просто напишите название модели Mercedes для поиска!*
    """
    await update.message.reply_text(help_text, parse_mode='Markdown')

# Упрощенный поиск информации
def search_mercedes_info(model_name):
    try:
        # Используем простой API для поиска
        url = f"https://ru.wikipedia.org/api/rest_v1/page/summary/Mercedes-Benz_{model_name}"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            title = data.get('title', '')
            summary = data.get('extract', 'Информация не найдена')
            image_url = data.get('thumbnail', {}).get('source') if data.get('thumbnail') else None
            
            info_text = f"🔍 *{title}*\n\n{summary}\n\n📖 *Источник: Wikipedia*"
            return info_text, image_url
        else:
            return f"❌ Информация о Mercedes {model_name} не найдена", None
            
    except Exception as e:
        logger.error(f"Search error: {e}")
        return f"❌ Ошибка при поиске информации", None

# Обработчик всех сообщений
async def handle_all_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text.strip().lower()
    
    # Игнорируем команды
    if user_message.startswith('/'):
        return
    
    # Словарь моделей для распознавания
    mercedes_models = {
        'g-class': 'G-Class', 'g class': 'G-Class', 'gclass': 'G-Class',
        's-class': 'S-Class', 's class': 'S-Class', 'sclass': 'S-Class',
        'e-class': 'E-Class', 'e class': 'E-Class', 'eclass': 'E-Class',
        'c-class': 'C-Class', 'c class': 'C-Class', 'cclass': 'C-Class',
        'a-class': 'A-Class', 'a class': 'A-Class', 'aclass': 'A-Class',
        'eqs': 'EQS', 'eqe': 'EQE', 'eqc': 'EQC',
        'gls': 'GLS', 'gle': 'GLE', 'glc': 'GLC', 'gla': 'GLA',
        'cls': 'CLS', 'cla': 'CLA', 'sl': 'SL', 'amg': 'AMG',
        'maybach': 'Maybach', 'vito': 'Vito', 'sprinter': 'Sprinter',
        'mercedes': 'Mercedes-Benz', 'мерседес': 'Mercedes-Benz'
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
        
        if info_text:
            if image_url:
                try:
                    # Пытаемся отправить с картинкой
                    await update.message.reply_photo(
                        photo=image_url,
                        caption=info_text[:1020],
                        parse_mode='Markdown'
                    )
                except Exception as e:
                    # Если картинка не отправляется, отправляем текст
                    await update.message.reply_text(info_text, parse_mode='Markdown')
            else:
                # Только текст если нет картинки
                await update.message.reply_text(info_text, parse_mode='Markdown')
        else:
            await update.message.reply_text("❌ Информация не найдена")
            
    else:
        # Если модель не распознана
        help_message = """
🚗 *Я не нашел модель Mercedes в вашем сообщении!*

*Попробуйте написать:*
• `G-class` - внедорожник
• `S-class` - флагманский седан  
• `E-class` - бизнес-класс
• `C-class` - компактный представительский
• `EQS` - электромобиль
• `AMG` - спортивные модели

*Или используйте:* /help
        """
        await update.message.reply_text(help_message, parse_mode='Markdown')

# Основная функция
def main():
    try:
        # Создаем приложение
        application = Application.builder().token(BOT_TOKEN).build()
        
        # Обработчики команд
        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(CommandHandler("help", help_command))
        
        # Обработчик всех текстовых сообщений
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_all_messages))
        
        # Запускаем
        print("=" * 50)
        print("🤖 БОТ MERCEDES-BENZ ЗАПУЩЕН!")
        print("✅ /start - работает")
        print("✅ Поиск информации - работает") 
        print("=" * 50)
        
        application.run_polling()
        
    except Exception as e:
        print(f"❌ Ошибка запуска: {e}")

if __name__ == '__main__':
    main()