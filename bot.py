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
    await message.answer("Привет, " + message.from_user.username + ".\nЯ менеджер релизов - бот, созданный для контроля за релизами. Для получения информации по моей настройке наберите /help.")

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
            releaseName = message.text.replace("/new_release", '').replace("@AL_RM_Bot", "").strip().split(" ")
            if (f.check_valid_string(releaseName[0])):
                # Релиз создаётся в БД через sqlighter.py
                i = 0
                description = ''
                while (i< len(releaseName)):
                    if (not i == 0):
                        description += releaseName[i] + " "
                    i += 1
                description.strip()
                SQLighter.add_release(db, message.chat.id, releaseName[0].lower(), description)
                await message.answer("Создан новый релиз \"" + releaseName[0].lower() + "\".")
            else:
                if (f.check_valid_string(message.chat.title)):
                    # Берём название конференции как название релиза
                    SQLighter.add_release(db, message.chat.id, str(message.chat.title).lower(), '')
                    await message.answer("Создан новый релиз \"" + message.chat.title + "\".")
                else:
                    await message.answer("Имя релиза не может содержать кириллицу или специальные символы. Введите имя релиза через пробел после команды /new_release.")
    else:
        await message.answer("Для создания нового релиза добавьте бота в чат релиза и вызовите эту команду там.")

# Запуск релиза в работу.
@dp.message_handler(commands=["start_release"])
async def start_release(message: types.Message):
    if (int(message.chat.id) < 0):
        activeReleases = SQLighter.get_active_releases(db)
        releaseToken = str(message.chat.id)
        releaseName = f.get_key_by_value(activeReleases, releaseToken)
        # releaseName = None - если не удалось найти имя уже созданного релиза.
        if (releaseName != None):
            parameters = message.text.replace("/start_release", '').replace("@AL_RM_Bot", "").strip().split(" ")
            parameters[0] = f.set_release_type(parameters[0].lower())
            if (parameters[0] > 0 and len(parameters) < 5):
                SQLighter.add_episodes_info(db, message.chat.id, parameters)
                await message.answer("Релиз запущен в работу. Текущее состояние релиза можно узнать командой /status.")
            else:
                message.answer("Неверно введены параметры для старта релиза. Для справки наберите команду /help.")
        else:
            await message.answer("Для этого чата не создано ни одного релиза. Создайте релиз командой /new_release [Release_name].")
    else:
        await message.answer("Для старта релиза добавьте бота в чат релиза и вызовите эту команду там.")

# Отображение статуса релиза
@dp.message_handler(commands=["status"])
async def status(message: types.Message):
    if (int(message.chat.id) < 0):
        releaseStatus = f.get_status(db, message.chat.id)
        await message.answer("@" + message.from_user.username + "\n\n" + releaseStatus)
    else:
        releaseName = message.text.replace("/status", '').replace("@AL_RM_Bot", "").strip()
        if (f.check_valid_string(releaseName)):
            activeReleases = SQLighter.get_active_releases(db)
            try:
                release_id = activeReleases[releaseName.lower()]
                releaseStatus = f.get_status(db, release_id)
                await message.answer(releaseName.lower() + "\n\n" + releaseStatus)
            except:
                await message.answer("Релиз \"" + releaseName + "\" не найден. Проверьте правильность написания названия релиза. Список активных релизов можно посмотреть командой /active_releases.")
        else:
            await message.answer("@" + message.from_user.username + ", введите название релиза после команды /status для просмотра статуса или введите эту команду в чат релиза. Список активных релизов можно посмотреть командой /active_releases.")

# Список активных релизов
@dp.message_handler(commands=["active_releases"])
async def get_active_releases_list(message: types.Message):
    if (int(message.chat.id) < 0):
        await message.answer("Данная команда работает только в личных сообщениях.")
    else:
        activeReleases = SQLighter.get_active_releases(db)
        description = SQLighter.get_description(db)
        releaseList = 'Список активных релизов:\n'
        i = 0
        for release in activeReleases:
            i += 1
            desc = str(description[i-1]).replace("(", "").replace(")", "").replace("'", "")[:-1]
            if (desc != "None"):
                releaseList += str(i) + ". " + release + " - " + desc.strip() + "\n"
            else:
                releaseList += str(i) + ". " + release + "\n"
        releaseList += "\nДля вызова статуса релиза наберите \"/status [Release_name]\", где Release_name - название релиза из списка."
        await message.answer(releaseList)

# Функция (шедулер) для ежедневной отправки статуса по активным релизам. Активна постоянно, проверятся раз в секунду.
async def scheduler(wait_for):
    while True:
        await asyncio.sleep(wait_for)
        now = datetime.strftime(datetime.now(pytz.timezone('Europe/Moscow')), "%X")
        if (now == "20:00:00"):
            activeReleases = SQLighter.get_active_releases(db)
            for Release in activeReleases:
                releaseStatus = f.get_status(db, activeReleases[Release])
                await bot.send_message(activeReleases[Release], Release + "\n\n" + releaseStatus, disable_notification=True)
        if (now == "00:00:00"):
            activeReleases = SQLighter.get_active_releases(db)
            for Release in activeReleases:
                f.increase_day(db, activeReleases[Release])

# Стартовая функция для запуска бота.
if __name__ == "__main__":
    # Создаём новый циклический ивент для запуска шедулера.
    loop = asyncio.get_event_loop()
    loop.create_task(scheduler(1))
    # Начало прослушки и готовности ботом принимать команды (long polling).
    executor.start_polling(dp, skip_updates=True)