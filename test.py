import DB_loader as cl
import random

activeUsers = cl.getActiveUsers()
newUserKey = '393313942'

UserName = cl.getKeyByToken(activeUsers, newUserKey)

print(UserName)

if UserName == None:
    newUserName = "New_User_" + str(random.randint(0,1000))
    cl.addActiveUser(newUserName, newUserKey)
    print("Создан новый юзер: " + newUserName)
else:
    print("Такой пользователь уже есть!")
#print(activeUsers.get(newUser))