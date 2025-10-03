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

Я найду информацию о любой модели Mercedes с ценами и фотографиями!

*Напишите название модели:*
• G-class (гелик, гелендваген, г-класс)
• S-class (эска, эс-класс)  
• E-class (ешка, е-класс, ешку)
• C-class (цешка, ц-класс)
• EQS (екс)
• AMG (амега)
• GLC (гэлэс)
• GLE (гэлэе)

*Пример:* напишите `гелик` или `ешка` и я покажу информацию с ценой!
    """
    await update.message.reply_text(welcome_text, parse_mode='Markdown')

# База данных моделей с ценами, картинками и сленговыми названиями
def get_mercedes_data():
    return {
        'G-Class': {
            'names': ['g-class', 'g class', 'gclass', 'гелик', 'гелендваген', 'гелендваген', 'г клас', 'g wagon', 'гелик', 'г класс', 'гель'],
            'price': '💰 *Цена:* от 12 900 000 ₽',
            'image': 'https://upload.wikimedia.org/wikipedia/commons/thumb/7/7d/2019_Mercedes-Benz_G_350_d_Professional_%28_V_%29.jpg/1200px-2019_Mercedes-Benz_G_350_d_Professional_%28_V_%29.jpg',
            'info': """🚙 *Mercedes-Benz G-Class*

Легендарный внедорожник класса «люкс», производится с 1979 года. Известен культовым дизайном и выдающейся проходимостью.

• Поколения: W460, W461, W463
• Привод: постоянный полный 4MATIC
• Двигатели: бензиновые и дизельные V6, V8
• Особенности: рамная конструкция, три блокируемых дифференциала
• Мощность: до 585 л.с. (G63 AMG)"""
        },
        'S-Class': {
            'names': ['s-class', 's class', 'sclass', 'эска', 'с класс', 's klasse', 'мерседес с', 'эс-класс', 'эску', 'с-класс'],
            'price': '💰 *Цена:* от 8 900 000 ₽',
            'image': 'https://upload.wikimedia.org/wikipedia/commons/thumb/9/9b/2022_Mercedes-Benz_S500_4Matic_%28V223%29.jpg/1200px-2022_Mercedes-Benz_S500_4Matic_%28V223%29.jpg',
            'info': """🚗 *Mercedes-Benz S-Class*

Флагманский седан бизнес-класса, эталон роскоши и технологий в автомобилестроении.

• Поколения: W223, W222, W221, W220
• Двигатели: рядные 6, V8, гибридные
• Особенности: система DRIVE PILOT, массажные кресла, технология MBUX Hyperscreen
• Длина: от 5179 мм (длинная версия)"""
        },
        'E-Class': {
            'names': ['e-class', 'e class', 'eclass', 'е класс', 'е клас', 'мерседес е', 'ешка', 'ешку', 'е-класс', 'мерс е'],
            'price': '💰 *Цена:* от 5 200 000 ₽',
            'image': 'https://upload.wikimedia.org/wikipedia/commons/thumb/d/dc/2017_Mercedes-Benz_E220d_AMG_Line_Automatic_2.0_Front.jpg/1200px-2017_Mercedes-Benz_E220d_AMG_Line_Automatic_2.0_Front.jpg',
            'info': """🚘 *Mercedes-Benz E-Class*

Бизнес-седан, идеально сочетающий комфорт, технологии и стиль.

• Поколения: W214, W213, W212
• Класс: бизнес-класс
• Особенности: система полуавтономного вождения, двойной экран
• Популярность: одна из самых продаваемых моделей Mercedes"""
        },
        'C-Class': {
            'names': ['c-class', 'c class', 'cclass', 'цешка', 'ц класс', 'с клас', 'мерседес ц', 'ц-класс', 'цешку'],
            'price': '💰 *Цена:* от 3 800 000 ₽',
            'image': 'https://upload.wikimedia.org/wikipedia/commons/thumb/e/e8/2018_Mercedes-Benz_C200_AMG_Line_%28W205%29.jpg/1200px-2018_Mercedes-Benz_C200_AMG_Line_%28W205%29.jpg',
            'info': """🚖 *Mercedes-Benz C-Class*

Компактный представительский седан для ценителей стиля и технологий.

• Поколения: W206, W205
• Класс: компактный представительский
• Особенности: спортивный дизайн, технология MBUX
• Разгон: C43 AMG - 4.6 сек до 100 км/ч"""
        },
        'EQS': {
            'names': ['eqs', 'е кс', 'еқс', 'мерседес екс', 'екс', 'электро мерс'],
            'price': '💰 *Цена:* от 9 500 000 ₽',
            'image': 'https://upload.wikimedia.org/wikipedia/commons/thumb/6/6c/2022_Mercedes-Benz_EQS_450%2B_AMG_Line.jpg/1200px-2022_Mercedes-Benz_EQS_450%2B_AMG_Line.jpg',
            'info': """⚡ *Mercedes-Benz EQS*

Флагманский электромобиль с революционным дизайном и технологиями.

• Запас хода: до 770 км
• Технологии: MBUX Hyperscreen, автопилот
• Разгон: 4.3 сек до 100 км/ч
• Класс: люкс электромобиль
• Мощность: до 524 л.с."""
        },
        'AMG': {
            'names': ['amg', 'амега', 'амг', 'мерседес амг', 'амегу'],
            'price': '💰 *Цена моделей AMG:* от 6 500 000 ₽',
            'image': 'https://upload.wikimedia.org/wikipedia/commons/thumb/8/8b/Mercedes-AMG_GT_63_S_4MATIC%2B_%28A_205%29_%E2%80%93_f_04032021.jpg/1200px-Mercedes-AMG_GT_63_S_4MATIC%2B_%28A_205%29_%E2%80%93_f_04032021.jpg',
            'info': """🏎️ *Mercedes-AMG*

Подразделение высокопроизводительных автомобилей Mercedes-Benz.

• Основан: 1967 год
• Особенности: handcrafted engines, спортивные характеристики
• Модели: C63, E63, G63, GT
• Мощность: до 831 л.с. (GT Black Series)"""
        },
        'GLC': {
            'names': ['glc', 'глс', 'г л с', 'гэлэс', 'глс'],
            'price': '💰 *Цена:* от 4 500 000 ₽',
            'image': 'https://upload.wikimedia.org/wikipedia/commons/thumb/8/8f/2019_Mercedes-Benz_GLC_300_4Matic_%28X253%29.jpg/1200px-2019_Mercedes-Benz_GLC_300_4Matic_%28X253%29.jpg',
            'info': """🚙 *Mercedes-Benz GLC*

Компактный кроссовер премиум-класса на базе C-Class.

• Поколения: X254, X253
• Класс: компактный кроссовер
• Особенности: полный привод 4MATIC, современный дизайн
• Объем багажника: 550 литров"""
        },
        'GLE': {
            'names': ['gle', 'гле', 'г л е', 'гэлэе', 'глешка'],
            'price': '💰 *Цена:* от 6 800 000 ₽',
            'image': 'https://upload.wikimedia.org/wikipedia/commons/thumb/7/7a/2020_Mercedes-Benz_GLE_400_d_4Matic_%28V_167%29.jpg/1200px-2020_Mercedes-Benz_GLE_400_d_4Matic_%28V_167%29.jpg',
            'info': """🚙 *Mercedes-Benz GLE*

Среднеразмерный кроссовер премиум-класса на базе E-Class.

• Поколения: V167, W166
• Класс: среднеразмерный кроссовер
• Особенности: просторный салон, продвинутые системы помощи
• Двигатели: бензиновые, дизельные, гибридные"""
        }
    }

# Поиск модели по сообщению пользователя
def find_mercedes_model(user_message):
    mercedes_data = get_mercedes_data()
    user_message = user_message.lower().strip()
    
    # Ищем совпадение в названиях моделей
    for model_name, model_data in mercedes_data.items():
        for name_variant in model_data['names']:
            if name_variant in user_message:
                return model_name, model_data
    
    # Если просто написали "мерседес"
    if any(word in user_message for word in ['мерседес', 'mercedes', 'мерс', 'мерсед', 'мерца', 'мерсюк']):
        return "mercedes_general", None
    
    return None, None

# Обработчик сообщений
async def handle_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text.strip()
    
    # Игнорируем команды
    if user_message.startswith('/'):
        return
    
    # Ищем модель
    model_name, model_data = find_mercedes_model(user_message)
    
    if model_name == "mercedes_general":
        # Если просто написали "мерседес"
        help_message = """
🚗 *Я нашел, что вы интересуетесь Mercedes-Benz!*

Пожалуйста, уточните *какая именно модель* вас интересует:

*Внедорожники:*
• G-class (гелик, гелендваген) - от 12.9 млн ₽
• GLC (гэлэс) - от 4.5 млн ₽  
• GLE (гэлэе) - от 6.8 млн ₽

*Седаны:*
• S-class (эска, эс-класс) - от 8.9 млн ₽
• E-class (ешка, е-класс) - от 5.2 млн ₽
• C-class (цешка, ц-класс) - от 3.8 млн ₽

*Электромобили:*
• EQS (екс) - от 9.5 млн ₽

*Спортивные:*
• AMG (амега) - от 6.5 млн ₽

*💡 Просто напишите интересующую модель (можно сленгом)!*
        """
        await update.message.reply_text(help_message, parse_mode='Markdown')
        
    elif model_data:
        # Если нашли конкретную модель
        await update.message.reply_text("🔍 *Нашел информацию...*", parse_mode='Markdown')
        
        # Формируем полный ответ
        full_info = f"{model_data['info']}\n\n{model_data['price']}"
        
        try:
            # Пытаемся отправить с картинкой
            await update.message.reply_photo(
                photo=model_data['image'],
                caption=full_info[:1020],
                parse_mode='Markdown'
            )
        except Exception as e:
            # Если картинка не загружается, отправляем только текст
            await update.message.reply_text(full_info, parse_mode='Markdown')
            
    else:
        # Если модель не распознана
        help_message = """
🚗 *Я не нашел такую модель Mercedes!*

*Популярные модели (понимаю сленг):*
• G-class (гелик, гелендваген)
• S-class (эска, эс-класс)  
• E-class (ешка, е-класс, ешку)
• C-class (цешка, ц-класс)
• EQS (екс)
• AMG (амега)
• GLC (гэлэс)
• GLE (гэлэе)

*💡 Попробуйте написать одно из этих названий!*
        """
        await update.message.reply_text(help_message, parse_mode='Markdown')

# Запуск бота
def main():
    try:
        application = Application.builder().token(BOT_TOKEN).build()
        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_messages))
        
        print("🤖 Бот Mercedes запущен и готов к работе!")
        print("✅ Распознает: гелик, ешка, цешка, эска, амега и др.")
        print("✅ Показывает цены и картинки")
        print("✅ Понимает сленговые названия")
        application.run_polling()
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == '__main__':
    main()