from aiogram import Router, F
from aiogram.filters import Command 
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove
from datetime import datetime

from data import texts, keyboards
from db_manager import Manager

router = Router()
manager = Manager()

@router.message(F.text == "Ежедневные задания 📑")
async def daily_tasks_button(message: Message):
    if manager.user_exists(message.from_user.id):
        await message.answer("📑 Ваши ежедневные задания:", parse_mode="html", reply_markup=keyboards.daily_tasks)
    else:
        await message.answer(texts.unregistered_acces_error, reply_markup=ReplyKeyboardRemove(), parse_mode="html")