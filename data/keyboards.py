from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="О Remi ℹ️"), KeyboardButton(text="Ежедневные задания 📑")],
        [KeyboardButton(text="Друзья 👥"), KeyboardButton(text="Особые задания 📍")],
    ], resize_keyboard=True
)

daily_tasks = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Задания 📋"), KeyboardButton(text="Настройки 🛠")],
        [KeyboardButton(text="Назад ⬅️")]
    ], resize_keyboard=True
)