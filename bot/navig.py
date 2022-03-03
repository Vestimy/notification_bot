from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

btnRegistration = KeyboardButton('Регистрация')
regMenu = ReplyKeyboardMarkup(resize_keyboard=True)
regMenu.add(btnRegistration)

# btnProfile = KeyboardButton('Профиль')
btnSub = KeyboardButton('Подписка')

mainMenu = ReplyKeyboardMarkup(resize_keyboard=True)
mainMenu.add(btnSub)

btnYes = KeyboardButton('Да')
btnNo = KeyboardButton('Нет')

editMenu = ReplyKeyboardMarkup(resize_keyboard=True)
editMenu.add(btnYes, btnNo)
