import DB_loader as cl
import bot_funcs as f
import logging
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

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)