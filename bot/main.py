import sys
import os
from aiogram import Bot, Dispatcher, executor
from config import BOT_TOKEN
from bot.handlers import register_handlers

def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(bot)
    register_handlers(dp)
    executor.start_polling(dp, skip_updates=True)

if __name__ == "__main__":
    main() 