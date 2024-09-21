from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove
from dotenv import load_dotenv
import os
import shutil
from TerraYolo.TerraYolo import TerraYoloV5             # загружаем фреймворк TerraYolo
import requests
from os import listdir
from os.path import isfile, join

# возьмем переменные окружения из .env
load_dotenv()

# загружаем токен бота
TOKEN =  os.environ.get("TOKEN") # ВАЖНО !!!!!

# инициализируем класс YOLO
# WORK_DIR = os.environ.get("WORK_DIR")
WORK_DIR = r'D:\NewUII'
os.makedirs(WORK_DIR, exist_ok=True)
yolov5 = TerraYoloV5(work_dir=WORK_DIR)


# функция обработки изображения
async def detection(update, context, my_class=None):
    # удаляем папку images с предыдущим загруженным изображением и папку runs с результатом предыдущего распознавания
    try:
        shutil.rmtree(f'{WORK_DIR}/yolov5/runs') 
    except:
        pass
    if my_class == None:
        try:
            shutil.rmtree('images') 
        except:
            pass
    try:
        await update.message.reply_text('Мы получили от тебя фотографию.')
    except:
        pass
    
    # получение файла из сообщения
    os.makedirs('images', exist_ok=True)
    try:
        new_file = await update.message.photo[-1].get_file()

        # имя файла на сервере
        image_name = str(new_file['file_path']).split("/")[-1]
        image_path = os.path.join('images', image_name)
        
        # скачиваем файл с сервера Telegram в папку images
        await new_file.download_to_drive(image_path)
    except:
        pass
    
    try:
        new_file = await update.message.document.get_file()
        image_url = new_file['file_path']
        
        # имя файла из URL
        image_name = image_url.split("/")[-1]  # Получаем имя файла из URL
        image_path = os.path.join('images', image_name)  # Формируем путь для сохранения файла

        # Загрузить файл
        response = requests.get(image_url)
        image_data = response.content

        # Сохранить файл на диск
        with open(image_path, "wb") as file:
            file.write(image_data)
    except:
        pass
    try:
        # Отправляем сообщение о сохранении файла
        await update.message.reply_text(f'Файл успешно сохранен на диск по пути: {image_path}')
        
        my_message = await update.message.reply_text(f'Идет распознание объектов на фотографии...')
    except:
        pass

    # создаем словарь с параметрами
    test_dict = dict()
    test_dict['weights'] = 'yolov5x.pt'     # Самые сильные веса yolov5x.pt, вы также можете загрузить версии: yolov5n.pt, yolov5s.pt, yolov5m.pt, yolov5l.pt (в порядке возрастания)

    test_dict['source'] = f'{WORK_DIR}\\images' # папка, в которую загружаются присланные в бота изображения
    # test_dict['conf'] = 0.5                   # порог распознавания 
    if my_class is not None:
        test_dict['classes'] = my_class         # классы, которые будут распознаны
    # test_dict['iou'] = 0.5                     # Порог Intersection over Union (IoU)

    # вызов функции detect из класса TerraYolo)
    yolov5.run(test_dict, exp_type='test') 


    # отправляем пользователю результат
    try:
        # удаляем предыдущее сообщение от бота
        await context.bot.deleteMessage(message_id = my_message.message_id, # если не указать message_id, то удаляется последнее сообщение
                                    chat_id = update.message.chat_id) # если не указать chat_id, то удаляется последнее сообщение
        await update.message.reply_text('Распознавание объектов завершено.') # отправляем пользователю результат 
    except:
        pass
    try:
        my_path = f"{WORK_DIR}/yolov5/runs/detect/exp/{image_name}"
    except:
        # получаем имя файла
        WORK_DIR_YOLO = f"{WORK_DIR}\\images"
        onlyfiles = [f for f in listdir(WORK_DIR_YOLO) if isfile(join(WORK_DIR_YOLO, f))]
        my_path = f"{WORK_DIR}/yolov5/runs/detect/exp/{onlyfiles[0]}" 
    

    homework_path = f"{WORK_DIR}/homework"
    if not os.path.exists(homework_path):
        os.makedirs(homework_path)
    # Позволяет сохранить результаты по детектированию одного класса
    target_path = os.path.join(homework_path, os.path.basename(my_path))
    if os.path.exists(target_path):
        # Если файл существует, добавляем "_1" к имени файла
        base_name, ext = os.path.splitext(os.path.basename(my_path))
        new_filename = f"{base_name}_1{ext}"
        target_path = os.path.join(homework_path, new_filename)
    shutil.copy(my_path, target_path)
    
    print('my_path', my_path)
    print("Файлы успешно перенесены в папку 'homework'")
    
    # await update.message.reply_photo(my_path) # отправляем пользователю результат изображение
    
    if update.message:
        await update.message.reply_photo(my_path) # отправляем пользователю результат изображение
    else:
        await update.callback_query.message.reply_photo(my_path)
        
    
    # создаем список Inline кнопок
    keyboard = [[InlineKeyboardButton("Детектируем человека", callback_data="0"),
                InlineKeyboardButton("Детектируем машину", callback_data="2"),
                InlineKeyboardButton("Детектируем трактор", callback_data="7")]]
    
    # создаем Inline клавиатуру
    reply_markup = InlineKeyboardMarkup(keyboard)

    # прикрепляем клавиатуру к сообщению
    # await update.message.reply_text('Кнопки для выбора объекта детектирования', reply_markup=reply_markup)

    if update.message: 
        await update.message.reply_text('Кнопки для выбора объекта детектирования', reply_markup=reply_markup) 
    elif update.callback_query: 
        await update.callback_query.message.reply_text('Кнопки для выбора объекта детектирования', reply_markup=reply_markup)
    else: 
        pass # Обрабатываем другие случаи, когда update.message и update.callback_query оба равны None


# функция команды /start
async def start(update, context):
    
    await update.message.reply_text('Этот бот предназначен для обработки сообщений с помощью yolov5x.')
    await update.message.reply_text('Пришлите фото для распознавания объектов.')
    
    
# функция обработки нажатия на кнопки Inline клавиатуры
async def button(update, context):

    # параметры входящего запроса при нажатии на кнопку
    query = update.callback_query
    print(query)

    # отправка всплывающего уведомления
    await query.answer('Ожидайте...')
    
    # редактирование сообщения
    await query.edit_message_text(text=f"Детектируем класс: {query.data}")
    
    await detection(update, context, query.data)

    
# функция команды /help
async def help(update, context):
    await update.message.reply_text('Этот бот используют объектный детектор YOLOv5 из фреймворка TerraYolo для распознавания объектов на изображениях, отправляемых пользователем.')
    await update.message.reply_text('Бот поддерживает команды /start, /help, а также обработку нажатия на кнопки Inline клавиатуры для выбора класса объекта для детектирования.')
    await update.message.reply_text('Основные функции бота: ')
    await update.message.reply_text('1. Обработка изображений, отправленных пользователем (в формате .jpg и .png).')
    await update.message.reply_text('Изображение .jpg можно отправить как фото и в документе (не в сжатом виде).')
    await update.message.reply_text('2.  Распознавание объектов на изображениях с помощью YOLOv5 из фреймворка TerraYolo.')
    await update.message.reply_text('3. Сохранение результатов распознавания в папку "homework".')
    await update.message.reply_text('4. Отправка пользователю изображения с результатами распознавания.')
    await update.message.reply_text('5. Предоставление интерактивной Inline клавиатуры для выбора класса объекта для детектирования.')
    await update.message.reply_text('Наберите /start, чтобы начать работу.')

        
def main():

    # точка входа в приложение
    application = Application.builder().token(TOKEN).build() # создаем объект класса Application
    print('Бот запущен...')

    # добавляем обработчик команды /start
    application.add_handler(CommandHandler("start", start))
    # добавляем обработчик изображений, которые загружаются в Telegram в СЖАТОМ формате
    # (выбирается при попытке прикрепления изображения к сообщению)
    application.add_handler(MessageHandler(filters.PHOTO | filters.Document.ALL | filters.Document.JPG | filters.Document.IMAGE, detection, block=False))
    # application.add_handler(MessageHandler(filters.TEXT, help))
    
    # добавляем обработчик нажатия Inline кнопок
    application.add_handler(CallbackQueryHandler(button))
    
    # добавляем обработчик команды /help
    application.add_handler(CommandHandler("help", help))
    
    # добавляем обработчик текстовых сообщений
    application.add_handler(MessageHandler(filters.TEXT, help))
    
    # запускаем бота (остановка CTRL + C)
    application.run_polling() 


if __name__ == "__main__":
    main()
