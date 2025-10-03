import logging
import wikipedia
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Токен бота
BOT_TOKEN = "7606597523:AAEsP5mcWb7vSg971B3WT-p9pu92BzFBEDc"

# Настройка
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
wikipedia.set_lang("ru")

# Команда /start
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = """
🧠 *Добро пожаловать в ИИ-бот!*

Я могу найти информацию о ЧЕМ УГОДНО в Wikipedia!

*Просто напишите любой вопрос:*
• "Tesla Model S"
• "Искусственный интеллект"
• "История Рима" 
• "Биография Пушкина"
• "Что такое черные дыры?"

*Я найду информацию и покажу вам!*
    """
    await update.message.reply_text(welcome_text, parse_mode='Markdown')

# Поиск в Wikipedia
def search_wikipedia(query):
    try:
        # Ищем страницу
        search_results = wikipedia.search(query)
        if not search_results:
            return "❌ Информация не найдена. Попробуйте другой запрос.", None
        
        page_title = search_results[0]
        summary = wikipedia.summary(page_title, sentences=5)
        
        # Получаем картинку
        page = wikipedia.page(page_title)
        image_url = None
        for img in page.images[:5]:
            if any(ext in img.lower() for ext in ['.jpg', '.jpeg', '.png']):
                image_url = img
                break
        
        info_text = f"🔍 *{page_title}*\n\n{summary}\n\n📖 *Источник: Wikipedia*"
        return info_text, image_url
        
    except wikipedia.exceptions.DisambiguationError as e:
        options = "\n".join([f"• {opt}" for opt in e.options[:5]])
        return f"🤔 Найдено несколько вариантов:\n\n{options}\n\n*Уточните запрос!*", None
        
    except wikipedia.exceptions.PageError:
        return f"❌ Информация по запросу '{query}' не найдена.", None
        
    except Exception as e:
        return f"❌ Ошибка: {str(e)}", None

# Обработчик сообщений
async def handle_all_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text.strip()
    
    if user_message.startswith('/'):
        return
    
    await update.message.reply_text("🔍 *Ищу информацию...*", parse_mode='Markdown')
    
    info_text, image_url = search_wikipedia(user_message)
    
    if image_url:
        try:
            await update.message.reply_photo(
                photo=image_url,
                caption=info_text,
                parse_mode='Markdown'
            )
        except:
            await update.message.reply_text(info_text, parse_mode='Markdown')
    else:
        await update.message.reply_text(info_text, parse_mode='Markdown')

# Запуск бота
def main():
    try:
        application = Application.builder().token(BOT_TOKEN).build()
        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_all_messages))
        
        print("🤖 ИИ-бот запущен!")
        application.run_polling()
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == '__main__':
    main()