import bot_funcs as f
import random


name = "('gosick',)"
release_id = "(-493905522,)"

name = str(name).replace("(", "").replace("'", "").replace(",", "").replace(")", "").strip()
release_id = str(release_id).replace("(", "").replace(",", "").replace(")", "").strip()

print(name)
print(release_id)


"""
activeUsers = cl.getActiveUsers()
newUserKey = '393313942'

string = 'deнt'


UserName = f.getKeyByValue(activeUsers, newUserKey)

print(UserName)

if UserName == None:
    newUserName = "New_User_" + str(random.randint(0,1000))
    cl.addActiveUser(newUserName, newUserKey)
    print("Создан новый юзер: " + newUserName)
else:
    print("Такой пользователь уже есть!")
#print(activeUsers.get(newUser))"""