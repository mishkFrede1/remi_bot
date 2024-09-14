from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="О Remi ℹ️"), KeyboardButton(text="Ежедневные задания 📑")],
        [KeyboardButton(text="Друзья 👥"), KeyboardButton(text="Особые задания 📍")],
    ], resize_keyboard=True
)