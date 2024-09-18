from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup

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

delete_daily_task = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Да ✔️", callback_data="yes_delete_daily_task"), InlineKeyboardButton(text="Нет ❌", callback_data="no_delete_daily_task")]
    ]
)
