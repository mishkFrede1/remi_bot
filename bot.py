import asyncio
import os
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

from handlers import base_commands

async def main():
    load_dotenv()
    bot = Bot(os.getenv('TOKEN'))
    dp = Dispatcher(bot=bot)
    
    dp.include_routers(
        base_commands.router
    )

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())