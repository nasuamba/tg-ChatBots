import sqlite3
from dic import *
from telebot.types import KeyboardButton, ReplyKeyboardMarkup

def all_check_box_create(user_id):
    # подключаем БД
    db = sqlite3.connect('db/mtr_bot.db', check_same_thread=False)
    c = db.cursor()

    for i in range(1, 18, 1):
        # по очереди перебираем объекты МТР и чистим от лишних символов
        c.execute(f"""SELECT mtr_objekt FROM {main_user_dic[user_id]['table']} WHERE rowid = {i}""")
        mtr_objekt = str(c.fetchall())[3:-4]

        # создаем словари для чекбоксов (уровень объекта)
        VC_dic[user_id][mtr_objekt] = {i: False for i in name_VC}
        DC_dic[user_id][mtr_objekt] = {i: False for i in name_DC}
        check_dic[user_id][mtr_objekt] = {i:'🔴' for i in name_check}

        # формируем чекбокс визуального состояния
        c.execute(f"""SELECT VC FROM {main_user_dic[user_id]['table']} WHERE mtr_objekt = ?""",
                 ((mtr_objekt),))
        res = str(c.fetchall())
        for i in name_VC:
            VC_dic[user_id][mtr_objekt][i] = i in res
            
        # формируем чекбокс документации
        c.execute(f"""SELECT DC FROM {main_user_dic[user_id]['table']} WHERE mtr_objekt = ?""",
                 ((mtr_objekt),))
        res = str(c.fetchall())
        for i in name_DC:
            DC_dic[user_id][mtr_objekt][i] = i in res

        # проверяем, насколько заполнено визуальное состояние по объекту
        c.execute(f"""SELECT VC, VCP, sklad FROM {main_user_dic[user_id]['table']} WHERE mtr_objekt = ?""",
                 ((mtr_objekt),))
        res = str(c.fetchall()).count('None')
        if res == 0:
            check_dic[user_id][mtr_objekt]['визуальное состояние'] = '🟢'
        elif 3 > res > 0:
            check_dic[user_id][mtr_objekt]['визуальное состояние'] = '🟡'
        elif res == 3:
            check_dic[user_id][mtr_objekt]['визуальное состояние'] = '🔴'

        # проверяем, насколько заполнены документы по объекту
        c.execute(f"""SELECT DC, DCP, doc_date_from, doc_date_to FROM {main_user_dic[user_id]['table']} WHERE mtr_objekt = ?""",
                 ((mtr_objekt),))
        res = str(c.fetchall()).count('None')
        if res == 0:
            check_dic[user_id][mtr_objekt]['документация'] = '🟢'
        elif 4 > res > 0:
            check_dic[user_id][mtr_objekt]['документация'] = '🟡'
        elif res == 4:
            check_dic[user_id][mtr_objekt]['документация'] = '🔴'

    db.close()


mtr_objekt_lst = []

def mtr_check_box_create(user_id, bot):
    mess = 'Пожалуйста, выберите объект для проверки:\n\n<i>🟢 - проверен\n🟡 - частично проверен\n🔴 - не проверен</i>'
    # подключаем БД
    db = sqlite3.connect('db/mtr_bot.db', check_same_thread=False)
    c = db.cursor()
    MTR_markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    btn1 = KeyboardButton('📄 сформировать акт')
    MTR_markup.add(btn1)
        
    for i in range(1, 18, 1):
        # по очереди перебираем объекты МТР
        c.execute(f"""SELECT mtr_objekt FROM {main_user_dic[user_id]['table']} WHERE rowid = {i}""")
        # чистим от лишних символов
        mtr_objekt = str(c.fetchall())[3:-4]
        mtr_objekt_lst.append(mtr_objekt)

        # извлекаем из БД статус заполнения по объекту
        c.execute(f"""SELECT VC, VCP, sklad, DC, DCP, doc_date_from, doc_date_to FROM 
                  {main_user_dic[user_id]['table']} WHERE rowid = {i}""")
        res = str(c.fetchall()).count('None')
        if res == 0:
            check_box_dic[user_id][mtr_objekt] = '🟢'
        elif 7 > res > 0 :
            check_box_dic[user_id][mtr_objekt] = '🟡'
        elif res == 7:
            check_box_dic[user_id][mtr_objekt] = '🔴'
        # приписываем кнопке
        btn1 = KeyboardButton(f'{check_box_dic[user_id][mtr_objekt]} {mtr_objekt}')
        MTR_markup.add(btn1)
    db.commit()
    db.close()
    
    bot.send_message(user_id, mess, parse_mode = 'html', reply_markup = MTR_markup)