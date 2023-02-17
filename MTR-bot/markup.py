from telebot import types
import config, dic

# сброс кнопок
markup_clear = types.ReplyKeyboardRemove()

# выбор номера инспекции
insp_num = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
btn1 = types.KeyboardButton('1')
insp_num.add(btn1)

# выбор склада
sklad = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
btn1 = types.KeyboardButton('открытый холодный')
btn2 = types.KeyboardButton('открытый теплый')
btn3 = types.KeyboardButton('открытый закрытый')
btn4 = types.KeyboardButton('⬅ назад')
btn5 = types.KeyboardButton('далее ➡️')
sklad.add(btn1)
sklad.add(btn2)
sklad.add(btn3)
sklad.add(btn4, btn5)

# к выбору инспекции
bck_to_insp_num = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
btn1 = types.KeyboardButton('⬅ назад к выбору инспекции')
bck_to_insp_num.add(btn1)

# назад
bck = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
btn1 = types.KeyboardButton('⬅ назад')
bck.add(btn1)

# вперед, назад
twix = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
btn1 = types.KeyboardButton('⬅ назад')
btn2 = types.KeyboardButton('далее ➡️')
twix.add(btn1, btn2)

# вперед, назад
photo_add = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
btn0 = types.KeyboardButton('добавить фото')
photo_add.add(btn0)
btn1 = types.KeyboardButton('⬅ назад')
btn2 = types.KeyboardButton('далее ➡️')
photo_add.add(btn1, btn2)