from telebot import types
import dic, pymongo

# ОБОЛОЧКА

# подключение MongoDB
db_client = pymongo.MongoClient("mongodb+srv://nasuamba:Sokol366@myfirstcluster.znekeok.mongodb.net/test")
db = db_client["CheckList_PZD_KO"] # БД
c = db["Users"] # пользователи
c_CheckLists = db["CheckLists"] # чек листы
c_CheckBoxes = db["CheckBoxes"] # чек боксы


# приветствие
welcome = types.InlineKeyboardMarkup(row_width = 1)
btn1 = types.InlineKeyboardButton('📋 чек листы', callback_data = 'welcome|чек листы')
btn2 = types.InlineKeyboardButton('👤 личный кабинет', callback_data = 'welcome|личный кабинет')
welcome.add(btn1, btn2)


# выбор роли
role = types.InlineKeyboardMarkup(row_width = 1)
btn1 = types.InlineKeyboardButton('👨‍💻 организатор', callback_data = 'role|организатор')
btn2 = types.InlineKeyboardButton('🙋 инициатор', callback_data = 'role|инициатор')
role.add(btn1, btn2)

# выбор подразделения
unit = types.InlineKeyboardMarkup(row_width = 4)
for i in range(1, 20, 4):
    btn1 = types.InlineKeyboardButton(i, callback_data = f'unit|{i}')
    btn2 = types.InlineKeyboardButton(i+1, callback_data = f'unit|{i+1}')
    btn3 = types.InlineKeyboardButton(i+2, callback_data = f'unit|{i+2}')
    btn4 = types.InlineKeyboardButton(i+3, callback_data = f'unit|{i+3}')
    unit.add(btn1, btn2, btn3, btn4)


def Profile_show():

    keyboard = types.InlineKeyboardMarkup(row_width = 2)

    btn1 = types.InlineKeyboardButton('⬅ назад', callback_data = f'back|back_to_main_menu')
    btn2 = types.InlineKeyboardButton('✏ редактировать', callback_data = f'set|edit profile')
    keyboard.add(btn1, btn2)

    return keyboard

    
# редактировать профиль
profile_set = types.InlineKeyboardMarkup(row_width = 1)
btn1 = types.InlineKeyboardButton('👨‍💻 изменить Роль', callback_data = 'set|role')
btn2 = types.InlineKeyboardButton('👤 изменить ФИО', callback_data = 'set|name')
btn3 = types.InlineKeyboardButton('📞 изменить Телефон', callback_data = 'set|phone')
btn4 = types.InlineKeyboardButton('🏫 изменить Подразделение', callback_data = 'set|unit')
btn5 = types.InlineKeyboardButton('❌ удалить профиль', callback_data = 'set|delite profile')
btn6 = types.InlineKeyboardButton('✅ закончить редактирование', callback_data = 'set|close')
profile_set.add(btn1, btn2, btn3, btn4, btn5, btn6)


# если профиля нет
profile_create = types.InlineKeyboardMarkup(row_width = 1)
btn1 = types.InlineKeyboardButton('👤 создать профиль', callback_data = 'set|create')
btn2 = types.InlineKeyboardButton('⬅ назад', callback_data = 'back|back_to_main_menu')
profile_create.add(btn1, btn2)


# назад
back_to_main  = types.InlineKeyboardMarkup(row_width = 1)
btn1 = types.InlineKeyboardButton('⬅ назад', callback_data = 'back|back_to_main_menu')
back_to_main.add(btn1)


# список активных Чек Листов
def active_CL(ID):
    
    keyboard = types.InlineKeyboardMarkup(row_width = 1)

    # если заполняет организатор
    if c.find_one({'user_id': ID}, {'user_id': 0, '_id': 0, 'ФИО': 0, 'телефон': 0, 'подразделение': 0})['роль'] == 'организатор':
        name = c.find_one({'user_id': ID}, {'user_id': 0, '_id': 0, 'роль': 0, 'телефон': 0, 'подразделение': 0})['ФИО']
        res = c_CheckLists.find({'организатор': name}, {'_id': 0, 'creator_id': 0})
        for doc in res:
            btn1 = types.InlineKeyboardButton(f'РНП: {doc["РНП"]}', callback_data = f'CheckList|doc|{doc["РНП"]}')
            keyboard.add(btn1)
    # если заполняет инициатор
    elif c.find_one({'user_id': ID}, {'user_id': 0, '_id': 0, 'ФИО': 0, 'телефон': 0, 'подразделение': 0})['роль'] == 'инициатор':
        name = c.find_one({'user_id': ID}, {'user_id': 0, '_id': 0, 'роль': 0, 'телефон': 0, 'подразделение': 0})['ФИО']
        res = c_CheckLists.find({'инициатор': name}, {'_id': 0, 'creator_id': 0})
        for doc in res:
            btn1 = types.InlineKeyboardButton(f'РНП: {doc["РНП"]}', callback_data = f'CheckList|doc|{doc["РНП"]}')
            keyboard.add(btn1)

    btn1 = types.InlineKeyboardButton('➕ создать новый чек лист', callback_data = 'CheckList|create')
    btn2 = types.InlineKeyboardButton('⬅ назад', callback_data = 'back|back_to_main_menu')
    keyboard.add(btn1, btn2)

    return keyboard


def CL_show(RNP):

    keyboard = types.InlineKeyboardMarkup(row_width = 2)

    btn1 = types.InlineKeyboardButton('⬅ назад', callback_data = f'back|back_to_main_menu|{RNP}')
    btn2 = types.InlineKeyboardButton('🆗 открыть', callback_data = f'CheckList|open|{RNP}')
    keyboard.add(btn1, btn2)
    btn3 = types.InlineKeyboardButton('✏ редактировать', callback_data = f'CheckList|edit|{RNP}')
    keyboard.add(btn3)

    return keyboard


def CL_edit(RNP):

    keyboard = types.InlineKeyboardMarkup(row_width = 1)
    btn1 = types.InlineKeyboardButton('️️#️⃣ изменить РНП', callback_data = f'set|RNP|{RNP}')
    btn2 = types.InlineKeyboardButton('👨‍💻 ФИО организатора', callback_data = f'set|organizer|{RNP}')
    btn3 = types.InlineKeyboardButton('🙋 ФИО инициатора', callback_data = f'set|initiator|{RNP}')
    btn4 = types.InlineKeyboardButton('❌ удалить чек лист', callback_data = f'CheckList|delite CheckList|{RNP}')
    btn5 = types.InlineKeyboardButton('✅ закончить редактирование', callback_data = f'CheckList|close|{RNP}')
    keyboard.add(btn1, btn2, btn3, btn4, btn5)

    return keyboard


# ЧЕК ЛИСТ

def ChekBox(RNP):

    docs = types.InlineKeyboardMarkup(row_width = 2)
    for i in dic.docs_lst:
        btn1 = types.InlineKeyboardButton(i, callback_data = f'ChekBox|{i}|{RNP}')
        if c_CheckBoxes.find_one({'РНП': RNP})[i]:
            btn2 = types.InlineKeyboardButton('✅', callback_data = f'ChekBox|✅{i}|{RNP}')
        else:
            btn2 = types.InlineKeyboardButton('❌', callback_data = f'ChekBox|❌{i}|{RNP}')
        docs.add(btn1, btn2)

    btn1 = types.InlineKeyboardButton('⬅ назад', callback_data = f'ChekBox|back_to_CheckList|{RNP}')
    docs.add(btn1)

    return docs

def back_from_CheckBox(RNP):
    keyboard  = types.InlineKeyboardMarkup(row_width = 1)
    btn1 = types.InlineKeyboardButton('⬅ назад', callback_data = f'ChekBox|back_to_main_menu|{RNP}')
    keyboard.add(btn1)

    return keyboard
