import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
import config
import sqlite3
import os
import pandas as pd

from email.mime.multipart import MIMEMultipart
# from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import smtplib


bot = telebot.TeleBot(config.BOT_TOKEN, skip_pending = True)


@bot.message_handler(commands = ["start"])
def start(message):
    mess = 'Привет' \
          f'\nвыбери email 📩'
    email_markup = ReplyKeyboardMarkup(resize_keyboard = True, row_width = 2)
    btn1 = KeyboardButton('test@icloud.com')
    btn2 = KeyboardButton('test@mail.ru')
    btn3 = KeyboardButton('test@gazprom-neft.ru')
    email_markup.add(btn1, btn2, btn3)
    bot.send_message(message.from_user.id, mess, reply_markup = email_markup)
    bot.register_next_step_handler(message, email_send)


def email_send(message):
    email = message.text

    # ВЫБИРАЕМ ДАННЫЕ ИЗ SQLite
    db = sqlite3.connect('db/misha_bot.db', check_same_thread=False)
    c = db.cursor()
    c.execute("""SELECT * FROM exp_frame WHERE division = ? AND step = ?""", 
                 ('Восток', '7. Итоговая тех. оценка'))
    df = c.fetchall()

    mess_1 = f'🧭 дивизион: {df[0][0]}' \
              '\n' \
             f'\n📅 этап: {df[0][3][3:]}' \
              '\n'
    mess_2 = ''
    for i in range(len(df)):
        mess_2 += f'\n👤 {df[i][2]}\n({df[i][1]})'
    
    bot.send_message(message.chat.id, mess_1)
    bot.send_message(message.chat.id, mess_2)
    
    # записываем в новую таблицу в БД (без неё все ломается)
    for i in df:
        c.execute("""INSERT INTO for_send (division, name, role, step, to_do) VALUES (?, ?, ?, ?, ?)""", i)
    
    # обязательно сохраняем изменения в БД
    db.commit()
    
    # создаем пользовательскую директорю для хранения Excel, если не существует
    if not str(message.from_user.id) in os.listdir():
        os.mkdir(str(message.from_user.id))
    

    # СОЗДАЕМ Ecxel
    with pd.ExcelWriter(f"{message.from_user.id}/пользовательская матрица.xlsx") as writer:
        doc = pd.read_sql("""SELECT * FROM for_send""", db)
        doc.to_excel(writer, sheet_name = "матрица", header = ['дивизион', 'имя', 'роль', 'этап', 'что нужно сделать'], index = False)
        sn = writer.sheets['матрица']
        for i,j in {'A': 20, 'B': 40, 'C': 60, 'D': 40, 'E': 100}.items():
            sn.column_dimensions[i].width = j

    # чистим пользовательскую матрицу в БД
    c.execute("""DELETE FROM for_send;""")

    db.commit()
    db.close()


    # ОТПРАВЛЯЕМ Excel
    my_msg = MIMEMultipart()
    my_msg['To'] = email
    my_msg['From'] = config.FROM_EMAIL
    my_msg['Subject'] = 'пользовательская матрица'
    # mess = ''
    # my_msg.attach(MIMEText(mess))
    my_msg["Accept-Charset"]="utf-8"
    att  =  MIMEApplication(open(f"{message.from_user.id}/пользовательская матрица.xlsx",'rb').read(),'utf-8')
    att.add_header('Content-Disposition', 'attachment',
                    filename = f"пользовательская матрица.xlsx")
    # att = openpyxl.load_workbook(path_file)
    my_msg.attach(att)

    try:
        mailserver = smtplib.SMTP_SSL(config.Y_SERVER, config.Y_PORT)
        mailserver.ehlo()
        mailserver.login(config.Y_LOGIN, config.MY_PASSWORD)
        mailserver.sendmail(config.FROM_EMAIL, email, my_msg.as_string())
        mailserver.quit()
        mess = f"письмо отправлено на {email}"
        bot.send_message(message.chat.id, mess)
    except:
        mess = "возникли какие-то проблемы😮" \
              f"\nпожалуйста, проверьте введенный адрес почты: {email}"
        bot.send_message(message.chat.id, mess)


bot.polling(non_stop = True, interval = 0)
