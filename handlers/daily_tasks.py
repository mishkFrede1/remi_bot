from aiogram import Router, F, Bot
from aiogram.filters import Command 
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from datetime import datetime, time

from data import keyboards
from db_manager import Manager
from utils.is_number import isNumber
from data.phrases import phrases
from random import choice

router = Router()
manager = Manager()

class new_dtask(StatesGroup):
    name = State()
    about = State()
    time = State()

def get_daily_tasks_keyboard(tasks: list):
    inline_keyboard = []
    if len(tasks) > 0:
        for i in tasks:
            minutes = i[3].minute
            if len(str(minutes)) < 2:
                minutes = f"0{minutes}"
                
            inline_keyboard.append([InlineKeyboardButton(text=f"{i[2]} {i[3].hour}:{minutes}", callback_data=f"daily_task_{i[0]}")])
    inline_keyboard.append([InlineKeyboardButton(text="Новое задание ✏️", callback_data="new_daily_task")])

    return InlineKeyboardMarkup(
        inline_keyboard=inline_keyboard
    )

@router.message(F.text == "Ежедневные задания 📑")
async def daily_tasks_button(message: Message):
    await message.answer(choice(phrases["daily_tasks"]), parse_mode="html", reply_markup=keyboards.daily_tasks)

@router.message(F.text == "Задания 📋")
async def tasks(message: Message):
    tasks = manager.get_daily_tasks(message.from_user.id)
    if len(tasks) == 0:
        await message.answer("😞 <b>У вас ещё нет ежедневных заданий</b>. Нам следует немедленно их сделать!", parse_mode="html", reply_markup=get_daily_tasks_keyboard(tasks))
    else:
        await message.answer("📑 Сегодня у вас:", parse_mode="html", reply_markup=get_daily_tasks_keyboard(tasks))


@router.callback_query(F.data == "new_daily_task")
async def new_daily_task1(callback_query: CallbackQuery, state: FSMContext, bot: Bot):
    await state.set_state(new_dtask.name)
    await bot.send_message(callback_query.from_user.id, "😉 Окей, давайте для начала зададим ей имя:")

@router.message(new_dtask.name)
async def new_daily_task2(message: Message, state: FSMContext, bot: Bot):
    try:
        await state.update_data(name = message.text)
        await bot.send_message(message.from_user.id, "Отлично! Теперь напишем небольшое описание для нового задания:")
        await state.set_state(new_dtask.about)

    except Exception as _ex:
        print("[ERROR]:", _ex)
        await message.answer("😣 Упс... Кажется произошла ошибка. Возможно вы неправильно задали имя.")
        await state.clear()

@router.message(new_dtask.about)
async def new_daily_task3(message: Message, state: FSMContext, bot: Bot):
    try:
        await state.update_data(about = message.text)
        await bot.send_message(message.from_user.id, "Почти готово, осталось выбрать время для нашего задания! Введите время в формате <b>часы:минуты</b>, например: 13:50 или 17:00.", parse_mode="html")
        await state.set_state(new_dtask.time)

    except Exception as _ex:
        print("[ERROR]:", _ex)
        await message.answer("😣 Упс... Кажется произошла ошибка. Возможно вы неправильно ввели описание.")
        await state.clear()

@router.message(new_dtask.time)
async def new_daily_task4(message: Message, state: FSMContext, bot: Bot):
    try:
        splitted = message.text.split(":")
        if len(splitted) == 2:
            hours = isNumber(splitted[0])
            minutes = isNumber(splitted[1])
            if hours != -1 and minutes != -1:
                await state.update_data(time = time(hours, minutes))
                data = await state.get_data()
                manager.upload_new_daily_task(message.from_user.id, data["name"], data["about"], data["time"])

                await bot.send_message(message.from_user.id, "✅ <b>|</b> Новое задание создано! Теперь вы можете увидеть его в своём списке ежедневных задач.\n\n😘 Я буду автоматически напоминать вам о нём каждый день!", parse_mode="html")
                await state.clear()
            else:
                await message.answer("😣 Упс... Кажется произошла ошибка. Возможно вы ввели время в неправильном формате, попробуйте ещё раз!")
        else:
            await message.answer("😣 Упс... Кажется произошла ошибка. Возможно вы ввели время в неправильном формате, попробуйте ещё раз!")

    except Exception as _ex:
        print("[ERROR]:", _ex)
        await message.answer("😣 Упс... Кажется произошла ошибка. Возможно вы неправильно ввели описание.")
        await state.clear()

