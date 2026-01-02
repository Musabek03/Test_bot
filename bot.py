import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from decouple import config as env

API_TOKEN = env('API_TOKEN')

bot = Bot(token=API_TOKEN)
dp = Dispatcher()


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(f"Assalawma aleykum {message.from_user.first_name} , bul matematika test bot!" )

async def main():
    print("Bot iske tusti...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())

