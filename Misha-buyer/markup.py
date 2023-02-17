from telebot import types
import config, dic, sqlite3

# сброс кнопок
markup_clear = types.ReplyKeyboardRemove()

# выбор роли
start_markup = types.ReplyKeyboardMarkup(resize_keyboard = True, row_width = 2)
btn1 = types.KeyboardButton('искать информацию 🔍')
btn2 = types.KeyboardButton('подобрать экспертов 💼')
start_markup.add(btn1, btn2)
btn1 = types.KeyboardButton('получить полную матрицу экспертов на почту 📩')
start_markup.add(btn1)

search_markup = types.ReplyKeyboardMarkup(resize_keyboard = True, row_width = 2)
btn1 = types.KeyboardButton('поиск по роли')
btn2 = types.KeyboardButton('поиск по имени')
btn3 = types.KeyboardButton('⬅ назад')
search_markup.add(btn1, btn2)
search_markup.add(btn3)


# выбор дивизиона
division_markup = types.ReplyKeyboardMarkup(resize_keyboard = True, row_width = 2)
btn1 = types.KeyboardButton('Восток')
btn2 = types.KeyboardButton('Восточная Сибирь')
btn3 = types.KeyboardButton('Запад')
btn4 = types.KeyboardButton('Север')
btn5 = types.KeyboardButton('Центр')
btn6 = types.KeyboardButton('Юг')
btn7 = types.KeyboardButton('ГО')
btn8 = types.KeyboardButton('⬅ назад')
btn9 = types.KeyboardButton('в главное меню 🏠')
division_markup.add(btn8, btn9)
division_markup.add(btn1, btn2, btn3, btn4, btn5, btn6, btn7)

# список экспертов
exp_list_markup = types.ReplyKeyboardMarkup(resize_keyboard = True, row_width = 3)
btn1 = types.KeyboardButton('⬅ назад')
btn2 = types.KeyboardButton('в главное меню 🏠')
exp_list_markup.add(btn1, btn2)
lgh = len(dic.nm_lst) - 2
for i in range(0, lgh, 3):
    btn1 = types.KeyboardButton(dic.nm_lst[i])
    btn2 = types.KeyboardButton(dic.nm_lst[i+1])
    btn3 = types.KeyboardButton(dic.nm_lst[i+2])
    exp_list_markup.add(btn1, btn2, btn3)
btn1 = types.KeyboardButton('Руководитель подразделения, в чьих интересах необходимо провести закупку')
btn2 = types.KeyboardButton('назначенный сотрудник ЦЗУиР или дивизиона')
exp_list_markup.add(btn1)
exp_list_markup.add(btn2)

# кнопка назад
back_markup = types.ReplyKeyboardMarkup(resize_keyboard = True, row_width = 2)
btn1 = types.KeyboardButton('⬅ назад')
btn2 = types.KeyboardButton('в главное меню 🏠')
back_markup.add(btn1, btn2)

simple_back_markup = types.ReplyKeyboardMarkup(resize_keyboard = True, row_width = 2)
btn1 = types.KeyboardButton('⬅ назад')
simple_back_markup.add(btn1)

# повторный ввод почты
remail_markup = types.ReplyKeyboardMarkup(resize_keyboard = True, row_width = 2)
btn1 = types.KeyboardButton('ввести еще раз')
btn2 = types.KeyboardButton('⬅ назад')
remail_markup.add(btn1, btn2)

# список ролей
role_list_markup = types.ReplyKeyboardMarkup(resize_keyboard = True, row_width = 2)
btn1 = types.KeyboardButton('⬅ назад')
btn2 = types.KeyboardButton('в главное меню 🏠')
role_list_markup.add(btn1, btn2)
for i in dic.role:
    btn1 = types.KeyboardButton(i)
    role_list_markup.add(btn1)

what_to_do_markup = types.ReplyKeyboardMarkup(resize_keyboard = True, row_width = 2)
btn1 = types.KeyboardButton('что дожен сделать эксперт?')
btn2 = types.KeyboardButton('замещающие лица')
btn3 = types.KeyboardButton('⬅ назад')
btn4 = types.KeyboardButton('в главное меню 🏠')
what_to_do_markup.add(btn1, btn2, btn3, btn4)


step_markup_2 = types.ReplyKeyboardMarkup(resize_keyboard = True, row_width = 2)
btn1 = types.KeyboardButton('⬅ назад')
btn2 = types.KeyboardButton('в главное меню 🏠')
step_markup_2.add(btn1, btn2)
for i in dic.steps:
    btn1 = types.KeyboardButton(i)
    step_markup_2.add(btn1)
    

sending_markup = types.ReplyKeyboardMarkup(resize_keyboard = True, row_width = 1)
btn1 = types.KeyboardButton('получить матрицу на почту 📩')
btn2 = types.KeyboardButton('⬅ назад')
sending_markup.add(btn1, btn2)

email_markup = types.ReplyKeyboardMarkup(resize_keyboard = True, row_width = 2)
btn1 = types.KeyboardButton('⬅ назад')
email_markup.add(btn1)
for i in dic.mail_lst:
    btn1 = types.KeyboardButton(i)
    email_markup.add(btn1)

pswd_markup = types.ReplyKeyboardMarkup(resize_keyboard = True, row_width = 1)
btn1 = types.KeyboardButton('я не знаю пароль 😟')
pswd_markup.add(btn1)