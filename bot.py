import DB_loader as cl
import logging
from aiogram import Bot, Dispatcher, executor, types
logging.basicConfig(level=logging.INFO)

token = cl.getToken()

bot = Bot(token)
dp = Dispatcher(bot)

@dp.message_handler(commands=["start"])
async def cmd_start(message: types.Message):
    activeUsers = cl.getActiveUsers()
    UserKey = str(message.from_user.id)
    UserName = cl.getKeyByToken(activeUsers, UserKey)
    if UserName == None:
        newUserName = message.from_user.username
        cl.addActiveUser(newUserName, UserKey)
        await message.answer("Привет, " + message.from_user.username + "!")
    else:
        await message.answer("С возвращением, " + message.from_user.username + "!")

@dp.message_handler(commands=["new_release"])
async def new_release(message: types.Message):
    print(message.chat.id)
    await message.answer("Создание нового релиза")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)