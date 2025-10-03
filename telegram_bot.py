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

*Также могу рассказать:*
• Об истории Mercedes-Benz
• О технологиях Mercedes
• О характеристиках моделей
• О ценах и комплектациях

*Я найду всю информацию и покажу вам!*
    """
    await update.message.reply_text(welcome_text, parse_mode='Markdown')

# Улучшенный поиск с подробной информацией
def search_detailed_info(query):
    try:
        # Пробуем разные варианты поиска
        search_variants = [
            f"Mercedes-Benz {query}",
            f"Mercedes {query}",
            query,
            f"{query} автомобиль",
            f"{query} Mercedes"
        ]
        
        for search_query in search_variants:
            try:
                search_results = wikipedia.search(search_query)
                if search_results:
                    page_title = search_results[0]
                    
                    # Берем больше текста для подробного ответа
                    summary = wikipedia.summary(page_title, sentences=8)
                    
                    # Получаем полную страницу для дополнительной информации
                    page = wikipedia.page(page_title)
                    
                    # Ищем картинку
                    image_url = None
                    for img in page.images[:10]:
                        if any(ext in img.lower() for ext in ['.jpg', '.jpeg', '.png', '.webp']):
                            if any(keyword in img.lower() for keyword in ['car', 'vehicle', 'model', 'mercedes', 'auto']):
                                image_url = img
                                break
                    if not image_url and page.images:
                        for img in page.images:
                            if any(ext in img.lower() for ext in ['.jpg', '.jpeg', '.png']):
                                image_url = img
                                break
                    
                    # Форматируем подробный ответ
                    detailed_text = format_detailed_response(page_title, summary, page.url)
                    return detailed_text, image_url
                    
            except wikipedia.exceptions.DisambiguationError as e:
                # Если неоднозначность, берем первый вариант
                if e.options:
                    page_title = e.options[0]
                    summary = wikipedia.summary(page_title, sentences=8)
                    page = wikipedia.page(page_title)
                    
                    image_url = None
                    for img in page.images[:5]:
                        if any(ext in img.lower() for ext in ['.jpg', '.jpeg', '.png']):
                            image_url = img
                            break
                    
                    detailed_text = format_detailed_response(page_title, summary, page.url)
                    return detailed_text, image_url
                    
            except wikipedia.exceptions.PageError:
                continue
            except Exception:
                continue
        
        # Если не нашли в Wikipedia, используем запасную информацию
        return get_fallback_info(query), None
        
    except Exception as e:
        logger.error(f"Search error: {e}")
        return get_fallback_info(query), None

# Форматирование подробного ответа
def format_detailed_response(title, summary, url):
    # Очищаем текст от скобок
    import re
    clean_summary = re.sub(r'\[.*?\]', '', summary)
    clean_summary = re.sub(r'\(.*?\)', '', clean_summary)
    
    detailed_text = f"🔍 *{title}*\n\n"
    detailed_text += f"{clean_summary}\n\n"
    detailed_text += f"📖 *Для более подробной информации:*\n{url}"
    
    return detailed_text

# Запасная информация если Wikipedia не нашел
def get_fallback_info(query):
    fallback_data = {
        'g-class': """🚙 *Mercedes-Benz G-Class*

Подробная информация о легендарном внедорожнике:

*История:* Производится с 1979 года, изначально разрабатывался для военных нужд, но стал символом роскоши и статуса.

*Поколения:*
• W460 (1979-1991) - первое поколение
• W461 (1992-2018) - военная и утилитарная версия  
• W463 (1990-настоящее время) - люксовая версия

*Технические характеристики:*
• Привод: постоянный полный 4MATIC
• Двигатели: от 2.0L до 4.0L V8
• Мощность: до 585 л.с. (G63 AMG)
• Трансмиссия: 9-ступенчатая АКПП
• Особенности: три блокируемых дифференциала, рамная конструкция

*Цены:* от 12 900 000 ₽ до 25 000 000 ₽ за специальные версии""",

        's-class': """🚗 *Mercedes-Benz S-Class*

Флагманский седан, устанавливающий стандарты в автомобилестроении:

*Поколения:*
• W223 (2020-н.в.) - текущее поколение с технологией MBUX Hyperscreen
• W222 (2013-2020) - революционный дизайн и автопилот
• W221 (2005-2013) - элегантный и технологичный
• W220 (1998-2005) - знаменитый "жук"

*Технологии:*
• DRIVE PILOT - система автономного вождения
• MAGIC BODY CONTROL - адаптивная подвеска
• ENERGIZING Comfort - система комфорта
• Rear-seat entertainment - развлечения для задних пассажиров

*Двигатели:* от S350d до S680 с мощностью до 612 л.с.

*Цены:* от 8 900 000 ₽ до 18 000 000 ₽""",

        'e-class': """🚘 *Mercedes-Benz E-Class*

Бизнес-седан, идеально сочетающий комфорт и технологии:

*Поколения:*
• W214 (2023-н.в.) - новейшее поколение
• W213 (2016-2023) - популярная модель с двойным экраном
• W212 (2009-2016) - классический дизайн
• W211 (2002-2009) - элегантное исполнение

*Особенности:*
• Система полуавтономного вождения
• Двойной широкоэкранный дисплей
• Активная система безопасности
• Комфортные сиденья с подогревом и вентиляцией

*Кузова:* седан, универсал, купе, кабриолет

*Цены:* от 5 200 000 ₽ до 9 500 000 ₽"""
    }
    
    query_lower = query.lower()
    for key, value in fallback_data.items():
        if key in query_lower:
            return value
    
    return f"🔍 *Информация по запросу '{query}'*\n\nК сожалению, не удалось найти подробную информацию в базе данных. Попробуйте уточнить запрос или обратиться к официальному дилеру Mercedes-Benz."

# Обработчик сообщений
async def handle_all_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text.strip()
    
    if user_message.startswith('/'):
        return
    
    await update.message.reply_text("🔍 *Ищу подробную информацию...*", parse_mode='Markdown')
    
    info_text, image_url = search_detailed_info(user_message)
    
    if image_url:
        try:
            await update.message.reply_photo(
                photo=image_url,
                caption=info_text,
                parse_mode='Markdown'
            )
        except Exception as e:
            logger.error(f"Image error: {e}")
            await update.message.reply_text(info_text, parse_mode='Markdown')
    else:
        await update.message.reply_text(info_text, parse_mode='Markdown')

# Запуск бота
def main():
    try:
        application = Application.builder().token(BOT_TOKEN).build()
        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_all_messages))
        
        print("🤖 ИИ-бот Mercedes запущен!")
        print("✅ Дает подробные ответы на любые запросы")
        application.run_polling()
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == '__main__':
    main()