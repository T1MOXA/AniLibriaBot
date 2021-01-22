import config_loader as cl
from sqlighter import SQLighter
import bot_funcs as f

import logging
from datetime import datetime
import asyncio

from aiogram import Bot, Dispatcher, executor, types

logging.basicConfig(level=logging.INFO)

token = cl.get_token()
bot = Bot(token)
dp = Dispatcher(bot)
db = SQLighter(cl.get_DB())

@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    await message.answer("Привет, " + message.from_user.username + "!\nЯ бот, созданный для контроля за релизами. Для получения информации по моей настройке напиши /help.")

@dp.message_handler(commands=["help"])
async def help(message: types.Message):
    await message.answer(f.get_help())

@dp.message_handler(commands=["new_release"])
async def new_release(message: types.Message):
    if (int(message.chat.id) < 0):
        activeReleases = SQLighter.get_active_releases(db)
        releaseToken = str(message.chat.id)
        releaseName = f.get_key_by_value(activeReleases, releaseToken)
        if (releaseName != None):
            await message.answer("Для этого чата релиза уже создан релиз \"" + releaseName + "\".")
        else:
            releaseName = message.text.replace("/new_release", '').strip()
            if (f.check_valid_string(releaseName)):
                SQLighter.add_release(db, message.chat.id, releaseName)
                await message.answer("Создан новый релиз \"" + releaseName + "\".")
            else:
                if (f.check_valid_string(message.chat.title)):
                    SQLighter.add_release(db, message.chat.id, message.chat.title)
                    await message.answer("Создан новый релиз \"" + message.chat.title + "\".")
                else:
                    await message.answer("Имя релиза не может содержать кириллицу или специальные символы. Введите имя релиза через пробел после команды /new_release.")
    else:
        await message.answer("Для создания нового релиза добавьте меня в чат релиза и вызовите эту команду там.")

@dp.message_handler(commands=["status"])
async def status(message: types.Message):
    if (int(message.chat.id) < 0):
        releaseStatus = f.get_status()
        await message.answer("@" + message.from_user.username + "\n\n" + releaseStatus)
    else:
        releaseName = message.text.replace("/status", '').strip()
        if (f.check_valid_string(releaseName)):
            releaseStatus = f.get_status()
            await message.answer(releaseName + "\n\n" + releaseStatus)
        else:
            await message.answer("@" + message.from_user.username + ", введите название релиза после команды /status для просмотра статуса релиза.")

async def scheduler(wait_for):
    while True:
        await asyncio.sleep(wait_for)
        now = datetime.strftime(datetime.now(), "%X")
        if (now == "21:00:00"):
            activeReleases = SQLighter.get_active_releases(db)
            print(activeReleases)
            for Release in activeReleases:
                releaseStatus = f.get_status()
                await bot.send_message(activeReleases[Release], Release + "\n\n" + releaseStatus, disable_notification=True)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(scheduler(1))
    executor.start_polling(dp, skip_updates=True)