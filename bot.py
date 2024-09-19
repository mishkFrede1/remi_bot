import asyncio
import os
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
from aiogram.client.bot import DefaultBotProperties

from handlers import base_commands, daily_tasks
from utils.scheduler import scheduler, start_all_notices_daily_tasks, start_scheduler

async def main():
    load_dotenv()
    bot = Bot(os.getenv('TOKEN'), default=DefaultBotProperties(parse_mode="HTML"))
    dp = Dispatcher(bot=bot)
    
    dp.include_routers(
        base_commands.router,
        daily_tasks.router
    )

    start_scheduler()
    start_all_notices_daily_tasks(bot)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
