import DB_loader as cl
import bot_funcs as f

import logging
from datetime import datetime
import asyncio

from aiogram import Bot, Dispatcher, executor, types

logging.basicConfig(level=logging.INFO)

token = cl.getToken()
bot = Bot(token)
dp = Dispatcher(bot)

@dp.message_handler(commands=["start"])
async def cmd_start(message: types.Message):
    activeUsers = cl.getActiveUsers()
    userToken = str(message.from_user.id)
    userName = f.getKeyByValue(activeUsers, userToken)
    if userName == None:
        newUserName = message.from_user.username
        cl.addActiveUser(newUserName, userToken)
        await message.answer("Привет, " + message.from_user.username + "!")
    else:
        await message.answer("С возвращением, " + message.from_user.username + "!")

@dp.message_handler(commands=["new_release"])
async def new_release(message: types.Message):
    if (int(message.chat.id) < 0):
        activeReleases = cl.getActiveReleases()
        releaseToken = str(message.chat.id)
        releaseName = f.getKeyByValue(activeReleases, releaseToken)
        if (releaseName != None):
            await message.answer("Для этого чата релиза уже создан релиз \"" + releaseName + "\".")
        else:
            releaseName = message.text.replace("/new_release", '').strip()
            if (f.checkValidString(releaseName)):
                cl.addActiveRelease(releaseName, message.chat.id)
                await message.answer("Создан новый релиз \"" + releaseName + "\".")
            else:
                if (f.checkValidString(message.chat.title)):
                    cl.addActiveRelease(message.chat.title, message.chat.id)
                    await message.answer("Создан новый релиз \"" + message.chat.title + "\".")
                else:
                    await message.answer("Имя релиза не может содержать кириллицу или специальные символы. Введите имя релиза через пробел после команды /new_release.")
    else:
        await message.answer("Для создания нового релиза добавьте меня в чат релиза и вызовите эту команду там.")

@dp.message_handler(commands=["status"])
async def status(message: types.Message):
    if (int(message.chat.id) < 0):
        releaseStatus = f.getStatus()
        await message.answer("@" + message.from_user.username + "\n\n" + releaseStatus)
    else:
        releaseName = message.text.replace("/status", '').strip()
        if (f.checkValidString(releaseName)):
            releaseStatus = f.getStatus()
            await message.answer(releaseStatus)
        else:
            await message.answer("@" + message.from_user.username + ", введите название релиза после команды /status для просмотра статуса релиза.")

async def scheduler(wait_for):
    while True:
        await asyncio.sleep(wait_for)
        now = datetime.strftime(datetime.now(), "%X")
        if (now == "20:00:00"):
            activeReleases = cl.getActiveReleases()
            for Release in activeReleases:
                releaseStatus = f.getStatus()
                await bot.send_message(activeReleases[Release], Release + "\n\n" + releaseStatus, disable_notification=True)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(scheduler(1))
    executor.start_polling(dp, skip_updates=True)