import asyncio
from aiogram import F
import logging
from aiogram import Bot, Dispatcher
from aiogram.filters.command import Command
from db import create_table
from handlers import right_answer, wrong_answer, cmd_start, cmd_quiz, cmd_stats

logging.basicConfig(level=logging.INFO)

API_TOKEN = ''

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Регистрация хэндлеров
dp.callback_query.register(right_answer, F.data == "right_answer")
dp.callback_query.register(wrong_answer, F.data == "wrong_answer")
dp.message.register(cmd_start, Command("start"))
dp.message.register(cmd_quiz, F.text == "Начать игру" or Command("quiz"))
dp.message.register(cmd_stats, F.text == "Показать статистику" or Command("stats"))

async def main():
    await create_table()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
