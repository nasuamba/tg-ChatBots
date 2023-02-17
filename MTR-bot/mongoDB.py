import pymongo
import pandas as pd
import datetime

# устанавливаем соединение с MongoDB
db_client = pymongo.MongoClient("mongodb+srv://nasuamba:Sokol366@myfirstcluster.znekeok.mongodb.net/test")
# подключаемся к БД MTR_bot, если её нет, то будет создана
current_db = db_client["MTR_bot"]  # dictionary style
# current_db = db_client.MTR_bot - attribute style

# получаем колекцию из нашей БД, если её нет, то будет создана
collection = current_db["MTR_objects"]
collection.drop()


MTR = pd.read_excel("Вход.XLSX", sheet_name="Лист1")

objekt_lst = []
lot_lst = []

for i in range(MTR['Наименование'].count()):
    mtr_objekt = MTR['Наименование'][i]
    objekt_lst.append(mtr_objekt)
    mtr_lot = MTR['Партия'][i]
    lot_lst.append(mtr_lot)
    note = {
        'objekt': mtr_objekt,
        'lot': mtr_lot,
        'VC': False,
        'VCP': False,
        'sklad': False,
        'DC': False,
        'DC': False,
        'DCP': False,
        'doc_date_from': False,
        'doc_date_to': False,
        'created_at': datetime.datetime.utcnow()
        }
    ins_result = collection.insert_one(note)  # добавляет запись в коллекцию