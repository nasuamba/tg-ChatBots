from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import telebot, config, markup, dic, sqlite3, smtplib, func
from telebot import types
import pandas as pd
import openpyxl
import os


bot = telebot.TeleBot(config.BOT_TOKEN, skip_pending = True)


@bot.message_handler(commands = ["start"])
def start(message):
    
    # пользовательский словарь
    dic.user_dic[message.from_user.id] = {i: '-' for i in dic.user_lst}
    dic.user_dic[message.from_user.id]['id'] = message.from_user.id
    dic.user_dic[message.from_user.id]['имя'] = message.from_user.first_name
    dic.user_dic[message.from_user.id]['фамилия'] = message.from_user.last_name
    # словарь бота
    dic.bot_dic[message.from_user.id] = {i: '-' for i in dic.bot_lst}
    dic.bot_dic[message.from_user.id]['пароль'] = False

    mess = 'Пожалуйста, введите пароль 🔒'
    bot.send_message(message.from_user.id, mess, reply_markup = markup.pswd_markup)
    bot.register_next_step_handler(message, verification)


@bot.message_handler(commands = ["instruction"])
def instruction(message):
    mess = dic.instr
    bot.send_message(message.chat.id, mess, parse_mode='html', reply_markup = markup.simple_back_markup)
    if dic.bot_dic[message.from_user.id]['пароль']:
        mess = 'как я могу вам помочь?'
        bot.send_message(message.chat.id, mess, reply_markup = markup.start_markup)
        bot.register_next_step_handler(message, get_need)
    else:
        mess = 'Пожалуйста, введите пароль 🔒'
        bot.send_message(message.chat.id, mess, reply_markup = markup.pswd_markup)
        bot.register_next_step_handler(message, verification)


@bot.message_handler(commands = ["help"])
def help(message):
    mess = 'пожалуйста, введите сообщение для службы поддержки 📨'
    bot.send_message(message.from_user.id, mess, reply_markup = markup.simple_back_markup)
    bot.register_next_step_handler(message, get_help_msg)
    
def get_help_msg(message):
    if message.text != '⬅ назад':
        mess = f'бот: @GPNS_expert_bot' \
               f'\nnuser id: {message.from_user.id}' \
               f'\n' \
               f'\nсообщение: {message.text}'
        to_chat_id = 'test'
        bot.send_message(to_chat_id, mess)

        mess = 'спасибо 🙏' \
               '\nмы постараемся связаться с вами как можно скорее'
        bot.send_message(message.from_user.id, mess, reply_markup = markup.simple_back_markup)
        if dic.bot_dic[message.from_user.id]['пароль']:
            mess = 'как я могу вам помочь?'
            bot.send_message(message.chat.id, mess, reply_markup = markup.start_markup)
            bot.register_next_step_handler(message, get_need)
        else:
            mess = 'Пожалуйста, введите пароль 🔒'
            bot.send_message(message.chat.id, mess, reply_markup = markup.pswd_markup)
            bot.register_next_step_handler(message, verification)
    elif message.text == '⬅ назад' and dic.bot_dic[message.from_user.id]['пароль']:
        mess = 'как я могу вам помочь?'
        bot.send_message(message.chat.id, mess, reply_markup = markup.start_markup)
        bot.register_next_step_handler(message, get_need)
    else:
        mess = 'Пожалуйста, введите пароль 🔒'
        bot.send_message(message.chat.id, mess, reply_markup = markup.pswd_markup)
        bot.register_next_step_handler(message, verification)


# существующие команды
comand_list = {'/start': start, '/help': help, '/instruction': instruction}


def verification(message):
    if message.text in comand_list:
        comand_list[message.text](message)
    elif message.text == '19':
        dic.bot_dic[message.from_user.id]['пароль'] = True
        mess = 'как я могу вам помочь?'
        bot.send_message(message.chat.id, mess, reply_markup = markup.start_markup)
        bot.register_next_step_handler(message, get_need)
    elif message.text == 'я не знаю пароль 😟':
        comand_list['/help'](message)
    else:
        mess = 'пароль неверный 🔒\nпопробуйте еще раз'
        bot.send_message(message.chat.id, mess, reply_markup = markup.pswd_markup)
        bot.register_next_step_handler(message, verification)


def get_need(message):
    if message.text in comand_list:
        comand_list[message.text](message)
    elif config.is_part_in_list(message.text, dic.need_lst):
        dic.user_dic[message.from_user.id]['задача'] = message.text

        db = sqlite3.connect('db/misha_bot.db', check_same_thread=False)
        c = db.cursor()
        c.execute('INSERT INTO user_info (ID, имя, фамилия, задача) VALUES (?, ?, ?, ?)',
        (dic.user_dic[message.from_user.id]['id'], dic.user_dic[message.from_user.id]['имя'], dic.user_dic[message.from_user.id]['фамилия'], dic.user_dic[message.from_user.id]['задача'])); 
        db.commit()
        db.close()

        if message.text == 'искать информацию 🔍':
            mess = '<u>выберите вариант поиска</u>' \
                   '\n' \
                   '\nпо роли: ФИО/обязанности/замы' \
                   '\n' \
                   '\nпо имени: роль, дивизион, этап'
            bot.send_message(message.chat.id, mess, parse_mode='html', reply_markup = markup.search_markup)
            bot.register_next_step_handler(message, info_search)
        elif message.text == '⬅ назад':
            mess = 'Как я могу вам помочь?'
            bot.send_message(message.chat.id, mess, reply_markup = markup.start_markup)
            bot.register_next_step_handler(message, get_need)
        elif message.text == 'подобрать экспертов 💼':
            mess = 'Пожалуйста, выберите дивизион (заказчика)'
            bot.send_message(message.chat.id, mess, reply_markup = markup.division_markup)
            bot.register_next_step_handler(message, get_division_Excel)
        elif message.text == 'получить полную матрицу экспертов на почту 📩':
            mess = f'пожалуйста, введите свою почту\nили выберите её из списка'
            bot.send_message(message.chat.id, mess, reply_markup = markup.email_markup)
            bot.register_next_step_handler(message, send_full_matrix_mail)
    elif message.text == 'в главное меню 🏠':
        mess = 'Как я могу вам помочь?'
        bot.send_message(message.chat.id, mess, reply_markup = markup.start_markup)
        bot.register_next_step_handler(message, get_need)
    else:
        mess = f'такого функционала пока нет😞' \
                'пожалуйста, выберите из списка'
        bot.send_message(message.chat.id, mess, reply_markup = markup.start_markup)
        bot.register_next_step_handler(message, get_need)

def info_search(message):
    if message.text in comand_list:
        comand_list[message.text](message)
    elif message.text == 'поиск по роли':
        mess = 'Пожалуйста, выберите дивизион:'
        bot.send_message(message.chat.id, mess, reply_markup = markup.division_markup)
        bot.register_next_step_handler(message, get_division)
    elif message.text == 'поиск по имени':
        mess = 'Пожалуйста, выберите себя из списка'
        bot.send_message(message.chat.id, mess, reply_markup = markup.exp_list_markup)
        bot.register_next_step_handler(message, get_exp_name)
    elif message.text == '⬅ назад':
        mess = 'Как я могу вам помочь?'
        bot.send_message(message.chat.id, mess, reply_markup = markup.start_markup)
        bot.register_next_step_handler(message, get_need)


def get_division_Excel(message):
    if message.text in comand_list:
        comand_list[message.text](message)
    elif config.is_part_in_list(message.text, dic.divisions):
        dic.bot_dic[message.from_user.id]['Excel_дивизион'] = message.text
        mess = 'на каком этапе находится закупка?'
        bot.send_message(message.chat.id, mess, reply_markup = markup.step_markup_2)
        bot.register_next_step_handler(message, get_step_Excel)
    elif message.text == '⬅ назад':
        mess = 'Как я могу вам помочь?'
        bot.send_message(message.chat.id, mess, reply_markup = markup.start_markup)
        bot.register_next_step_handler(message, get_need)
    elif message.text == 'в главное меню 🏠':
        mess = 'Как я могу вам помочь?'
        bot.send_message(message.chat.id, mess, reply_markup = markup.start_markup)
        bot.register_next_step_handler(message, get_need)
    else:
        mess = f'такого дивизиона пока нет😞' \
                'пожалуйста, выберите из списка'
        bot.send_message(message.chat.id, mess, reply_markup = markup.division_markup)
        bot.register_next_step_handler(message, get_division_Excel)


def get_step_Excel(message):
    if message.text in comand_list:
        comand_list[message.text](message)
    elif config.is_part_in_list(message.text, dic.steps):
        dic.bot_dic[message.from_user.id]['Excel_этап'] = message.text
    
        db = sqlite3.connect('db/misha_bot.db', check_same_thread=False)
        c = db.cursor()
        c.execute("""SELECT * FROM exp_frame WHERE division = ? AND step = ?""", 
                 (dic.bot_dic[message.from_user.id]['Excel_дивизион'], dic.bot_dic[message.from_user.id]['Excel_этап']))
        df = c.fetchall()

        for i in df:
            c.execute("""INSERT INTO for_send (division, name, role, step, to_do) VALUES (?, ?, ?, ?, ?)""", i)

        db.commit()
        
        mess_1 = f'🧭 дивизион: {df[0][0]}' \
                  '\n' \
                 f'\n📅 этап: {df[0][3][3:]}' \
                  '\n'
        mess_2 = ''
        for i in range(len(df)):
            mess_2 += f'\n👤 {df[i][2]}\n({df[i][1]})'
        
        bot.send_message(message.chat.id, mess_1)
        bot.send_message(message.chat.id, mess_2, reply_markup = markup.back_markup)

        path_file = f"{message.from_user.id}/пользовательская матрица.xlsx"
        if not str(message.from_user.id) in os.listdir(): 
            os.mkdir(str(message.from_user.id))
     
        with pd.ExcelWriter(path_file) as writer:
            doc = pd.read_sql("""SELECT * FROM for_send""", db)
            doc.to_excel(writer, sheet_name = "матрица", header = dic.hdr, index = False)
            sn = writer.sheets['матрица']
            for i,j in {'A': 20, 'B': 40, 'C': 60, 'D': 40, 'E': 100}.items():
                sn.column_dimensions[i].width = j
            writer.save()
    
        # чистим пользовательскую таблицу в БД
        c.execute("""DELETE FROM for_send;""")
        db.commit()
        db.close()

        bot.register_next_step_handler(message, instead_Excel)

    elif message.text == 'в главное меню 🏠':
        mess = 'Как я могу вам помочь?'
        bot.send_message(message.chat.id, mess, reply_markup = markup.start_markup)
        bot.register_next_step_handler(message, get_need)

    elif message.text == '⬅ назад':
        mess = 'Пожалуйста, выберите дивизион (заказчика)'
        bot.send_message(message.chat.id, mess, reply_markup = markup.division_markup)
        bot.register_next_step_handler(message, get_division_Excel)
    
    else:
        mess = f'такого этапа пока нет😞' \
                'пожалуйста, выберите из списка'
        bot.send_message(message.chat.id, mess, reply_markup = markup.step_markup_2)
        bot.register_next_step_handler(message, get_step_Excel)

def instead_Excel(message):
    if message.text in comand_list:
        comand_list[message.text](message)
    elif message.text == '⬅ назад':
        mess = 'на каком этапе находится закупка?'
        bot.send_message(message.chat.id, mess, reply_markup = markup.step_markup_2)
        bot.register_next_step_handler(message, get_step_Excel)
    elif message.text == 'в главное меню 🏠':
        mess = 'Как я могу вам помочь?'
        bot.send_message(message.chat.id, mess, reply_markup = markup.start_markup)
        bot.register_next_step_handler(message, get_need)

# def send_user_matrix(message):
#     if message.text in comand_list:
#         comand_list[message.text](message)
#     elif message.text == 'получить матрицу на почту 📩':
#         # if message.text == 'отправить матрицу в чат':
#         #     # подключаем БД
#         #     db = sqlite3.connect('db/misha_bot.db', check_same_thread=False)
#         #     c = db.cursor()
#         #     # открываем Excel
#         #     doc = open(f"пользовательская матрица {message.from_user.id}.xlsx", "rb")
#         #     bot.send_document(message.chat.id, doc)
#         #     # чистим пользовательскую матрицу в БД
#         #     c.execute("""DELETE FROM for_send;""")
#         #     db.commit()
#         #     db.close()
#         #     mess = 'я могу чем-то еще вам помочь?'
#         #     bot.send_message(message.chat.id, mess, reply_markup = markup.start_markup)
#         #     bot.register_next_step_handler(message, get_need)
#         mess = 'пожалуйста, введите свою почту'
#         bot.send_message(message.chat.id, mess, reply_markup = markup.email_markup)
#         bot.register_next_step_handler(message, send_matrix_mail)

#     elif message.text == '⬅ назад':
#         db = sqlite3.connect('db/misha_bot.db', check_same_thread=False)
#         c = db.cursor()
#         # чистим пользовательскую матрицу в БД
#         c.execute("""DELETE FROM for_send;""")
#         db.commit()
#         db.close()
#         mess = 'на каком этапе находится закупка?'
#         bot.send_message(message.chat.id, mess, reply_markup = markup.step_markup_2)
#         bot.register_next_step_handler(message, get_step_Excel)

#     elif message.text == 'в главное меню 🏠':
#         mess = 'Как я могу вам помочь?'
#         bot.send_message(message.chat.id, mess, reply_markup = markup.start_markup)
#         bot.register_next_step_handler(message, get_need)
#     else:
#         mess = f'такого функционала пока нет😞' \
#                 'пожалуйста, выберите из списка'
#         bot.send_message(message.chat.id, mess, reply_markup = markup.sending_markup)
#         bot.register_next_step_handler(message, send_user_matrix)

# def send_matrix_mail(message):
#     if message.text in comand_list:
#         comand_list[message.text](message)
#     elif '@' in message.text:
#         if str(message.text)[-16:] == '@gazprom-neft.ru':
#             # получаем mail
#             dic.bot_dic[message.from_user.id]['mail'] = message.text

#             my_msg = MIMEMultipart()
#             my_msg['To'] = dic.bot_dic[message.from_user.id]['mail']
#             my_msg['From'] = config.FROM_EMAIL
#             my_msg['Subject'] = 'пользовательская матрица'
#             mess = ''
#             my_msg.attach(MIMEText(mess))
#             my_msg["Accept-Charset"]="utf-8"
#             att  =  MIMEApplication(open(f"{message.from_user.id}/пользовательская матрица.xlsx",'rb').read(),'utf-8')
#             att.add_header('Content-Disposition', 'attachment',
#                         filename = f"пользовательская матрица.xlsx")
#             my_msg.attach(att)

#             try:
#                 mailserver = smtplib.SMTP_SSL(config.Y_SERVER, config.Y_PORT)
#                 mailserver.ehlo()
#                 mailserver.login(config.Y_LOGIN, config.MY_PASSWORD)
#                 mailserver.sendmail(config.FROM_EMAIL, dic.bot_dic[message.from_user.id]['mail'], my_msg.as_string())
#                 mailserver.quit()
#                 mess = f"письмо отправлено на {dic.bot_dic[message.from_user.id]['mail']}"
#                 bot.send_message(message.chat.id, mess, reply_markup = markup.simple_back_markup)
#                 bot.register_next_step_handler(message, get_help_msg)
#             except:
#                 mess = "возникли какие-то проблемы😮" \
#                       f"\nпожалуйста, проверьте введенный адрес почты: {dic.bot_dic[message.from_user.id]['mail']}"
#                 bot.send_message(message.chat.id, mess, reply_markup = markup.remail_markup)
#                 bot.register_next_step_handler(message, add_matrix_mail)
#         else:
#             mess = "почта должна заканчиватся на '@gazprom-neft.ru'"
#             bot.send_message(message.chat.id, mess, reply_markup = markup.remail_markup)
#             bot.register_next_step_handler(message, add_matrix_mail)
#     else:
#         mess = "Я вас не понимаю... Пожалуйста, выберите из предложенных вариантов"
#         bot.send_message(message.chat.id, mess, reply_markup = markup.remail_markup)
#         bot.register_next_step_handler(message, add_matrix_mail)

# def add_matrix_mail(message):
#     if message.text in comand_list:
#         comand_list[message.text](message)
#     elif message.text == 'ввести еще раз':
#         mess = 'пожалуйста, введите свою почту'
#         bot.send_message(message.chat.id, mess, reply_markup = markup.markup_clear)
#         bot.register_next_step_handler(message, send_matrix_mail)
#     elif message.text == '⬅ назад':
#         mess = 'Как я могу вам помочь?'
#         bot.send_message(message.chat.id, mess, reply_markup = markup.start_markup)
#         bot.register_next_step_handler(message, get_need)
#     else:
#         mess = 'Я вас не понимаю... Пожалуйста, выберите из предложенных вариантов'
#         bot.send_message(message.chat.id, mess, reply_markup = markup.remail_markup)
#         bot.register_next_step_handler(message, add_matrix_mail)

def send_full_matrix_mail(message):
    if message.text in comand_list:
        comand_list[message.text](message)
    elif message.text == '⬅ назад':
        mess = 'Как я могу вам помочь?'
        bot.send_message(message.chat.id, mess, reply_markup = markup.start_markup)
        bot.register_next_step_handler(message, get_need)
    elif '@' in message.text:
        if str(message.text)[-16:] == '@gazprom-neft.ru':
            # получаем mail
            dic.bot_dic[message.from_user.id]['mail'] = message.text

            my_msg = MIMEMultipart()
            my_msg['To'] = dic.bot_dic[message.from_user.id]['mail']
            my_msg['From'] = config.FROM_EMAIL
            my_msg['Subject'] = 'матрица экспертов'
            mess = u'<a href="file:///H:\общая папка\13_ОТП\матрица экспертов">матрица экспертов</a> находится в общей папке'
            my_msg.attach(MIMEText(mess, 'html'))
            my_msg["Accept-Charset"]="utf-8"
            # att  =  MIMEApplication(open('матрица экспертов.xlsm','rb').read(),'utf-8')
            # att.add_header('Content-Disposition', 'attachment',
            #             filename = 'матрица экспертов.xlsm')
            # my_msg.attach(att)

            try:
                mailserver = smtplib.SMTP_SSL(config.Y_SERVER, config.Y_PORT)
                mailserver.ehlo()
                mailserver.login(config.Y_LOGIN, config.MY_PASSWORD)
                mailserver.sendmail(config.FROM_EMAIL, dic.bot_dic[message.from_user.id]['mail'], my_msg.as_string())
                mailserver.quit()
                mess = f"письмо отправлено на {dic.bot_dic[message.from_user.id]['mail']}" \
                       f"\nэто может занять несколько минут ⏱"
                bot.send_message(message.chat.id, mess, reply_markup = markup.simple_back_markup)
                bot.register_next_step_handler(message, send_full_matrix_mail)
            except:
                mess = f"возникли какие-то проблемы с отправкой на {dic.bot_dic[message.from_user.id]['mail']}" \
                      f"\nпожалуйста, введите другую почту или выберите её из списка"
                bot.send_message(message.chat.id, mess, reply_markup = markup.email_markup)
                bot.register_next_step_handler(message, send_full_matrix_mail)
        else:
            mess = "почта должна заканчиватся на @gazprom-neft.ru" \
                  f"\nпожалуйста, введите другую почту или выберите её из списка"
            bot.send_message(message.chat.id, mess, reply_markup = markup.email_markup)
            bot.register_next_step_handler(message, send_full_matrix_mail)
    else:
        mess = "Я вас не понимаю..." \
              f"\nпожалуйста, введите вашу почту или выберите её из списка"
        bot.send_message(message.chat.id, mess, reply_markup = markup.email_markup)
        bot.register_next_step_handler(message, send_full_matrix_mail)


def get_division(message):
    if message.text in comand_list:
        comand_list[message.text](message)
    elif config.is_part_in_list(message.text, dic.divisions):
        dic.bot_dic[message.from_user.id]['дивизион'] = message.text
        mess = 'Пожалуйста, выберите роль'
        bot.send_message(message.chat.id, mess, reply_markup = markup.role_list_markup)
        bot.register_next_step_handler(message, get_role)
    elif message.text == '⬅ назад':
        mess = '<u>выберите вариант поиска</u>' \
               '\n' \
               '\nпо роли: ФИО/обязанности/замы' \
               '\n' \
               '\nпо имени: роль, дивизион, этап'
        bot.send_message(message.chat.id, mess, parse_mode='html', reply_markup = markup.search_markup)
        bot.register_next_step_handler(message, info_search)
    elif message.text == 'в главное меню 🏠':
        mess = 'Как я могу вам помочь?'
        bot.send_message(message.chat.id, mess, reply_markup = markup.start_markup)
        bot.register_next_step_handler(message, get_need)
    else:
        mess = f'такого дивизиона пока нет😞' \
                'пожалуйста, выберите из списка'
        bot.send_message(message.chat.id, mess, reply_markup = markup.division_markup)
        bot.register_next_step_handler(message, get_division)


def get_role(message):
    if message.text in comand_list:
        comand_list[message.text](message)
    elif config.is_part_in_list(message.text, dic.role):
        dic.bot_dic[message.from_user.id]['роль'] = message.text
        mess = 'на каком этапе находится закупка?'

        db = sqlite3.connect('db/misha_bot.db', check_same_thread = False)
        c = db.cursor()
        c.execute("SELECT step FROM exp_by_steps WHERE role = ?", ((dic.bot_dic[message.from_user.id]['роль']),))
        step_list_s = c.fetchall()
        db.close()
        
        # создаем адаптивную клавиатуру
        step_markup = types.ReplyKeyboardMarkup(resize_keyboard = True, row_width = 2)
        btn1 = types.KeyboardButton('⬅ назад')
        btn2 = types.KeyboardButton('в главное меню 🏠')
        step_markup.add(btn1, btn2)
        for i in step_list_s:
            btn1 = types.KeyboardButton(str(i)[2:-3])
            step_markup.add(btn1)
        
        bot.send_message(message.chat.id, mess, reply_markup = step_markup)
        bot.register_next_step_handler(message, get_step)
    
    elif message.text == 'в главное меню 🏠':
        mess = 'Как я могу вам помочь?'
        bot.send_message(message.chat.id, mess, reply_markup = markup.start_markup)
        bot.register_next_step_handler(message, get_need)

    elif message.text == '⬅ назад':
        mess = 'Пожалуйста, выберите дивизион:'
        bot.send_message(message.chat.id, mess, reply_markup = markup.division_markup)
        bot.register_next_step_handler(message, get_division)
    else:
        mess = f'такой роли пока нет😞' \
                'пожалуйста, выберите из списка'
        bot.send_message(message.chat.id, mess, reply_markup = markup.role_list_markup)
        bot.register_next_step_handler(message, get_role)


def get_exp_name(message):
    if message.text in comand_list:
        comand_list[message.text](message)
    elif config.is_part_in_list(message.text, dic.nm_lst):
        dic.bot_dic[message.from_user.id]['имя'] = message.text

        db = sqlite3.connect('db/misha_bot.db', check_same_thread = False)
        c = db.cursor()

        c.execute(f"SELECT role FROM full_exp_frame WHERE name = ?", ((dic.bot_dic[message.from_user.id]['имя']),))
        your_role = set(c.fetchall())
        c.execute(f"SELECT division FROM full_exp_frame WHERE name = ?", ((dic.bot_dic[message.from_user.id]['имя']),))
        your_division = set(c.fetchall())
        c.execute(f"SELECT step FROM full_exp_frame WHERE name = ?", ((dic.bot_dic[message.from_user.id]['имя']),))
        your_steps = set(c.fetchall())

        db.close()

        mess_1 = '<b>👤 ваша роль:</b>'
        for i in your_role:
            x = str(i)[2:-3]
            mess_1 += f'\n- {x}'
        mess_2 = '<b>🧭 вы привлекаетесь в дивизионах:</b>'
        for i in your_division:
            x = str(i)[2:-3]
            mess_2 += f'\n- {x}'
        mess_3 = '<b>📅 на этапах:</b>'
        for i in your_steps:
            x = str(i)[2:-3]
            mess_3 += f'\n- {x[3:]}'

        bot.send_message(message.chat.id, mess_1, parse_mode='html')
        bot.send_message(message.chat.id, mess_2, parse_mode='html')
        bot.send_message(message.chat.id, mess_3, parse_mode='html', reply_markup = markup.what_to_do_markup)
        bot.register_next_step_handler(message, what_to_do_by_name)
    
    elif message.text == 'в главное меню 🏠':
        mess = 'Как я могу вам помочь?'
        bot.send_message(message.chat.id, mess, reply_markup = markup.start_markup)
        bot.register_next_step_handler(message, get_need)

    elif message.text == '⬅ назад':
        mess = '<u>выберите вариант поиска</u>' \
               '\n' \
               '\nпо роли: ФИО/обязанности/замы' \
               '\n' \
               '\nпо имени: роль, дивизион, этап'
        bot.send_message(message.chat.id, mess, parse_mode='html', reply_markup = markup.search_markup)
        bot.register_next_step_handler(message, info_search)
    else:
        mess = f'такого эксперта пока нет😞' \
                'пожалуйста, выберите из списка'
        bot.send_message(message.chat.id, mess, reply_markup = markup.exp_list_markup)
        bot.register_next_step_handler(message, get_exp_name)

def what_to_do_by_name(message):
    if message.text in comand_list:
        comand_list[message.text](message)
    elif message.text == '⬅ назад':
        mess = 'Пожалуйста, выберите себя из списка'
        bot.send_message(message.chat.id, mess, reply_markup = markup.exp_list_markup)
        bot.register_next_step_handler(message, get_exp_name)
    elif message.text == 'в главное меню 🏠':
        mess = 'Как я могу вам помочь?'
        bot.send_message(message.chat.id, mess, reply_markup = markup.start_markup)
        bot.register_next_step_handler(message, get_need)
    elif message.text == 'что дожен сделать эксперт?':
        db = sqlite3.connect('db/misha_bot.db', check_same_thread = False)
        c = db.cursor()
        
        c.execute(f"SELECT role FROM full_exp_frame WHERE name = ?", ((dic.bot_dic[message.from_user.id]['имя']),))
        your_role = set(c.fetchall())

        if len(your_role) != 1:
            role_markup = types.ReplyKeyboardMarkup(resize_keyboard = True, row_width = 2)
            btn1 = types.KeyboardButton('⬅ назад')
            btn2 = types.KeyboardButton('в главное меню 🏠')
            role_markup.add(btn1, btn2)
            for i in your_role:
                btn1 = types.KeyboardButton(str(i)[2:-3])
                role_markup.add(btn1)
            mess = 'пожалуйста, выберите роль'
            bot.send_message(message.chat.id, mess, reply_markup = role_markup)
            bot.register_next_step_handler(message, what_to_do_by_name_get_role)

        elif len(your_role) == 1:
            for i in your_role:
                dic.bot_dic[message.from_user.id]['роль'] = str(i)[2:-3]
                c.execute(f"SELECT step FROM full_exp_frame WHERE name = ? AND role = ?", (dic.bot_dic[message.from_user.id]['имя'], str(i)[2:-3]))
                your_steps = set(c.fetchall())
        
            step_markup = types.ReplyKeyboardMarkup(resize_keyboard = True, row_width = 2)
            btn1 = types.KeyboardButton('⬅ назад')
            btn2 = types.KeyboardButton('в главное меню 🏠')
            step_markup.add(btn1, btn2)
            for j in your_steps:
                btn1 = types.KeyboardButton(str(j)[2:-3])
                step_markup.add(btn1)
            mess = 'пожалуйста, выберите этап'
            bot.send_message(message.from_user.id, mess, reply_markup = step_markup)
            bot.register_next_step_handler(message, what_to_do_by_name_get_step)

        db.close()

    elif message.text == 'замещающие лица':
        db = sqlite3.connect('db/misha_bot.db', check_same_thread = False)
        c = db.cursor()
        if dic.bot_dic[message.from_user.id]['имя'] == 'Львова Е.С.':
            c.execute(f"SELECT division FROM full_exp_frame WHERE name = ?", ((dic.bot_dic[message.from_user.id]['имя']),))
            your_division = set(c.fetchall())
        
            mess = 'пожалуйста, выберите дивизион'
            div_markup = types.ReplyKeyboardMarkup(resize_keyboard = True, row_width = 2)
            btn1 = types.KeyboardButton('⬅ назад')
            btn2 = types.KeyboardButton('в главное меню 🏠')
            div_markup.add(btn1, btn2)
            for i in your_division:
                btn1 = types.KeyboardButton(str(i)[2:-3])
                div_markup.add(btn1)
            bot.send_message(message.chat.id, mess, reply_markup = div_markup)
            bot.register_next_step_handler(message, what_to_do_by_name_get_div)
        else:
            c.execute("SELECT zam FROM alternate WHERE name = ?",
                     ((dic.bot_dic[message.from_user.id]['имя']),))
            zam_lst = set(c.fetchall())
            mess = ''
            for i in zam_lst:
                mess = mess + f'👤 {str(i)[2:-3]}\n'
            bot.send_message(message.chat.id, mess, reply_markup = markup.back_markup)
            bot.register_next_step_handler(message, what_to_do_by_name_repeat)

        db.close()



    else:
        mess = 'Я вас не понимаю... Пожалуйста, выберите из предложенных вариантов'
        bot.send_message(message.chat.id, mess, parse_mode='html', reply_markup = markup.back_markup)
        bot.register_next_step_handler(message, what_to_do_by_name)

def what_to_do_by_name_get_role(message):
    if message.text in comand_list:
        comand_list[message.text](message)
    elif message.text == 'в главное меню 🏠':
        mess = 'Как я могу вам помочь?'
        bot.send_message(message.chat.id, mess, reply_markup = markup.start_markup)
        bot.register_next_step_handler(message, get_need)
    elif message.text == '⬅ назад':
        db = sqlite3.connect('db/misha_bot.db', check_same_thread = False)
        c = db.cursor()

        c.execute(f"SELECT role FROM full_exp_frame WHERE name = ?", ((dic.bot_dic[message.from_user.id]['имя']),))
        your_role = set(c.fetchall())
        c.execute(f"SELECT division FROM full_exp_frame WHERE name = ?", ((dic.bot_dic[message.from_user.id]['имя']),))
        your_division = set(c.fetchall())
        c.execute(f"SELECT step FROM full_exp_frame WHERE name = ?", ((dic.bot_dic[message.from_user.id]['имя']),))
        your_steps = set(c.fetchall())

        db.close()

        mess_1 = '<b>👤 ваша роль:</b>'
        for i in your_role:
            x = str(i)[2:-3]
            mess_1 += f'\n- {x}'
        mess_2 = '<b>🧭 вы привлекаетесь в дивизионах:</b>'
        for i in your_division:
            x = str(i)[2:-3]
            mess_2 += f'\n- {x}'
        mess_3 = '<b>📅 на этапах:</b>'
        for i in your_steps:
            x = str(i)[2:-3]
            mess_3 += f'\n- {x[3:]}'

        bot.send_message(message.chat.id, mess_1, parse_mode='html')
        bot.send_message(message.chat.id, mess_2, parse_mode='html')
        bot.send_message(message.chat.id, mess_3, parse_mode='html', reply_markup = markup.what_to_do_markup)
        bot.register_next_step_handler(message, what_to_do_by_name)
    elif config.is_part_in_list(message.text, dic.role):
        dic.bot_dic[message.from_user.id]['роль'] = message.text
        db = sqlite3.connect('db/misha_bot.db', check_same_thread = False)
        c = db.cursor()
        c.execute(f"SELECT step FROM full_exp_frame WHERE name = ? AND role = ?",
                 (dic.bot_dic[message.from_user.id]['имя'],
                  dic.bot_dic[message.from_user.id]['роль']))
        your_steps = set(c.fetchall())
        
        step_markup = types.ReplyKeyboardMarkup(resize_keyboard = True, row_width = 2)
        btn1 = types.KeyboardButton('⬅ назад')
        btn2 = types.KeyboardButton('в главное меню 🏠')
        step_markup.add(btn1, btn2)
        for j in your_steps:
            btn1 = types.KeyboardButton(str(j)[2:-3])
            step_markup.add(btn1)
        mess = 'пожалуйста, выберите этап'
        bot.send_message(message.chat.id, mess, reply_markup = step_markup)
        bot.register_next_step_handler(message, what_to_do_by_name_get_step)

        db.close()

def what_to_do_by_name_get_step(message):
    if message.text in comand_list:
        comand_list[message.text](message)
    elif message.text == 'в главное меню 🏠':
        mess = 'Как я могу вам помочь?'
        bot.send_message(message.chat.id, mess, reply_markup = markup.start_markup)
        bot.register_next_step_handler(message, get_need)
    elif message.text == '⬅ назад':
        db = sqlite3.connect('db/misha_bot.db', check_same_thread = False)
        c = db.cursor()

        c.execute(f"SELECT role FROM full_exp_frame WHERE name = ?", ((dic.bot_dic[message.from_user.id]['имя']),))
        your_role = set(c.fetchall())
        c.execute(f"SELECT division FROM full_exp_frame WHERE name = ?", ((dic.bot_dic[message.from_user.id]['имя']),))
        your_division = set(c.fetchall())
        c.execute(f"SELECT step FROM full_exp_frame WHERE name = ?", ((dic.bot_dic[message.from_user.id]['имя']),))
        your_steps = set(c.fetchall())

        db.close()

        mess_1 = '<b>👤 ваша роль:</b>'
        for i in your_role:
            x = str(i)[2:-3]
            mess_1 += f'\n- {x}'
        mess_2 = '<b>🧭 вы привлекаетесь в дивизионах:</b>'
        for i in your_division:
            x = str(i)[2:-3]
            mess_2 += f'\n- {x}'
        mess_3 = '<b>📅 на этапах:</b>'
        for i in your_steps:
            x = str(i)[2:-3]
            mess_3 += f'\n- {x[3:]}'

        bot.send_message(message.chat.id, mess_1, parse_mode='html')
        bot.send_message(message.chat.id, mess_2, parse_mode='html')
        bot.send_message(message.chat.id, mess_3, parse_mode='html', reply_markup = markup.what_to_do_markup)
        bot.register_next_step_handler(message, what_to_do_by_name)
    elif config.is_part_in_list(message.text, dic.steps):
        dic.bot_dic[message.from_user.id]['этап'] = message.text

        db = sqlite3.connect('db/misha_bot.db', check_same_thread = False)
        c = db.cursor()

        c.execute("SELECT to_do FROM exp_frame WHERE role = ? AND step = ?",
                 (dic.bot_dic[message.from_user.id]['роль'],
                  dic.bot_dic[message.from_user.id]['этап']))
        mess = c.fetchall()
        bot.send_message(message.chat.id, mess, reply_markup = markup.back_markup)

        bot.register_next_step_handler(message, what_to_do_by_name_repeat)


def what_to_do_by_name_get_div(message):
    if message.text in comand_list:
        comand_list[message.text](message)
    elif message.text == 'в главное меню 🏠':
        mess = 'Как я могу вам помочь?'
        bot.send_message(message.chat.id, mess, reply_markup = markup.start_markup)
        bot.register_next_step_handler(message, get_need)
    elif message.text == '⬅ назад':
        db = sqlite3.connect('db/misha_bot.db', check_same_thread = False)
        c = db.cursor()

        c.execute(f"SELECT role FROM full_exp_frame WHERE name = ?", ((dic.bot_dic[message.from_user.id]['имя']),))
        your_role = set(c.fetchall())
        c.execute(f"SELECT division FROM full_exp_frame WHERE name = ?", ((dic.bot_dic[message.from_user.id]['имя']),))
        your_division = set(c.fetchall())
        c.execute(f"SELECT step FROM full_exp_frame WHERE name = ?", ((dic.bot_dic[message.from_user.id]['имя']),))
        your_steps = set(c.fetchall())

        db.close()

        mess_1 = '<b>👤 ваша роль:</b>'
        for i in your_role:
            x = str(i)[2:-3]
            mess_1 += f'\n- {x}'
        mess_2 = '<b>🧭 вы привлекаетесь в дивизионах:</b>'
        for i in your_division:
            x = str(i)[2:-3]
            mess_2 += f'\n- {x}'
        mess_3 = '<b>📅 на этапах:</b>'
        for i in your_steps:
            x = str(i)[2:-3]
            mess_3 += f'\n- {x[3:]}'

        bot.send_message(message.chat.id, mess_1, parse_mode='html')
        bot.send_message(message.chat.id, mess_2, parse_mode='html')
        bot.send_message(message.chat.id, mess_3, parse_mode='html', reply_markup = markup.what_to_do_markup)
        bot.register_next_step_handler(message, what_to_do_by_name)
    elif config.is_part_in_list(message.text, dic.divisions):
        dic.bot_dic[message.from_user.id]['дивизион'] = message.text
        db = sqlite3.connect('db/misha_bot.db', check_same_thread = False)
        c = db.cursor()
        c.execute("SELECT zam FROM alternate WHERE name = ? AND division = ?",
                 (dic.bot_dic[message.from_user.id]['имя'],
                  dic.bot_dic[message.from_user.id]['дивизион']))
        zam_lst = c.fetchall()
        mess = ''
        for i in zam_lst:
            mess = mess + f'👤 {str(i)[2:-3]}\n'
        bot.send_message(message.chat.id, mess, reply_markup = markup.back_markup)
        bot.register_next_step_handler(message, what_to_do_by_name_repeat)

        db.close()


def what_to_do_by_name_repeat(message):
    if message.text in comand_list:
        comand_list[message.text](message)
    elif message.text == '⬅ назад':
        db = sqlite3.connect('db/misha_bot.db', check_same_thread = False)
        c = db.cursor()

        c.execute(f"SELECT role FROM full_exp_frame WHERE name = ?", ((dic.bot_dic[message.from_user.id]['имя']),))
        your_role = set(c.fetchall())
        c.execute(f"SELECT division FROM full_exp_frame WHERE name = ?", ((dic.bot_dic[message.from_user.id]['имя']),))
        your_division = set(c.fetchall())
        c.execute(f"SELECT step FROM full_exp_frame WHERE name = ?", ((dic.bot_dic[message.from_user.id]['имя']),))
        your_steps = set(c.fetchall())

        db.close()

        mess_1 = '<b>👤 ваша роль:</b>'
        for i in your_role:
            x = str(i)[2:-3]
            mess_1 += f'\n- {x}'
        mess_2 = '<b>🧭 вы привлекаетесь в дивизионах:</b>'
        for i in your_division:
            x = str(i)[2:-3]
            mess_2 += f'\n- {x}'
        mess_3 = '<b>📅 на этапах:</b>'
        for i in your_steps:
            x = str(i)[2:-3]
            mess_3 += f'\n- {x[3:]}'

        bot.send_message(message.chat.id, mess_1, parse_mode='html')
        bot.send_message(message.chat.id, mess_2, parse_mode='html')
        bot.send_message(message.chat.id, mess_3, parse_mode='html', reply_markup = markup.what_to_do_markup)
        bot.register_next_step_handler(message, what_to_do_by_name)
    elif message.text == 'в главное меню 🏠':
        mess = 'Как я могу вам помочь?'
        bot.send_message(message.chat.id, mess, reply_markup = markup.start_markup)
        bot.register_next_step_handler(message, get_need)
    else:
        mess = f'такого функционала пока нет😞' \
                'пожалуйста, выберите из списка'
        bot.send_message(message.chat.id, mess, reply_markup = markup.back_markup)
        bot.register_next_step_handler(message, what_to_do_repeat)


def get_step(message):
    if message.text in comand_list:
        comand_list[message.text](message)
    elif config.is_part_in_list(message.text, dic.steps):
        dic.bot_dic[message.from_user.id]['этап'] = message.text

        db = sqlite3.connect('db/misha_bot.db', check_same_thread = False)
        c = db.cursor()
        c.execute("SELECT name FROM exp_frame WHERE division = ? AND role = ? AND step = ?",
                  (dic.bot_dic[message.from_user.id]['дивизион'], dic.bot_dic[message.from_user.id]['роль'], dic.bot_dic[message.from_user.id]['этап']))
        mess = f"👤 {str(c.fetchall())[3:-4]}"
        db.close()
        bot.send_message(message.chat.id, mess, reply_markup = markup.what_to_do_markup)
        bot.register_next_step_handler(message, what_to_do)
    
    elif message.text == 'в главное меню 🏠':
        mess = 'Как я могу вам помочь?'
        bot.send_message(message.chat.id, mess, reply_markup = markup.start_markup)
        bot.register_next_step_handler(message, get_need)

    elif message.text == '⬅ назад':
        mess = 'Пожалуйста, выберте роль'
        bot.send_message(message.chat.id, mess, reply_markup = markup.role_list_markup)
        bot.register_next_step_handler(message, get_role)
    else:
        mess = f'такого этапа пока нет😞' \
                'пожалуйста, выберите из списка'
        bot.send_message(message.chat.id, mess, reply_markup = markup.step_markup_2)
        bot.register_next_step_handler(message, get_step)

def what_to_do(message):
    if message.text in comand_list:
        comand_list[message.text](message)
    elif message.text == '⬅ назад':
        mess = 'на каком этапе находится закупка?'

        db = sqlite3.connect('db/misha_bot.db', check_same_thread = False)
        c = db.cursor()
        c.execute("SELECT step FROM exp_by_steps WHERE role = ?", ((dic.bot_dic[message.from_user.id]['роль']),))
        step_list_s = c.fetchall()
        db.close()
        
        # создаем адаптивную клавиатуру
        step_markup = types.ReplyKeyboardMarkup(resize_keyboard = True, row_width = 2)
        chars = "(,')"
        for i in step_list_s:
            btn1 = types.KeyboardButton(str(i).translate(str.maketrans('', '', chars)))
            step_markup.add(btn1)
        btn1 = types.KeyboardButton('⬅ назад')
        step_markup.add(btn1)

        bot.send_message(message.chat.id, mess, reply_markup = step_markup)
        bot.register_next_step_handler(message, get_step)

    elif message.text == 'что дожен сделать эксперт?':
        db = sqlite3.connect('db/misha_bot.db', check_same_thread = False)
        c = db.cursor()
        c.execute("SELECT to_do FROM exp_frame WHERE division = ? AND role = ? AND step = ?",
                  (dic.bot_dic[message.from_user.id]['дивизион'], dic.bot_dic[message.from_user.id]['роль'], dic.bot_dic[message.from_user.id]['этап']))
        mess = c.fetchall()
        db.close()
        bot.send_message(message.chat.id, mess, reply_markup = markup.back_markup)
        bot.register_next_step_handler(message, what_to_do_repeat)

    elif message.text == 'замещающие лица':
        db = sqlite3.connect('db/misha_bot.db', check_same_thread = False)
        c = db.cursor()

        c.execute("SELECT name FROM exp_frame WHERE division = ? AND role = ? AND step = ?",
                 (dic.bot_dic[message.from_user.id]['дивизион'], dic.bot_dic[message.from_user.id]['роль'], dic.bot_dic[message.from_user.id]['этап']))
        name = str(c.fetchall())[3:-4]

        c.execute("SELECT zam FROM alternate WHERE name = ? AND division = ?",
                 (name, dic.bot_dic[message.from_user.id]['дивизион']))
        zam_lst = c.fetchall()
        db.close()
        mess = ''
        for i in zam_lst:
            mess += f'\n👤 {str(i)[2:-3]}'

        bot.send_message(message.chat.id, mess, reply_markup = markup.back_markup)
        bot.register_next_step_handler(message, what_to_do_repeat)

    elif message.text == 'в главное меню 🏠':
        mess = 'Как я могу вам помочь?'
        bot.send_message(message.chat.id, mess, reply_markup = markup.start_markup)
        bot.register_next_step_handler(message, get_need)
    else:
        mess = f'такого функционала пока нет😞' \
                'пожалуйста, выберите из списка'
        bot.send_message(message.chat.id, mess, reply_markup = markup.what_to_do_markup)
        bot.register_next_step_handler(message, what_to_do)

def what_to_do_repeat(message):
    if message.text in comand_list:
        comand_list[message.text](message)
    elif message.text == '⬅ назад':
        db = sqlite3.connect('db/misha_bot.db', check_same_thread = False)
        c = db.cursor()
        c.execute("SELECT name FROM exp_frame WHERE division = ? AND role = ? AND step = ?",
                  (dic.bot_dic[message.from_user.id]['дивизион'], dic.bot_dic[message.from_user.id]['роль'], dic.bot_dic[message.from_user.id]['этап']))
        mess = c.fetchall()
        db.close()
        bot.send_message(message.chat.id, mess, reply_markup = markup.what_to_do_markup)
        bot.register_next_step_handler(message, what_to_do)
    elif message.text == 'в главное меню 🏠':
        mess = 'Как я могу вам помочь?'
        bot.send_message(message.chat.id, mess, reply_markup = markup.start_markup)
        bot.register_next_step_handler(message, get_need)
    else:
        mess = f'такого функционала пока нет😞' \
                'пожалуйста, выберите из списка'
        bot.send_message(message.chat.id, mess, reply_markup = markup.back_markup)
        bot.register_next_step_handler(message, what_to_do_repeat)


bot.polling(non_stop = True, interval = 0)