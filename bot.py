'''
Менеджер релизов - бот, предназначенный для контроля за работой над релизами. Он способен сообщать ответственным за релиз, что происходит задержка.
Список файлов проекта:
- bot.py - основной файл для работы бота, здесь работает long polling для перехвата команд. Команды перехватыватываются через @dp.message_handler.
- bot_funcs.py - вспомогательный файл бота, содержит функции для его работы (составление отчёта по статусу, справки и т.д.).
- config_loader.py - файл для подгрузки данных из файла конфигурации.
- sqlighter.py - файл для подгрузки данных из БД SQLighter, в т.ч. список релизов, статус и их привязку к конференциям в телеграме.
- config.cfg - файл конфигурации.
- db.db - база данных со списком релизов.
- requirements.txt - список библиотек/зависимостей проекта.
'''

import config_loader as cl
from sqlighter import SQLighter
import bot_funcs as f

import logging
from datetime import datetime
import pytz
import asyncio
from aiogram import Bot, Dispatcher, executor, types

logging.basicConfig(level=logging.INFO)

token = cl.get_token()
bot = Bot(token)
dp = Dispatcher(bot)
db = SQLighter(cl.get_DB())

# Запускается при первом запуске бота в ЛС.
@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    await message.answer("Привет, " + message.from_user.username + "!\nЯ бот, созданный для контроля за релизами. Для получения информации по моей настройке напиши /help.")

# Вывод справки. Содержит описание и список доступных команд.
@dp.message_handler(commands=["help"])
async def help(message: types.Message):
    await message.answer(f.get_help())

# Создание нового релиза.
@dp.message_handler(commands=["new_release"])
async def new_release(message: types.Message):
    # message.chat.id < 0 (отрицательный ID) в том случае, если сообщение пришло из чата. Если больше нуля - это ЛС.
    if (int(message.chat.id) < 0):
        activeReleases = SQLighter.get_active_releases(db)
        releaseToken = str(message.chat.id)
        releaseName = f.get_key_by_value(activeReleases, releaseToken)
        # releaseName = None - если не удалось найти имя уже созданного релиза.
        if (releaseName != None):
            await message.answer("Для этого чата релиза уже создан релиз \"" + releaseName + "\".")
        else:
            releaseName = message.text.replace("/new_release", '').strip()
            if (f.check_valid_string(releaseName)):
                # Релиз создаётся в БД через sqlighter.py
                SQLighter.add_release(db, message.chat.id, releaseName)
                await message.answer("Создан новый релиз \"" + releaseName + "\".")
            else:
                if (f.check_valid_string(message.chat.title)):
                    # Релиз создаётся в БД через sqlighter.py
                    SQLighter.add_release(db, message.chat.id, message.chat.title)
                    await message.answer("Создан новый релиз \"" + message.chat.title + "\".")
                else:
                    await message.answer("Имя релиза не может содержать кириллицу или специальные символы. Введите имя релиза через пробел после команды /new_release.")
    else:
        await message.answer("Для создания нового релиза добавьте меня в чат релиза и вызовите эту команду там.")

# Отображение статуса релиза
@dp.message_handler(commands=["status"])
async def status(message: types.Message):
    if (int(message.chat.id) < 0):
        releaseStatus = f.get_status(db, message.chat.id)
        await message.answer("@" + message.from_user.username + "\n\n" + releaseStatus)
    else:
        releaseName = message.text.replace("/status", '').strip()
        if (f.check_valid_string(releaseName)):
            activeReleases = SQLighter.get_active_releases(db)
            release_id = activeReleases[releaseName]
            releaseStatus = f.get_status(db, release_id)
            await message.answer(releaseName + "\n\n" + releaseStatus)
        else:
            await message.answer("@" + message.from_user.username + ", введите название релиза после команды /status для просмотра статуса или введите эту команду в чат релиза.")

# Функция (шедулер) для ежедневной отправки статуса по активным релизам. Активна постоянно, проверятся раз в секунду.
async def scheduler(wait_for):
    while True:
        await asyncio.sleep(wait_for)
        now = datetime.strftime(datetime.now(pytz.timezone('Europe/Moscow')), "%X")
        if (now == "20:00:00"):
            activeReleases = SQLighter.get_active_releases(db)
            for Release in activeReleases:
                releaseStatus = f.get_status()
                await bot.send_message(activeReleases[Release], Release + "\n\n" + releaseStatus, disable_notification=True)

# Стартовая функция для запуска бота.
if __name__ == "__main__":
    # Создаём новый циклический ивент для запуска шедулера.
    loop = asyncio.get_event_loop()
    loop.create_task(scheduler(1))
    # Начало прослушки и готовности ботом принимать команды (long polling).
    executor.start_polling(dp, skip_updates=True)