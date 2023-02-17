import pymongo


# подключение MongoDB
db_client = pymongo.MongoClient("mongodb+srv://nasuamba:Sokol366@myfirstcluster.znekeok.mongodb.net/test")
db = db_client["CheckList_PZD_KO"] # БД
c = db["Users"] # коллекция
c_CheckLists = db["CheckLists"] # коллекция


# функция для записи в mongoDB
def DB_EDIT(collection, filter_field, filter_value, field, value):
    if collection.find_one({filter_field: filter_value}) == None:
        collection.insert_one({filter_field: filter_value, field: value})
    else:
        filter = {filter_field: filter_value} # обновляемый документ
        newvalues = {"$set": {field: value}} # новвое значение
        collection.update_one(filter, newvalues)


def PROFILE_SHOW(ID):
            if c.find_one({'user_id': ID}, {'user_id': 0, '_id': 0, 'ФИО': 0, 'телефон': 0, 'подразделение': 0}) == {}:
                role = 'пусто'
            else:
                role = c.find_one({'user_id': ID}, {'user_id': 0, '_id': 0, 'ФИО': 0, 'телефон': 0, 'подразделение': 0})['роль']
            
            if c.find_one({'user_id': ID}, {'user_id': 0, '_id': 0, 'роль': 0, 'телефон': 0, 'подразделение': 0}) == {}:
                name = 'пусто'
            else:
                name = c.find_one({'user_id': ID}, {'user_id': 0, '_id': 0, 'роль': 0, 'телефон': 0, 'подразделение': 0})['ФИО']
            
            if c.find_one({'user_id': ID}, {'user_id': 0, '_id': 0, 'роль': 0, 'ФИО': 0, 'подразделение': 0}) == {}:
                phone = 'пусто'
            else:
                phone = c.find_one({'user_id': ID}, {'user_id': 0, '_id': 0, 'роль': 0, 'ФИО': 0, 'подразделение': 0})['телефон']
            
            if c.find_one({'user_id': ID}, {'user_id': 0, '_id': 0, 'роль': 0, 'ФИО': 0, 'телефон': 0}) == {}:
                unit = 'пусто'
            else:
                unit = c.find_one({'user_id': ID}, {'user_id': 0, '_id': 0, 'роль': 0, 'ФИО': 0, 'телефон': 0})['подразделение']


            mess = f'Данные вашего профиля' \
                   f'\n' \
                   f'\n👨‍💻 Роль: {role}' \
                   f'\n👤 ФИО: {name}' \
                   f'\n📞 Телефон: {phone}' \
                   f'\n🏫 Подразделение: {unit}'
            
            return mess


def CHECK_LIST_SHOW(RNP):
    
    try: organizer = c_CheckLists.find_one({'РНП': RNP})['организатор']
    except: organizer = 'пусто'

    try: initiator = c_CheckLists.find_one({'РНП': RNP})['инициатор']
    except: initiator = 'пусто'
    
    mess = f'Чек Лист самопроверки' \
           f'\n' \
           f'\n#️⃣ РНП: {RNP}' \
           f'\n👨‍💻 организатор: {organizer}' \
           f'\n🙋 инициатор: {initiator}'
            
    return mess