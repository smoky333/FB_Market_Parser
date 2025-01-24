import logging
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
import asyncio
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()  # Создаем отдельно хранилище
dp = Dispatcher(storage=storage)  # Передаем только storage, а bot задается в методах

# State for adding filters
class AddFilterState(StatesGroup):
    waiting_for_category = State()
    waiting_for_location = State()

# Command: Start
@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer("Welcome! This bot will notify you about new listings on Facebook Marketplace.\nTo start tracking, use /add_filter.")

# Command: Add filter
@dp.message(Command("add_filter"))
async def add_filter(message: Message, state: FSMContext):
    await message.answer("Enter the category you want to track (e.g., iPhones, Cars, etc.):")
    await state.set_state(AddFilterState.waiting_for_category)

# Handle category input
@dp.message(AddFilterState.waiting_for_category)
async def handle_category_input(message: Message, state: FSMContext):
    await state.update_data(category=message.text)
    await message.answer("Enter the location (zip code or city):")
    await state.set_state(AddFilterState.waiting_for_location)

# Handle location input
@dp.message(AddFilterState.waiting_for_location)
async def handle_location_input(message: Message, state: FSMContext):
    user_data = await state.get_data()
    category = user_data.get("category")
    location = message.text

    # Save filter (for now, just echo it back)
    await message.answer(f"Filter added:\nCategory: {category}\nLocation: {location}")
    await state.clear()

# Start polling
async def main():
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
