from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup
from data.phrases import phrases
from random import choice

from data import texts
from utils.get_time_ending import getTimeEndingMinute


async def send_daily_task_reminder(user_id: int, bot: Bot, name: str, hour: int, minute: int, about: str, completed: str): #keyboard: InlineKeyboardMarkup
    if len(str(minute)) < 2:
        minute = f"0{minute}"

    phrase = choice(phrases["daily_task_remind"])

    await bot.send_message(user_id, texts.daily_task_notice_text.format(phrase=phrase, hour=hour, minute=minute, name=name))

async def send_daily_task_hour_before_reminder(user_id: int, bot: Bot, name: str, hour: int, minute: int, about: str, completed: str): #keyboard: InlineKeyboardMarkup
    if len(str(minute)) < 2:
        minute = f"0{minute}"

    phrase = choice(phrases["daily_task_remind_before_hour"])

    await bot.send_message(user_id, texts.daily_task_notice_before_hour_text.format(phrase=phrase, hour=hour, minute=minute, name=name))