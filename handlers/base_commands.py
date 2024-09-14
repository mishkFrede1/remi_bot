from aiogram import Router, F, Bot
from aiogram.filters import Command 
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from datetime import datetime

from data import texts, keyboards
from db_manager import Manager

router = Router()
manager = Manager()

# @router.message(Command("help"))
# async def start(message: Message):
#     await message.answer(texts.help_text, parse_mode="html")

# @router.message(Command("menu"))
# async def main_menu_command(message: Message):
#     if manager.user_exists(message.from_user.id):
#         await message.answer("⚙️ Главное меню:", reply_markup=keyboards.main_menu)
#     else:
#         await message.answer(texts.unregistered_access_text, parse_mode="html", reply_markup=ReplyKeyboardRemove())

@router.message(Command("start"))
async def start(message: Message):
    if manager.user_exists(message.from_user.id):
        await message.answer(texts.welcome_text.format(username=message.from_user.first_name), parse_mode="html", reply_markup=keyboards.main_menu)
    else:
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Создать аккаунт", callback_data="reg")]
            ], resize_keyboard=True, one_time_keyboard=True 
        )
        await message.answer(texts.registration_text, reply_markup=keyboard, parse_mode="html")

@router.callback_query(F.data == "reg")
async def reg(callback_query: CallbackQuery, bot: Bot):
    if manager.user_exists(callback_query.from_user.id):
        await bot.send_message(callback_query.from_user.id, texts.acc_exist_error, parse_mode="html", reply_markup=keyboards.main_menu)
    else:
        now = datetime.now()
        date_strftime = now.strftime("%d.%m.%Y")    
        manager.upload_registration_data(callback_query.from_user.id, date_strftime, callback_query.from_user.first_name)
        
        await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)
        await bot.send_message(callback_query.from_user.id, "✔️ <b>Аккаунт успешно создан!</b> Я всегда рада новым пользователям 🤍", parse_mode="html", reply_markup=keyboards.main_menu)

