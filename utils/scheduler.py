from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from db_manager import Manager
from utils.send_reminder import send_daily_task_reminder, send_daily_task_hour_before_reminder

scheduler = AsyncIOScheduler()
manager = Manager()

def start_scheduler():
    scheduler.start()

def scheduler_off_daily_tasks(user_id):
    """
    Stops all scheduled tasks for a specific user (daily tasks).

    :param user_id: User's telegram id .
    """

    tasks = manager.get_daily_tasks(user_id)

    for i in tasks:
        scheduler.pause_job(job_id=f"job_id_dailytask_{i[0]}")#dailytaskbefore
        try:
            scheduler.pause_job(job_id=f"job_id_dailytaskbefore_{i[0]}")
        except: pass

def scheduler_on_daily_tasks(user_id):
    """
    Starts all scheduled tasks for a specific user.

    :param user_id: User's telegram id .
    """
    
    tasks = manager.get_daily_tasks(user_id)

    for i in tasks:
        scheduler.resume_job(job_id=f"job_id_dailytask_{i[0]}")
        try:
            scheduler.resume_job(job_id=f"job_id_dailytaskbefore_{i[0]}")
        except: pass

def start_all_notices_daily_tasks(bot: Bot):
    """
    Create and starts notices for all daily tasks.

    :param bot: aiogram Bot object.
    """
    ids = manager.get_all_user_id()

    for id in ids:
        #user_notice = manager.get_daily_tasks_setting(id)

        tasks = manager.get_daily_tasks(id)
        for task in tasks:
            task_id = task[0]
            name = task[2]
            hour = task[3].hour
            minute = task[3].minute
            about = task[4]
            completed = task[5]

            notice_args = [
                id,
                bot,
                name,
                hour,
                minute,
                about,
                completed
            ]

            remind_an_hour_before = manager.get_daily_tasks_setting(id, "remind_an_hour_before")
            if remind_an_hour_before:
                scheduler.add_job(send_daily_task_hour_before_reminder, 'cron', day_of_week='mon-sun', hour=hour-1, minute=minute, args=notice_args, id=f"job_id_dailytaskbefore_{task_id}")

            #day_of_week = get_days_str(days)
            # keyboard = InlineKeyboardMarkup(inline_keyboard=[
            #     [InlineKeyboardButton(text="Показать тренировку", callback_data=f"info_{training_id}")]
            # ])
            scheduler.add_job(send_daily_task_reminder, 'cron', day_of_week='mon-sun', hour=hour, minute=minute, args=notice_args, id=f"job_id_dailytask_{task_id}")

            # if not user_notice:
            #     scheduler.pause_job(f"job_id_{training_id}")

def start_new_daily_task_notice(notice_args: list, hour: int, minute: int, task_id: int):
    remind_an_hour_before = manager.get_daily_tasks_setting(notice_args[0], "remind_an_hour_before")
    if remind_an_hour_before:
        scheduler.add_job(send_daily_task_hour_before_reminder, 'cron', day_of_week='mon-sun', hour=hour-1, minute=minute, args=notice_args, id=f"job_id_dailytaskbefore_{task_id}")
    scheduler.add_job(send_daily_task_reminder, 'cron', day_of_week='mon-sun', hour=hour, minute=minute, args=notice_args, id=f"job_id_dailytask_{task_id}")
    print(scheduler.get_jobs())