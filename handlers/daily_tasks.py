from aiogram import Router, F, Bot
from aiogram.filters import Command 
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from datetime import datetime, time

from data import keyboards, texts
from db_manager import Manager
from utils.is_number import isNumber
from data.phrases import phrases
from random import choice
from utils.scheduler import start_new_daily_task_notice

router = Router()
manager = Manager()

class new_dtask(StatesGroup):
    name = State()
    about = State()
    time = State()

class delete_dtask(StatesGroup):
    task_id = State()
    is_accept = State()

def get_daily_tasks_keyboard(tasks: list):
    inline_keyboard = []
    ln = len(tasks)
    if ln > 0:
        for i in tasks:
            minutes = i[3].minute
            if len(str(minutes)) < 2:
                minutes = f"0{minutes}"

            inline_keyboard.append([InlineKeyboardButton(text=f"{i[2]} {i[3].hour}:{minutes}", callback_data=f"daily_task_{i[0]}")])
    if ln < 10:
        inline_keyboard.append([InlineKeyboardButton(text="Создать задание ✏️", callback_data="new_daily_task")])

    return InlineKeyboardMarkup(
        inline_keyboard=inline_keyboard
    )

def get_settings_keyboard(status1: str, data1: str, status2: str, data2: str):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=f"Напоминать за час | {status1}", callback_data=f"settings_remindAnHourBefore_{data1}")],
            [InlineKeyboardButton(text=f"Настойчивость | {status2}", callback_data=f"settings_bePersistent_{data2}")]
        ]
    )
    return keyboard

@router.message(F.text == "Ежедневные задания 📑")
async def daily_tasks_button(message: Message):
    await message.answer(choice(phrases["daily_tasks"]), parse_mode="html", reply_markup=keyboards.daily_tasks)

@router.message(F.text == "Задания 📋")
async def tasks(message: Message):
    tasks = manager.get_daily_tasks(message.from_user.id)
    if len(tasks) == 0:
        await message.answer("😞 <b>У вас ещё нет ежедневных заданий</b>. Нам следует немедленно их сделать!", parse_mode="html", reply_markup=get_daily_tasks_keyboard(tasks))
    else:
        await message.answer("📑 Список ежедневных заданий:", parse_mode="html", reply_markup=get_daily_tasks_keyboard(tasks))


@router.callback_query(F.data == "new_daily_task")
async def new_daily_task1(callback_query: CallbackQuery, state: FSMContext, bot: Bot):
    await state.set_state(new_dtask.name)
    await bot.edit_message_text("😉 Окей, давайте для начала придумаем имя новому заданию:", callback_query.from_user.id, callback_query.message.message_id)

@router.message(new_dtask.name)
async def new_daily_task2(message: Message, state: FSMContext, bot: Bot):
    try:
        await state.update_data(name = message.text)
        await bot.send_message(message.from_user.id, "Отлично! Теперь напишем для него небольшое описание:")
        await state.set_state(new_dtask.about)

    except Exception as _ex:
        print("[ERROR]:", _ex)
        await message.answer("😣 Упс... Кажется произошла ошибка. Возможно вы неправильно задали имя")
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

                notice_args = [
                    message.from_user.id,
                    bot,
                    data["name"],
                    hours,
                    minutes,
                    data["about"],
                    False
                ]
                start_new_daily_task_notice(notice_args, hours, minutes, manager.get_daily_tasks_last_id(message.from_user.id))

                await bot.send_message(message.from_user.id, "✅ <b>|</b> <b>Новое задание создано!</b> \nТеперь вы можете увидеть его в своём списке ежедневных задач.\n\n😘 Я буду автоматически напоминать о нём каждый день!", parse_mode="html", reply_markup=keyboards.daily_tasks)
                await state.clear()
            else:
                await message.answer("😣 Упс... Кажется произошла ошибка. Возможно вы ввели время в неправильном формате, попробуйте ещё раз!")
        else:
            await message.answer("😣 Упс... Кажется произошла ошибка. Возможно вы ввели время в неправильном формате, попробуйте ещё раз!")

    except Exception as _ex:
        print("[ERROR]:", _ex)
        await message.answer("😣 Упс... Кажется произошла ошибка. Возможно вы ввели время в неправильном формате, попробуйте ещё раз!")
        await state.clear()

@router.callback_query(F.data.startswith("daily_task_"))
async def daily_task_info(callback_query: CallbackQuery, bot: Bot):
    task_id = int(callback_query.data.split("_")[2])
    task = manager.get_daily_task_by_id(task_id)
    complited = task[5]

    hour = task[3].hour
    minutes = task[3].minute
    if len(str(minutes)) < 2:
        minutes = f"0{minutes}"

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Удалить задание ❌", callback_data=f"delete_daily_task_{task_id}")],
            [InlineKeyboardButton(text="Назад ⤴️", callback_data="back_to_daily_tasks")]
        ]
    )
    text = texts.daily_task_uncomplited_text.format(name=task[2], hour=hour, minutes=minutes, description=task[4])
    if complited:
        text = texts.daily_task_complited_text.format(name=task[2], hour=hour, minutes=minutes, description=task[4])

    await bot.edit_message_text(text, callback_query.from_user.id, callback_query.message.message_id, reply_markup=keyboard)

@router.callback_query(F.data == "back_to_daily_tasks")
async def daily_task_back_to_list(callback_query: CallbackQuery, bot: Bot):
    tasks = manager.get_daily_tasks(callback_query.from_user.id)
    await bot.edit_message_text("📑 Список ежедневных заданий:", callback_query.from_user.id, callback_query.message.message_id, reply_markup=get_daily_tasks_keyboard(tasks), parse_mode="html")

@router.callback_query(F.data.startswith("delete_daily_task_"))
async def daily_task_delete(callback_query: CallbackQuery, state: FSMContext, bot: Bot):
    await state.set_state(delete_dtask.task_id)
    task_id = int(callback_query.data.split("_")[3])
    await state.update_data(task_id=task_id)
    await state.set_state(delete_dtask.is_accept)
    await bot.edit_message_text("🥺 <b>Вы точно уверены что хотите удалить это задание???</b>", callback_query.from_user.id, callback_query.message.message_id, reply_markup=keyboards.delete_daily_task)

@router.callback_query(delete_dtask.is_accept)
async def daily_task_delete_accept(callback_query: CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    task_id = int(data["task_id"])
    if callback_query.data == "yes_delete_daily_task":
        manager.delete_daily_task(task_id)
        await bot.edit_message_text("✅ <b>|</b> <b>Успешное удаление!</b>", callback_query.from_user.id, callback_query.message.message_id)
    else:
        await bot.edit_message_text("❎ <b>|</b> <b>Отмена!!!</b>", callback_query.from_user.id, callback_query.message.message_id)
    
    tasks = manager.get_daily_tasks(callback_query.from_user.id)
    if len(tasks) > 0:
        await bot.send_message(callback_query.from_user.id, "📑 Список ежедневных заданий:", reply_markup=get_daily_tasks_keyboard(tasks))
    await state.clear() 

@router.message(F.text == "Настройки 🛠")
async def daily_tasks_settings(message: Message):
    user = manager.get_user_data(message.from_user.id)
    status1 = "❌"
    data1 = "notActive"
    if user[4]:
        status1 = "✅"
        data1 = "active"

    status2 = "❌"
    data2 = "notActive"
    if user[5]:
        status2 = "✅"
        data2 = "active"

    await message.answer(choice(phrases["daily_tasks_settings"]), parse_mode="html", reply_markup=get_settings_keyboard(status1, data1, status2, data2))

@router.callback_query(F.data.startswith("settings_remindAnHourBefore_"))
async def daily_task_remindAnHourBefore_setting(callback_query: CallbackQuery, bot: Bot):
    data = callback_query.data.split("_")[2]
    value = False
    if data == "active": 
        data = "notActive"
        status = "❌"
    else: 
        data = "active"
        status = "✅"
        value = True

    user = manager.get_user_data(callback_query.from_user.id)
    status2 = "❌"
    data2 = "notActive"
    if user[5]:
        status2 = "✅"
        data2 = "active"

    manager.upload_new_daily_tasks_settings(callback_query.from_user.id, "remind_an_hour_before", value)
    await bot.edit_message_reply_markup(callback_query.from_user.id, callback_query.message.message_id, reply_markup=get_settings_keyboard(status, data, status2, data2))

@router.callback_query(F.data.startswith("settings_bePersistent_"))
async def daily_task_bePersistent_setting(callback_query: CallbackQuery, bot: Bot):
    data = callback_query.data.split("_")[2]
    value = False
    if data == "active": 
        data = "notActive"
        status = "❌"
    else: 
        data = "active"
        status = "✅"
        value = True

    user = manager.get_user_data(callback_query.from_user.id)
    status2 = "❌"
    data2 = "notActive"
    if user[4]:
        status2 = "✅"
        data2 = "active"

    manager.upload_new_daily_tasks_settings(callback_query.from_user.id, "persistence", value)
    await bot.edit_message_reply_markup(callback_query.from_user.id, callback_query.message.message_id, reply_markup=get_settings_keyboard(status2, data2, status, data))



