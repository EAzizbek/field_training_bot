import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
import redis.asyncio as redis
from aiogram.types import BotCommand

from bot.config import BOT_TOKEN

from bot.handlers import registration, workday

async def set_bot_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="Botni ishga tushirish"),
        BotCommand(command="help", description="Yordam"),
        BotCommand(command="ishni_boshlash", description="🚀 Ishni boshlash"),
        BotCommand(command="ishni_yakunlash", description="⏹ Ishni yakunlash"),
    ]
    await bot.set_my_commands(commands)

async def main():
    redis_client = redis.Redis(host="redis", port=6379, db=0)
    storage = RedisStorage(redis=redis_client)

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=storage)

    dp.include_router(registration.router)
    dp.include_router(workday.router)

    from bot.scheduler import daily
    await set_bot_commands(bot)

    print("🤖 Bot ishga tushdi...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("⛔ Bot to‘xtatildi.")
