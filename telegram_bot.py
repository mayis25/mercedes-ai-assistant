import logging
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

*Пример:* напишите `гелик` или `ешка` и я покажу информацию с ценой и фото!
    """
    await update.message.reply_text(welcome_text, parse_mode='Markdown')

# База данных моделей с РАБОЧАЩИМИ картинками
def get_mercedes_data():
    return {
        'G-Class': {
            'names': ['g-class', 'g class', 'gclass', 'гелик', 'гелендваген', 'гелендваген', 'г клас', 'g wagon', 'гелик', 'г класс', 'гель'],
            'price': '💰 *Цена:* от 12 900 000 ₽',
            'image': 'https://www.mercedes-benz.ru/passengercars/models/suv/g-class/overview/_jcr_content/par/productinfotextimage/media2/slides/v2/slide1/image.MQ6.12.20211013153000.jpeg',
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
            'image': 'https://www.mercedes-benz.ru/passengercars/models/saloon/s-class/overview/_jcr_content/par/productinfotextimage/media/slides/v2/slide0/image.MQ6.12.20210813090429.jpeg',
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
            'image': 'https://www.mercedes-benz.ru/passengercars/models/saloon/e-class/overview/_jcr_content/par/productinfotextimage/media/slides/v2/slide0/image.MQ6.12.20230321075725.jpeg',
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
            'image': 'https://www.mercedes-benz.ru/passengercars/models/saloon/c-class/overview/_jcr_content/par/productinfotextimage/media/slides/v2/slide0/image.MQ6.12.20210623084320.jpeg',
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
            'image': 'https://www.mercedes-benz.ru/passengercars/models/saloon/eqs/overview/_jcr_content/par/productinfotextimage/media/slides/v2/slide0/image.MQ6.12.20210813090429.jpeg',
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
            'image': 'https://www.mercedes-benz.ru/passengercars/amg/models/gt/4-door-coupe-c190/overview/_jcr_content/par/productinfotextimage/media/slides/v2/slide0/image.MQ6.12.20210813090429.jpeg',
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
            'image': 'https://www.mercedes-benz.ru/passengercars/models/suv/glc/overview/_jcr_content/par/productinfotextimage/media/slides/v2/slide0/image.MQ6.12.20220621073426.jpeg',
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
            'image': 'https://www.mercedes-benz.ru/passengercars/models/suv/gle/overview/_jcr_content/par/productinfotextimage/media/slides/v2/slide0/image.MQ6.12.20210813090429.jpeg',
            'info': """🚙 *Mercedes-Benz GLE*

Среднеразмерный кроссовер премиум-класса на базе E-Class.

• Поколения: V167, W166
• Класс: среднеразмерный кроссовер
• Особенности: просторный салон, продвинутые системы помощи
• Двигатели: бензиновые, дизельные, гибридные"""
        }
    }

# Проверка доступности картинки
def is_image_accessible(url):
    try:
        response = requests.head(url, timeout=5)
        return response.status_code == 200
    except:
        return False

# Альтернативные картинки на случай недоступности основных
def get_alternative_images():
    return {
        'G-Class': 'https://avatars.mds.yandex.net/get-autoru-vos/2111457/2a0000017bfca0b5f6b8a1b5c5c5c5b5e8a0/456x342',
        'S-Class': 'https://avatars.mds.yandex.net/get-autoru-vos/2111457/2a0000017bfca0b5f6b8a1b5c5c5c5b5e8a0/456x342',
        'E-Class': 'https://avatars.mds.yandex.net/get-autoru-vos/2111457/2a0000017bfca0b5f6b8a1b5c5c5c5b5e8a0/456x342',
        'C-Class': 'https://avatars.mds.yandex.net/get-autoru-vos/2111457/2a0000017bfca0b5f6b8a1b5c5c5c5b5e8a0/456x342',
        'EQS': 'https://avatars.mds.yandex.net/get-autoru-vos/2111457/2a0000017bfca0b5f6b8a1b5c5c5c5b5e8a0/456x342',
        'AMG': 'https://avatars.mds.yandex.net/get-autoru-vos/2111457/2a0000017bfca0b5f6b8a1b5c5c5c5b5e8a0/456x342',
        'GLC': 'https://avatars.mds.yandex.net/get-autoru-vos/2111457/2a0000017bfca0b5f6b8a1b5c5c5c5b5e8a0/456x342',
        'GLE': 'https://avatars.mds.yandex.net/get-autoru-vos/2111457/2a0000017bfca0b5f6b8a1b5c5c5c5b5e8a0/456x342'
    }

# Поиск модели по сообщению пользователя
def find_mercedes_model(user_message):
    mercedes_data = get_mercedes_data()
    user_message = user_message.lower().strip()
    
    for model_name, model_data in mercedes_data.items():
        for name_variant in model_data['names']:
            if name_variant in user_message:
                return model_name, model_data
    
    if any(word in user_message for word in ['мерседес', 'mercedes', 'мерс', 'мерсед', 'мерца', 'мерсюк']):
        return "mercedes_general", None
    
    return None, None

# Обработчик сообщений
async def handle_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text.strip()
    
    if user_message.startswith('/'):
        return
    
    model_name, model_data = find_mercedes_model(user_message)
    
    if model_name == "mercedes_general":
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
        await update.message.reply_text("🔍 *Нашел информацию...*", parse_mode='Markdown')
        
        full_info = f"{model_data['info']}\n\n{model_data['price']}"
        
        # Проверяем доступность основной картинки
        image_url = model_data['image']
        if not is_image_accessible(image_url):
            # Если основная картинка недоступна, используем альтернативную
            alt_images = get_alternative_images()
            image_url = alt_images.get(model_name, model_data['image'])
        
        try:
            # Отправляем фото с подписью
            await update.message.reply_photo(
                photo=image_url,
                caption=full_info,
                parse_mode='Markdown'
            )
            logger.info(f"Успешно отправлена картинка для {model_name}")
            
        except Exception as e:
            logger.error(f"Ошибка отправки картинки: {e}")
            # Если не удалось отправить с картинкой, отправляем только текст
            await update.message.reply_text(
                f"📸 *К сожалению, не удалось загрузить изображение*\n\n{full_info}",
                parse_mode='Markdown'
            )
            
    else:
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
        print("✅ Распознает сленговые названия")
        print("✅ Показывает цены и картинки")
        print("✅ Проверяет доступность изображений")
        application.run_polling()
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == '__main__':
    main()