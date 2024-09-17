from aiogram import Router, F, Bot
from aiogram.filters import Command 
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, ReplyKeyboardRemove
from datetime import datetime

from data import texts, keyboards
from db_manager import Manager
from data.phrases import phrases
from random import choice

router = Router()
manager = Manager()

@router.message(Command("start"))
async def start(message: Message):
    if not manager.user_exists(message.from_user.id):
        now = datetime.now()
        date_strftime = now.strftime("%d.%m.%Y")
        manager.upload_registration_data(message.from_user.id, date_strftime, message.from_user.first_name)
        
    await message.answer(texts.start_text, reply_markup=keyboards.main_menu, parse_mode="html")

@router.message(F.text == "Назад ⬅️")
async def back_button(message: Message):
    await message.answer(choice(phrases["menu"]), parse_mode="html", reply_markup=keyboards.main_menu)