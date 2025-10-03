import logging
import wikipedia
import requests
import re
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Токен бота
BOT_TOKEN = "7606597523:AAEsP5mcWb7vSg971B3WT-p9pu92BzFBEDc"

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Устанавливаем язык Википедии
wikipedia.set_lang("ru")

# Команда /start
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = """
🧠 *Добро пожаловать в ИИ-бот с искусственным интеллектом!*

Я могу найти информацию о *ЧЕМ УГОДНО* в Wikipedia и предоставить вам подробный ответ!

*Что я умею:*
• Искать информацию о любых автомобилях
• Находить данные о странах, городах, исторических событиях
• Рассказывать о знаменитых людях, науке, технологиях
• Объяснять сложные понятия простыми словами
• Показывать фотографии по теме

*Просто напишите мне ЛЮБОЙ вопрос или тему!*

*Примеры:*
• "Расскажи о Tesla Model S"
• "Что такое черные дыры?"
• "Биография Путина"
• "История Древнего Рима"
• "Как работает искусственный интеллект?"
    """
    await update.message.reply_text(welcome_text, parse_mode='Markdown')

# Команда /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
📖 *Помощь по использованию ИИ-бота*

*Доступные команды:*
/start - начать работу
/help - показать эту справку

*Как использовать:*
Просто напишите мне ЛЮБОЙ вопрос или тему, и я найду информацию в Wikipedia!

*Примеры запросов:*
• "Машины Mercedes"
• "Солнечная система" 
• "Вторая мировая война"
• "Альберт Эйнштейн"
• "Квантовая физика"
• "Искусственный интеллект"

*Я понимаю естественный язык и могу ответить на любой ваш вопрос!*
    """
    await update.message.reply_text(help_text, parse_mode='Markdown')

# Умный поиск в Википедии
def smart_wikipedia_search(query):
    try:
        # Очищаем запрос от лишних слов
        clean_query = clean_user_query(query)
        
        # Ищем в Википедии
        search_results = wikipedia.search(clean_query)
        
        if not search_results:
            return None, None
        
        # Берем самый релевантный результат
        page_title = search_results[0]
        
        # Получаем полную страницу
        page = wikipedia.page(page_title)
        summary = wikipedia.summary(page_title, sentences=6)
        
        # Ищем картинку
        image_url = find_best_image(page.images)
        
        # Форматируем текст
        formatted_text = format_wikipedia_text(summary, page_title, page.url)
        
        return formatted_text, image_url
        
    except wikipedia.exceptions.DisambiguationError as e:
        # Если есть неоднозначность, предлагаем варианты
        options = e.options[:5]  # Берем первые 5 вариантов
        options_text = "\n".join([f"• {opt}" for opt in options])
        text = f"🤔 *Найдено несколько вариантов для \"{query}\":*\n\n{options_text}\n\n*Пожалуйста, уточните ваш запрос!*"
        return text, None
        
    except wikipedia.exceptions.PageError:
        return f"❌ *Информация по запросу \"{query}\" не найдена в Wikipedia.*\n\nПопробуйте переформулировать запрос или уточнить тему.", None
        
    except Exception as e:
        logger.error(f"Search error: {e}")
        return f"❌ *Произошла ошибка при поиске информации.*\n\nПопробуйте еще раз или переформулируйте запрос.", None

# Очистка пользовательского запроса
def clean_user_query(query):
    # Удаляем вопросительные слова и лишние фразы
    stop_words = ['расскажи', 'про', 'о', 'об', 'что', 'такое', 'кто', 'такой', 'как', 'работает', 'информация', 'найди']
    
    words = query.lower().split()
    clean_words = [word for word in words if word not in stop_words and len(word) > 2]
    
    return ' '.join(clean_words) if clean_words else query

# Поиск лучшей картинки
def find_best_image(images):
    if not images:
        return None
    
    # Приоритет для изображений с определенными расширениями и ключевыми словами
    for img_url in images:
        img_lower = img_url.lower()
        # Проверяем расширения файлов
        if any(ext in img_lower for ext in ['.jpg', '.jpeg', '.png', '.webp']):
            # Ищем изображения с релевантными ключевыми словами
            if any(keyword in img_lower for keyword in ['photo', 'image', 'picture', 'main', 'featured']):
                return img_url
    
    # Если не нашли подходящую, берем первую
    for img_url in images:
        if any(ext in img_url.lower() for ext in ['.jpg', '.jpeg', '.png', '.webp']):
            return img_url
    
    return None

# Форматирование текста из Википедии
def format_wikipedia_text(text, title, url):
    # Убираем лишние скобки и технические символы
    clean_text = re.sub(r'\[.*?\]', '', text)
    clean_text = re.sub(r'\(.*?\)', '', clean_text)
    
    # Форматируем заголовок
    formatted_text = f"🔍 *{title}*\n\n"
    
    # Добавляем основной текст
    formatted_text += f"{clean_text}\n\n"
    
    # Добавляем ссылку на полную статью
    formatted_text += f"📖 *Полная статья в Wikipedia:*\n{url}"
    
    return formatted_text

# Обработчик ВСЕХ сообщений
async def handle_all_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text.strip()
    
    # Игнорируем команды
    if user_message.startswith('/'):
        return
    
    # Показываем, что бот думает
    await update.message.reply_text("🤔 *Ищу информацию в Wikipedia...*", parse_mode='Markdown')
    
    # Ищем информацию
    info_text, image_url = smart_wikipedia_search(user_message)
    
    if info_text:
        if image_url:
            try:
                # Пытаемся отправить с картинкой
                await update.message.reply_photo(
                    photo=image_url,
                    caption=info_text,
                    parse_mode='Markdown'
                )
                logger.info(f"✅ Успешно найдена информация для запроса: {user_message}")
                
            except Exception as e:
                logger.error(f"❌ Ошибка отправки картинки: {e}")
                # Отправляем только текст если картинка не загрузилась
                await update.message.reply_text(info_text, parse_mode='Markdown')
        else:
            # Отправляем только текст если нет картинки
            await update.message.reply_text(info_text, parse_mode='Markdown')
    else:
        error_text = """
❌ *Не удалось найти информацию по вашему запросу!*

*Возможные причины:*
• Слишком сложный или неоднозначный запрос
• Тема слишком новая или узкоспециализированная
• Проблемы с подключением к Wikipedia

*Попробуйте:*
• Переформулировать запрос
• Использовать более простые слова
• Уточнить тему

*Примеры рабочих запросов:*
• "Илон Маск"
• "Электрические автомобили" 
• "История компьютеров"
• "Климат Земли"
• "Медицинские технологии"
        """
        await update.message.reply_text(error_text, parse_mode='Markdown')

# Запуск бота
def main():
    try:
        application = Application.builder().token(BOT_TOKEN).build()
        
        # Обработчики команд
        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(CommandHandler("help", help_command))
        
        # Обработчик ВСЕХ текстовых сообщений
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_all_messages))
        
        # Запускаем
        print("=" * 60)
        print("🧠 ИИ-БОТ С ИСКУССТВЕННЫМ ИНТЕЛЛЕКТОМ ЗАПУЩЕН!")
        print("✅ Может отвечать на ЛЮБЫЕ вопросы")
        print("✅ Ищет информацию в Wikipedia")
        print("✅ Показывает картинки")
        print("✅ Понимает естественный язык")
        print("=" * 60)
        
        application.run_polling()
        
    except Exception as e:
        print(f"❌ Ошибка запуска: {e}")

if __name__ == '__main__':
    main()