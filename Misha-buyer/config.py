BOT_TOKEN='BOT_TOKEN'

def is_part_in_list(what, where):
    for word in where:
        if word.lower() in what.lower():
            return True
    return False

Y_LOGIN = 'Y_LOGIN'
FROM_EMAIL = 'FROM_EMAIL@yandex.ru' 
MY_PASSWORD = 'PASSWORD'

Y_SERVER = 'smtp.yandex.ru'
Y_PORT = 465