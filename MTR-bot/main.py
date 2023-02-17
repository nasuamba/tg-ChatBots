import telebot
import dic
import markup
import config
import os
import pandas as pd
from funcs import *

bot = telebot.TeleBot(config.BOT_TOKEN, skip_pending = True)


# ПОДДЕРЖКА
@bot.message_handler(commands = ["help"])
def help(message):
    mess = 'пожалуйста, введите сообщение для службы поддержки 📨'
    bot.send_message(message.from_user.id, mess, reply_markup = markup.markup_clear)
    bot.register_next_step_handler(message, get_help_msg)


def get_help_msg(message):
    mess = f'бот: @GPNS_mtr_bot\nuser id: {message.from_user.id}\n\nсообщение: {message.text}'
    to_chat_id = -1001528081284
    bot.send_message(to_chat_id, mess)

    mess = 'спасибо 🙏' \
           '\nмы постараемся связаться с вами как можно скорее'
    bot.send_message(message.from_user.id, mess, reply_markup = markup.markup_clear)


# ВЫБОР АТТЕСТАЦИИ МТР
@bot.message_handler(commands = ["start"])
def start(message):
    if not message.from_user.id in dic.main_user_dic:
        # пользовательские словари
        dic.main_user_dic[message.from_user.id] = {i: '' for i in dic.main_user_dic_names}
        dic.main_user_dic[message.from_user.id]['user_id'] = message.from_user.id
        # статус заполнения визуального состояния для каждого объекта каждым пользователем (уровень пользователя)
        dic.VC_dic[message.from_user.id] = {}
        # статус заполнения вопросов по документации для каждого объекта каждым пользователем (уровень пользователя)
        dic.DC_dic[message.from_user.id] = {}
        # статус заполнения каждого меню для каждого объекта каждым пользователем (уровень пользователя)
        dic.check_dic[message.from_user.id] = {}
        # статус заполнения каждого МТР для каждого пользователя (уровень пользователя)
        dic.check_box_dic[message.from_user.id] = {}

        mess = f'Добрый день, {message.from_user.first_name}!\nПожалуйста, выберите номер аттестации МТР'
        bot.send_message(message.from_user.id, mess, reply_markup = markup.insp_num)
        bot.register_next_step_handler(message, get_ins_num)


# существующие команды
comand_list = {'/start': start, '/help': help}


# ВВОД ИМЕНИ
def get_ins_num(message):
    if message.text in comand_list:
        comand_list[message.text](message)
    # проверяем, что инспекция есть в списке
    elif config.is_part_in_list(message.text, dic.ins_lst):
        dic.main_user_dic[message.from_user.id]['table'] = f'mtr_inspection_{message.text}'

        # формируем чекбоксы по выбраной аттестации МТР на основе БД
        all_check_box_create(message.from_user.id)

        mess = 'Пожалуйста, напишите, как к вам обращаться в формате "Путин В.В."'
        bot.send_message(message.from_user.id, mess, reply_markup = markup.bck_to_insp_num)
        bot.register_next_step_handler(message, get_name)
    else:
        mess = 'Я вас не понимаю... Пожалуйста, выберите из предложенных вариантов'
        bot.send_message(message.from_user.id, mess, reply_markup = markup.insp_num)
        bot.register_next_step_handler(message, get_ins_num)


# ВЫБОР ОБЪЕКТА МТР
def get_name(message):
    if message.text in comand_list:
        comand_list[message.text](message)
    elif message.text == '⬅ назад к выбору инспекции':
        mess = 'Пожалуйста, выберите номер аттестации МТР'
        bot.send_message(message.from_user.id, mess, reply_markup = markup.insp_num)
        bot.register_next_step_handler(message, get_ins_num)
    else:
        if message.text != '⬅ назад' and message.text != 'далее ➡️':
            # записываем имя пользователя
            dic.main_user_dic[message.from_user.id]['user_name'] = message.text

        mtr_check_box_create(message.from_user.id, bot)
        bot.register_next_step_handler(message, get_objekt)


# ВЫБОР ПРОВЕРКИ (ГЛАВНОЕ МЕНЮ)
def get_objekt(message):
    if message.text in comand_list:
        comand_list[message.text](message)
    elif message.text == '📄 сформировать акт':
        # формируем Excel отчет
        db = sqlite3.connect('db/mtr_bot.db', check_same_thread = False)
        # c = db.cursor()
        path_file = f"{message.from_user.id}/акт аттестации МТР.xlsx"
        if not str(message.from_user.id) in os.listdir():
            os.mkdir(str(message.from_user.id))
        with pd.ExcelWriter(path_file) as writer:
            doc = pd.read_sql(f"""SELECT user_name, mtr_objekt, VC, DC, sklad, doc_date_from, doc_date_to, VCP,
                              DCP FROM {dic.main_user_dic[message.from_user.id]['table']}""", db)
            doc.to_excel(writer, sheet_name = "отчет", header = dic.hdr, index = False)
            sn = writer.sheets['отчет']
            for i, j in {'A': 20, 'B': 60, 'C': 70, 'D': 50, 'E': 25, 'F': 15, 'G': 15, 'H': 35, 'I': 35}.items():
                sn.column_dimensions[i].width = j

            # отправляем пользователю подтверждение
            mess = 'Запись в акте создана. Спасибо!'
            bot.send_message(message.from_user.id, mess, reply_markup = markup.markup_clear)

            # if not str(message.from_user.id) in os.listdir():
            #     os.mkdir(str(message.from_user.id))

            writer.save()

        db.close()

        # отправляем Excel в чат
        with open(path_file, "rb") as file_send:
            bot.send_document(message.from_user.id, file_send)


    elif config.is_part_in_list(message.text[2:], mtr_objekt_lst) == True:
        # отрезаем первые 2 символа (маркер + пробел) от сообщения и записываем в словарь
        dic.main_user_dic[message.from_user.id]['mtr_objekt'] = message.text[2:]

        db = sqlite3.connect('db/mtr_bot.db', check_same_thread = False)
        c = db.cursor()

        # проверяем, насколько заполнено визуальное состояние по объекту
        c.execute(
            f"""SELECT VC, VCP, sklad FROM {dic.main_user_dic[message.from_user.id]['table']} WHERE mtr_objekt = ?""",
            ((dic.main_user_dic[message.from_user.id]['mtr_objekt']),))
        res = str(c.fetchall()).count('None')
        if res == 0:
            dic.check_dic[message.from_user.id][dic.main_user_dic[message.from_user.id]['mtr_objekt']][
                'визуальное состояние'] = '🟢'
        elif 3 > res > 0:
            dic.check_dic[message.from_user.id][dic.main_user_dic[message.from_user.id]['mtr_objekt']][
                'визуальное состояние'] = '🟡'
        elif res == 3:
            dic.check_dic[message.from_user.id][dic.main_user_dic[message.from_user.id]['mtr_objekt']][
                'визуальное состояние'] = '🔴'

        # проверяем, насколько заполнены документы по объекту
        c.execute(
            f"""SELECT DC, DCP, doc_date_from, doc_date_to FROM {dic.main_user_dic[message.from_user.id]['table']} WHERE mtr_objekt = ?""",
            ((dic.main_user_dic[message.from_user.id]['mtr_objekt']),))
        res = str(c.fetchall()).count('None')
        if res == 0:
            dic.check_dic[message.from_user.id][dic.main_user_dic[message.from_user.id]['mtr_objekt']][
                'документация'] = '🟢'
        elif 4 > res > 0:
            dic.check_dic[message.from_user.id][dic.main_user_dic[message.from_user.id]['mtr_objekt']][
                'документация'] = '🟡'
        elif res == 4:
            dic.check_dic[message.from_user.id][dic.main_user_dic[message.from_user.id]['mtr_objekt']][
                'документация'] = '🔴'

        # db.commit()
        db.close()

        check_menu_markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard = True, row_width = 2)
        for i in ['визуальное состояние', 'документация']:
            btn1 = telebot.types.KeyboardButton(
                f"{dic.check_dic[message.from_user.id][dic.main_user_dic[message.from_user.id]['mtr_objekt']][i]} {i}")
            check_menu_markup.add(btn1)

        btn1 = telebot.types.KeyboardButton('⬅ назад')
        check_menu_markup.add(btn1)

        mess = 'пожалуйста, выберите проверку'
        bot.send_message(message.from_user.id, mess, reply_markup = check_menu_markup)
        bot.register_next_step_handler(message, menu)
    else:
        mess = 'Я вас не понимаю... Пожалуйста, выберите из предложенных вариантов'
        bot.send_message(message.from_user.id, mess, reply_markup = markup.markup_clear)
        get_name(message)


# ЧЕКБОКСЫ ПРОВЕРОК
def menu(message):
    if message.text in comand_list:
        comand_list[message.text](message)
    elif message.text[2:] == 'визуальное состояние':
        mess = 'пожалуйста, ответьте на вопросы'
        # формируем чекбокс по визуальному состоянию
        VC_markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard = True, row_width = 2)
        for i in dic.VC_dic[message.from_user.id][dic.main_user_dic[message.from_user.id]['mtr_objekt']]:
            if dic.VC_dic[message.from_user.id][dic.main_user_dic[message.from_user.id]['mtr_objekt']][i] == False:
                btn1 = telebot.types.KeyboardButton(f'🔴 {i}')
                VC_markup.add(btn1)
            elif dic.VC_dic[message.from_user.id][dic.main_user_dic[message.from_user.id]['mtr_objekt']][i] == True:
                btn1 = telebot.types.KeyboardButton(f'🟢 {i}')
                VC_markup.add(btn1)

        btn1 = telebot.types.KeyboardButton('⬅ назад')
        btn2 = telebot.types.KeyboardButton('далее ➡️')
        VC_markup.add(btn1, btn2)

        bot.send_message(message.from_user.id, mess, reply_markup = VC_markup)
        bot.register_next_step_handler(message, VC_menu)

    elif message.text[2:] == 'документация':
        mess = 'пожалуйста, ответьте на вопросы'
        # формируем чекбокс по документации
        DC_markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard = True, row_width = 2)
        for i in dic.DC_dic[message.from_user.id][dic.main_user_dic[message.from_user.id]['mtr_objekt']]:
            if dic.DC_dic[message.from_user.id][dic.main_user_dic[message.from_user.id]['mtr_objekt']][i] == False:
                btn1 = telebot.types.KeyboardButton(f'🔴 {i}')
                DC_markup.add(btn1)
            elif dic.DC_dic[message.from_user.id][dic.main_user_dic[message.from_user.id]['mtr_objekt']][i] == True:
                btn1 = telebot.types.KeyboardButton(f'🟢 {i}')
                DC_markup.add(btn1)

        btn1 = telebot.types.KeyboardButton('⬅ назад')
        btn2 = telebot.types.KeyboardButton('далее ➡️')
        DC_markup.add(btn1, btn2)

        bot.send_message(message.from_user.id, mess, reply_markup = DC_markup)
        bot.register_next_step_handler(message, DC_menu)

    elif message.text == '⬅ назад':
        get_name(message)
    else:
        mess = 'Я вас не понимаю... Пожалуйста, выберите объект'
        bot.send_message(message.from_user.id, mess, reply_markup = markup.markup_clear)
        get_objekt(message)


# ЧЕКБОКС VC
def VC_menu(message):
    if message.text in comand_list:
        comand_list[message.text](message)
    elif message.text != '⬅ назад' and message.text != 'далее ➡️':
        VC_markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard = True, row_width = 2)
        for i in dic.VC_dic[message.from_user.id][dic.main_user_dic[message.from_user.id]['mtr_objekt']]:
            if message.text[2:] == i:
                if dic.VC_dic[message.from_user.id][dic.main_user_dic[message.from_user.id]['mtr_objekt']][i] == False:
                    dic.VC_dic[message.from_user.id][dic.main_user_dic[message.from_user.id]['mtr_objekt']][i] = True
                elif dic.VC_dic[message.from_user.id][dic.main_user_dic[message.from_user.id]['mtr_objekt']][i] == True:
                    dic.VC_dic[message.from_user.id][dic.main_user_dic[message.from_user.id]['mtr_objekt']][i] = False
            if dic.VC_dic[message.from_user.id][dic.main_user_dic[message.from_user.id]['mtr_objekt']][i] == False:
                btn1 = telebot.types.KeyboardButton(f'🔴 {i}')
                VC_markup.add(btn1)
            elif dic.VC_dic[message.from_user.id][dic.main_user_dic[message.from_user.id]['mtr_objekt']][i] == True:
                btn1 = telebot.types.KeyboardButton(f'🟢 {i}')
                VC_markup.add(btn1)

        btn1 = telebot.types.KeyboardButton('⬅ назад')
        btn2 = telebot.types.KeyboardButton('далее ➡️')
        VC_markup.add(btn1, btn2)
        mess = 'что-то еще?'
        bot.send_message(message.from_user.id, mess, reply_markup = VC_markup)
        bot.register_next_step_handler(message, VC_menu)

    elif message.text == 'далее ➡️':
        # записываем ответы на чекбокс в словарь
        dic.main_user_dic[message.from_user.id]['VC'] = []
        for i in dic.name_VC:
            if dic.VC_dic[message.from_user.id][dic.main_user_dic[message.from_user.id]['mtr_objekt']][i] == True:
                dic.main_user_dic[message.from_user.id]['VC'].append(i)

        db = sqlite3.connect('db/mtr_bot.db', check_same_thread = False)
        c = db.cursor()
        # записываем имя в БД
        c.execute(
            f"""UPDATE {dic.main_user_dic[message.from_user.id]['table']} SET user_name = ? WHERE mtr_objekt = ?""",
            (dic.main_user_dic[message.from_user.id]['user_name'],
             dic.main_user_dic[message.from_user.id]['mtr_objekt']))
        c.execute(f"""UPDATE {dic.main_user_dic[message.from_user.id]['table']} SET user_id = ? WHERE mtr_objekt = ?""",
                  (dic.main_user_dic[message.from_user.id]['user_id'],
                   dic.main_user_dic[message.from_user.id]['mtr_objekt']))

        for i in dic.main_user_dic[message.from_user.id]['VC']:
            c.execute(f"""UPDATE {dic.main_user_dic[message.from_user.id]['table']} SET VC = ? WHERE mtr_objekt = ?""",
                      (f'{i}\n', dic.main_user_dic[message.from_user.id]['mtr_objekt']))
        db.commit()
        db.close()

        mess = 'пожалуйста, выберите тип склада'
        bot.send_message(message.from_user.id, mess, reply_markup = markup.sklad)
        bot.register_next_step_handler(message, get_sklad)

    elif message.text == '⬅ назад':
        # записываем ответы на чекбокс в словарь
        dic.main_user_dic[message.from_user.id]['VC'] = []
        for i in dic.name_VC:
            if dic.VC_dic[message.from_user.id][dic.main_user_dic[message.from_user.id]['mtr_objekt']][i] == True:
                dic.main_user_dic[message.from_user.id]['VC'].append(i)

        db = sqlite3.connect('db/mtr_bot.db', check_same_thread = False)
        c = db.cursor()
        c.execute(f"""UPDATE {dic.main_user_dic[message.from_user.id]['table']} SET VC = ? WHERE mtr_objekt = ?""",
                  (str(dic.main_user_dic[message.from_user.id]['VC']),
                   dic.main_user_dic[message.from_user.id]['mtr_objekt']))
        # извлекаем из БД статус заполнения группы
        c.execute(
            f"""SELECT VC, VCP, sklad FROM {dic.main_user_dic[message.from_user.id]['table']} WHERE mtr_objekt = ?""",
            ((dic.main_user_dic[message.from_user.id]['mtr_objekt']),))
        res = str(c.fetchall()).count('None')
        if res == 0:
            dic.check_dic[message.from_user.id][dic.main_user_dic[message.from_user.id]['mtr_objekt']][
                'визуальное состояние'] = '🟢'
        elif 3 > res > 0:
            dic.check_dic[message.from_user.id][dic.main_user_dic[message.from_user.id]['mtr_objekt']][
                'визуальное состояние'] = '🟡'
        elif res == 3:
            dic.check_dic[message.from_user.id][dic.main_user_dic[message.from_user.id]['mtr_objekt']][
                'визуальное состояние'] = '🔴'

        c.execute(
            f"""SELECT DC, DCP, doc_date_from, doc_date_to FROM {dic.main_user_dic[message.from_user.id]['table']} WHERE mtr_objekt = ?""",
            ((dic.main_user_dic[message.from_user.id]['mtr_objekt']),))
        res = str(c.fetchall()).count('None')
        if res == 0:
            dic.check_dic[message.from_user.id][dic.main_user_dic[message.from_user.id]['mtr_objekt']][
                'документация'] = '🟢'
        elif 4 > res > 0:
            dic.check_dic[message.from_user.id][dic.main_user_dic[message.from_user.id]['mtr_objekt']][
                'документация'] = '🟡'
        elif res == 4:
            dic.check_dic[message.from_user.id][dic.main_user_dic[message.from_user.id]['mtr_objekt']][
                'документация'] = '🔴'

        db.commit()
        db.close()

        check_menu_markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard = True, row_width = 2)
        for i in dic.check_dic[message.from_user.id][dic.main_user_dic[message.from_user.id]['mtr_objekt']]:
            btn1 = telebot.types.KeyboardButton(
                f"{dic.check_dic[message.from_user.id][dic.main_user_dic[message.from_user.id]['mtr_objekt']][i]} {i}")
            check_menu_markup.add(btn1)

        btn1 = telebot.types.KeyboardButton('⬅ назад')
        check_menu_markup.add(btn1)

        mess = 'пожалуйста, выберите проверку'
        bot.send_message(message.from_user.id, mess, reply_markup = check_menu_markup)
        bot.register_next_step_handler(message, menu)


# ЗАПИСЫВАЕМ ТИП СКЛАДА
def get_sklad(message):
    if message.text in comand_list:
        comand_list[message.text](message)
    elif message.text != '⬅ назад' and message.text != 'далее ➡️':
        # записываем ответ в словарь
        dic.main_user_dic[message.from_user.id]['sklad'] = message.text

        db = sqlite3.connect('db/mtr_bot.db', check_same_thread = False)
        c = db.cursor()

        # записываем имя в БД
        c.execute(
            f"""UPDATE {dic.main_user_dic[message.from_user.id]['table']} SET user_name = ? WHERE mtr_objekt = ?""",
            (dic.main_user_dic[message.from_user.id]['user_name'],
             dic.main_user_dic[message.from_user.id]['mtr_objekt']))
        c.execute(f"""UPDATE {dic.main_user_dic[message.from_user.id]['table']} SET user_id = ? WHERE mtr_objekt = ?""",
                  (dic.main_user_dic[message.from_user.id]['user_id'],
                   dic.main_user_dic[message.from_user.id]['mtr_objekt']))

        c.execute(f"""UPDATE {dic.main_user_dic[message.from_user.id]['table']} SET sklad = ? WHERE mtr_objekt = ?""",
                  (dic.main_user_dic[message.from_user.id]['sklad'],
                   dic.main_user_dic[message.from_user.id]['mtr_objekt']))
        db.commit()
        db.close()

        mess = 'пожалуйста, приложите фото объекта МТР'
        bot.send_message(message.from_user.id, mess, reply_markup = markup.twix)
        bot.register_next_step_handler(message, get_VCP)
    elif message.text == '⬅ назад':
        VC_markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard = True, row_width = 2)
        for i in dic.VC_dic[message.from_user.id][dic.main_user_dic[message.from_user.id]['mtr_objekt']]:
            if message.text[2:] == i:
                if dic.VC_dic[message.from_user.id][dic.main_user_dic[message.from_user.id]['mtr_objekt']][i] == False:
                    dic.VC_dic[message.from_user.id][dic.main_user_dic[message.from_user.id]['mtr_objekt']][i] = True
                elif dic.VC_dic[message.from_user.id][dic.main_user_dic[message.from_user.id]['mtr_objekt']][i] == True:
                    dic.VC_dic[message.from_user.id][dic.main_user_dic[message.from_user.id]['mtr_objekt']][i] = False

            if dic.VC_dic[message.from_user.id][dic.main_user_dic[message.from_user.id]['mtr_objekt']][i] == False:
                btn1 = telebot.types.KeyboardButton(f'🔴 {i}')
                VC_markup.add(btn1)
            elif dic.VC_dic[message.from_user.id][dic.main_user_dic[message.from_user.id]['mtr_objekt']][i] == True:
                btn1 = telebot.types.KeyboardButton(f'🟢 {i}')
                VC_markup.add(btn1)

        btn1 = telebot.types.KeyboardButton('⬅ назад')
        btn2 = telebot.types.KeyboardButton('далее ➡️')
        VC_markup.add(btn1, btn2)
        mess = 'что-то еще?'
        bot.send_message(message.from_user.id, mess, reply_markup = VC_markup)
        bot.register_next_step_handler(message, VC_menu)
    elif message.text == 'далее ➡️':
        mess = 'пожалуйста, приложите фото объекта МТР'
        bot.send_message(message.from_user.id, mess, reply_markup = markup.twix)
        # bot.register_next_step_handler(message, get_VCP)
        bot.register_next_step_handler(message, photo)


@bot.message_handler(content_types = ['photo'])
def photo(message):
    mtr_objekt = dic.main_user_dic[message.from_user.id]['mtr_objekt']
    if not str(mtr_objekt) in os.listdir():
        os.mkdir(str(mtr_objekt))

    fileID = message.photo[-1].file_id
    file_info = bot.get_file(fileID)
    downloaded_file = bot.download_file(file_info.file_path)
    dic.photo_count += 1
    with open(f"{mtr_objekt}/img_{dic.photo_count}.jpg", 'wb') as new_file:
        new_file.write(downloaded_file)

    mess = 'фото загружено!'
    bot.send_message(message.from_user.id, mess, reply_markup = markup.photo_add)
    bot.register_next_step_handler(message, get_VCP)


# ФОТО МТР
def get_VCP(message):
    if message.text in comand_list:
        comand_list[message.text](message)
    elif message.text == 'добавить фото':
        photo(message)
    elif message.text == '⬅ назад':
        mess = 'пожалуйста, выберите тип склада'
        bot.send_message(message.from_user.id, mess, reply_markup = markup.sklad)
        bot.register_next_step_handler(message, get_sklad)
    elif message.text == 'далее ➡️':
        get_name(message)


# ЧЕКБОКС DC
def DC_menu(message):
    if message.text in comand_list:
        comand_list[message.text](message)
    elif message.text != '⬅ назад' and message.text != 'далее ➡️':
        DC_markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard = True, row_width = 2)
        for i in dic.DC_dic[message.from_user.id][dic.main_user_dic[message.from_user.id]['mtr_objekt']]:
            if message.text[2:] == i:
                if dic.DC_dic[message.from_user.id][dic.main_user_dic[message.from_user.id]['mtr_objekt']][i] == False:
                    dic.DC_dic[message.from_user.id][dic.main_user_dic[message.from_user.id]['mtr_objekt']][i] = True
                elif dic.DC_dic[message.from_user.id][dic.main_user_dic[message.from_user.id]['mtr_objekt']][i] == True:
                    dic.DC_dic[message.from_user.id][dic.main_user_dic[message.from_user.id]['mtr_objekt']][i] = False

            if dic.DC_dic[message.from_user.id][dic.main_user_dic[message.from_user.id]['mtr_objekt']][i] == False:
                btn1 = telebot.types.KeyboardButton(f'🔴 {i}')
                DC_markup.add(btn1)
            elif dic.DC_dic[message.from_user.id][dic.main_user_dic[message.from_user.id]['mtr_objekt']][i] == True:
                btn1 = telebot.types.KeyboardButton(f'🟢 {i}')
                DC_markup.add(btn1)

        btn1 = telebot.types.KeyboardButton('⬅ назад')
        btn2 = telebot.types.KeyboardButton('далее ➡️')
        DC_markup.add(btn1, btn2)
        mess = 'что-то еще?'
        bot.send_message(message.from_user.id, mess, reply_markup = DC_markup)
        bot.register_next_step_handler(message, DC_menu)

    elif message.text == 'далее ➡️':
        # записываем ответы на чекбокс в словарь
        dic.main_user_dic[message.from_user.id]['DC'] = []
        for i in dic.name_DC:
            if dic.DC_dic[message.from_user.id][dic.main_user_dic[message.from_user.id]['mtr_objekt']][i] == True:
                dic.main_user_dic[message.from_user.id]['DC'].append(i)

        db = sqlite3.connect('db/mtr_bot.db', check_same_thread = False)
        c = db.cursor()

        # записываем имя в БД
        c.execute(
            f"""UPDATE {dic.main_user_dic[message.from_user.id]['table']} SET user_name = ? WHERE mtr_objekt = ?""",
            (dic.main_user_dic[message.from_user.id]['user_name'],
             dic.main_user_dic[message.from_user.id]['mtr_objekt']))
        c.execute(f"""UPDATE {dic.main_user_dic[message.from_user.id]['table']} SET user_id = ? WHERE mtr_objekt = ?""",
                  (dic.main_user_dic[message.from_user.id]['user_id'],
                   dic.main_user_dic[message.from_user.id]['mtr_objekt']))

        c.execute(f"""UPDATE {dic.main_user_dic[message.from_user.id]['table']} SET DC = ? WHERE mtr_objekt = ?""",
                  (str(dic.main_user_dic[message.from_user.id]['DC']),
                   dic.main_user_dic[message.from_user.id]['mtr_objekt']))
        db.commit()
        db.close()

        mess = 'пожалуйста, укажите дату изготовления'
        bot.send_message(message.from_user.id, mess, reply_markup = markup.twix)
        bot.register_next_step_handler(message, get_doc_date_from)

    elif message.text == '⬅ назад':
        # записываем ответы на чекбокс в словарь
        dic.main_user_dic[message.from_user.id]['DC'] = []
        for i in dic.name_DC:
            if dic.DC_dic[message.from_user.id][dic.main_user_dic[message.from_user.id]['mtr_objekt']][i] == True:
                dic.main_user_dic[message.from_user.id]['DC'].append(i)

        db = sqlite3.connect('db/mtr_bot.db', check_same_thread = False)
        c = db.cursor()
        c.execute(f"""UPDATE {dic.main_user_dic[message.from_user.id]['table']} SET DC = ? WHERE mtr_objekt = ?""",
                  (str(dic.main_user_dic[message.from_user.id]['DC']),
                   dic.main_user_dic[message.from_user.id]['mtr_objekt']))
        # извлекаем из БД статус заполнения группы
        c.execute(
            f"""SELECT VC, VCP, sklad FROM {dic.main_user_dic[message.from_user.id]['table']} WHERE mtr_objekt = ?""",
            ((dic.main_user_dic[message.from_user.id]['mtr_objekt']),))
        res = str(c.fetchall()).count('None')
        if res == 0:
            dic.check_dic[message.from_user.id][dic.main_user_dic[message.from_user.id]['mtr_objekt']][
                'визуальное состояние'] = '🟢'
        elif 3 > res > 0:
            dic.check_dic[message.from_user.id][dic.main_user_dic[message.from_user.id]['mtr_objekt']][
                'визуальное состояние'] = '🟡'
        elif res == 3:
            dic.check_dic[message.from_user.id][dic.main_user_dic[message.from_user.id]['mtr_objekt']][
                'визуальное состояние'] = '🔴'

        c.execute(
            f"""SELECT DC, DCP, doc_date_from, doc_date_to FROM {dic.main_user_dic[message.from_user.id]['table']} WHERE mtr_objekt = ?""",
            ((dic.main_user_dic[message.from_user.id]['mtr_objekt']),))
        res = str(c.fetchall()).count('None')
        if res == 0:
            dic.check_dic[message.from_user.id][dic.main_user_dic[message.from_user.id]['mtr_objekt']][
                'документация'] = '🟢'
        elif 4 > res > 0:
            dic.check_dic[message.from_user.id][dic.main_user_dic[message.from_user.id]['mtr_objekt']][
                'документация'] = '🟡'
        elif res == 4:
            dic.check_dic[message.from_user.id][dic.main_user_dic[message.from_user.id]['mtr_objekt']][
                'документация'] = '🔴'

        db.commit()
        db.close()

        check_menu_markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard = True, row_width = 2)
        for i in dic.check_dic[message.from_user.id][dic.main_user_dic[message.from_user.id]['mtr_objekt']]:
            btn1 = telebot.types.KeyboardButton(
                f"{dic.check_dic[message.from_user.id][dic.main_user_dic[message.from_user.id]['mtr_objekt']][i]} {i}")
            check_menu_markup.add(btn1)

        btn1 = telebot.types.KeyboardButton('⬅ назад')
        check_menu_markup.add(btn1)

        mess = 'пожалуйста, выберите проверку'
        bot.send_message(message.from_user.id, mess, reply_markup = check_menu_markup)
        bot.register_next_step_handler(message, menu)


# ДАТА ИЗГОТОВЛЕНИЯ
def get_doc_date_from(message):
    if message.text in comand_list:
        comand_list[message.text](message)
    elif message.text != '⬅ назад' and message.text != 'далее ➡️':
        # записываем ответ в словарь
        dic.main_user_dic[message.from_user.id]['doc_date_from'] = message.text

        db = sqlite3.connect('db/mtr_bot.db', check_same_thread = False)
        c = db.cursor()
        # записываем имя в БД
        c.execute(
            f"""UPDATE {dic.main_user_dic[message.from_user.id]['table']} SET user_name = ? WHERE mtr_objekt = ?""",
            (dic.main_user_dic[message.from_user.id]['user_name'],
             dic.main_user_dic[message.from_user.id]['mtr_objekt']))
        c.execute(f"""UPDATE {dic.main_user_dic[message.from_user.id]['table']} SET user_id = ? WHERE mtr_objekt = ?""",
                  (dic.main_user_dic[message.from_user.id]['user_id'],
                   dic.main_user_dic[message.from_user.id]['mtr_objekt']))

        c.execute(
            f"""UPDATE {dic.main_user_dic[message.from_user.id]['table']} SET doc_date_from = ? WHERE mtr_objekt = ?""",
            (dic.main_user_dic[message.from_user.id]['doc_date_from'],
             dic.main_user_dic[message.from_user.id]['mtr_objekt']))
        db.commit()
        db.close()

        mess = 'пожалуйста, укажите дату окончания срока годности'
        bot.send_message(message.from_user.id, mess, reply_markup = markup.twix)
        bot.register_next_step_handler(message, get_doc_date_to)
    elif message.text == '⬅ назад':
        DC_markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard = True, row_width = 2)
        for i in dic.DC_dic[message.from_user.id][dic.main_user_dic[message.from_user.id]['mtr_objekt']]:
            if message.text[2:] == i:
                if dic.DC_dic[message.from_user.id][dic.main_user_dic[message.from_user.id]['mtr_objekt']][i] == False:
                    dic.DC_dic[message.from_user.id][dic.main_user_dic[message.from_user.id]['mtr_objekt']][i] = True
                elif dic.DC_dic[message.from_user.id][dic.main_user_dic[message.from_user.id]['mtr_objekt']][i] == True:
                    dic.DC_dic[message.from_user.id][dic.main_user_dic[message.from_user.id]['mtr_objekt']][i] = False

            if dic.DC_dic[message.from_user.id][dic.main_user_dic[message.from_user.id]['mtr_objekt']][i] == False:
                btn1 = telebot.types.KeyboardButton(f'🔴 {i}')
                DC_markup.add(btn1)
            elif dic.DC_dic[message.from_user.id][dic.main_user_dic[message.from_user.id]['mtr_objekt']][i] == True:
                btn1 = telebot.types.KeyboardButton(f'🟢 {i}')
                DC_markup.add(btn1)

        btn1 = telebot.types.KeyboardButton('⬅ назад')
        btn2 = telebot.types.KeyboardButton('далее ➡️')
        DC_markup.add(btn1, btn2)
        mess = 'что-то еще?'
        bot.send_message(message.from_user.id, mess, reply_markup = DC_markup)
        bot.register_next_step_handler(message, DC_menu)
    elif message.text == 'далее ➡️':
        mess = 'пожалуйста, укажите дату окончания срока годности'
        bot.send_message(message.from_user.id, mess, reply_markup = markup.twix)
        bot.register_next_step_handler(message, get_doc_date_to)


# СРОК ГОДНОСТИ
def get_doc_date_to(message):
    if message.text in comand_list:
        comand_list[message.text](message)
    elif message.text != '⬅ назад' and message.text != 'далее ➡️':
        # записываем ответ в словарь
        dic.main_user_dic[message.from_user.id]['doc_date_to'] = message.text

        db = sqlite3.connect('db/mtr_bot.db', check_same_thread = False)
        c = db.cursor()

        # записываем имя в БД
        c.execute(
            f"""UPDATE {dic.main_user_dic[message.from_user.id]['table']} SET user_name = ? WHERE mtr_objekt = ?""",
            (dic.main_user_dic[message.from_user.id]['user_name'],
             dic.main_user_dic[message.from_user.id]['mtr_objekt']))
        c.execute(f"""UPDATE {dic.main_user_dic[message.from_user.id]['table']} SET user_id = ? WHERE mtr_objekt = ?""",
                  (dic.main_user_dic[message.from_user.id]['user_id'],
                   dic.main_user_dic[message.from_user.id]['mtr_objekt']))

        c.execute(
            f"""UPDATE {dic.main_user_dic[message.from_user.id]['table']} SET doc_date_to = ? WHERE mtr_objekt = ?""",
            (dic.main_user_dic[message.from_user.id]['doc_date_to'],
             dic.main_user_dic[message.from_user.id]['mtr_objekt']))
        db.commit()
        db.close()

        mess = 'пожалуйста, приложите фото документов'
        bot.send_message(message.from_user.id, mess, reply_markup = markup.twix)
        bot.register_next_step_handler(message, get_DCP)
    elif message.text == '⬅ назад':
        mess = 'пожалуйста, укажите дату изготовления'
        bot.send_message(message.from_user.id, mess, reply_markup = markup.twix)
        bot.register_next_step_handler(message, get_doc_date_from)
    elif message.text == 'далее ➡️':
        mess = 'пожалуйста, приложите фото документов'
        bot.send_message(message.from_user.id, mess, reply_markup = markup.twix)
        bot.register_next_step_handler(message, get_DCP)


# ФОТО ДОКУМЕНТОВ
def get_DCP(message):
    if message.text in comand_list:
        comand_list[message.text](message)
    elif message.text != '⬅ назад' and message.text != 'далее ➡️':
        DCP_ID = bot.get_file(message.photo[len(message.photo) - 1].file_id)
        # записываем ответ в словарь
        dic.main_user_dic[message.from_user.id]['DCP'] = []
        dic.main_user_dic[message.from_user.id]['DCP'].append(DCP_ID)

        db = sqlite3.connect('db/mtr_bot.db', check_same_thread = False)
        c = db.cursor()

        # записываем имя в БД
        c.execute(
            f"""UPDATE {dic.main_user_dic[message.from_user.id]['table']} SET user_name = ? WHERE mtr_objekt = ?""",
            (dic.main_user_dic[message.from_user.id]['user_name'],
             dic.main_user_dic[message.from_user.id]['mtr_objekt']))
        c.execute(f"""UPDATE {dic.main_user_dic[message.from_user.id]['table']} SET user_id = ? WHERE mtr_objekt = ?""",
                  (dic.main_user_dic[message.from_user.id]['user_id'],
                   dic.main_user_dic[message.from_user.id]['mtr_objekt']))

        c.execute(f"""UPDATE {dic.main_user_dic[message.from_user.id]['table']} SET DCP = ? WHERE mtr_objekt = ?""",
                  (str(dic.main_user_dic[message.from_user.id]['DCP']),
                   dic.main_user_dic[message.from_user.id]['mtr_objekt']))
        db.commit()
        db.close()

        mess = 'фото загружено!'
        bot.send_message(message.from_user.id, mess, reply_markup = markup.twix)
        bot.register_next_step_handler(message, get_DCP)
    elif message.text == '⬅ назад':
        mess = 'пожалуйста, укажите дату окончания срока годности'
        bot.send_message(message.from_user.id, mess, reply_markup = markup.twix)
        bot.register_next_step_handler(message, get_doc_date_to)
    elif message.text == 'далее ➡️':
        get_name(message)


bot.polling(non_stop = True, interval = 0)
