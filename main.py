import sqlite3
import logging
import asyncio
import csv
from datetime import datetime
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import State, StatesGroup
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# Recreate database table to ensure correct structure
def recreate_table():
    conn = sqlite3.connect("filters.db")
    cursor = conn.cursor()

    # Drop the existing table
    cursor.execute("DROP TABLE IF EXISTS user_filters")

    # Recreate the table with the new structure
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS user_filters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            category TEXT NOT NULL,
            location TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    conn.commit()
    conn.close()

# Initialize database connection
def init_db():
    recreate_table()
    conn = sqlite3.connect("filters.db")
    return conn

# Add filter to the database
def add_filter_to_db(conn, user_id, category, location):
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM user_filters WHERE user_id = ? AND category = ? AND location = ?",
        (user_id, category, location)
    )
    if cursor.fetchone():
        return False  # Duplicate filter

    cursor.execute(
        "INSERT INTO user_filters (user_id, category, location) VALUES (?, ?, ?)",
        (user_id, category, location)
    )
    conn.commit()
    return True

# List filters for a user
def list_filters_for_user(conn, user_id):
    cursor = conn.cursor()
    cursor.execute(
        "SELECT category, location, created_at FROM user_filters WHERE user_id = ?",
        (user_id,)
    )
    return cursor.fetchall()

# Get all filters
def get_all_filters(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, category, location FROM user_filters")
    return cursor.fetchall()

# Remove a filter for a user
def remove_filter_from_db(conn, user_id, category, location):
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM user_filters WHERE user_id = ? AND category = ? AND location = ?",
        (user_id, category, location)
    )
    conn.commit()

# Remove all filters for a user
def clear_filters_for_user(conn, user_id):
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM user_filters WHERE user_id = ?",
        (user_id,)
    )
    conn.commit()

# Save listings to CSV
def save_listings_to_csv(listings, filename="listings.csv"):
    with open(filename, mode="w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["title", "price", "link"])
        writer.writeheader()
        writer.writerows(listings)

# Logging
logging.basicConfig(level=logging.INFO)

bot = Bot(token="7622019784:AAEvQZ0nMZcrE-fE7m--NxwFbCXAJv-vLf4")
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Define states
class FilterStates(StatesGroup):
    waiting_for_category = State()
    waiting_for_location = State()
    waiting_for_remove_category = State()
    waiting_for_remove_location = State()
    waiting_for_facebook_login = State()
    waiting_for_facebook_password = State()

# Initialize database
conn = init_db()

facebook_credentials = {}

@dp.message(Command("start"))
async def start_command(message: Message):
    await message.answer("Welcome! Use /add_filter to start adding filters.")

@dp.message(Command("help"))
async def help_command(message: Message):
    help_text = (
        "Here are the available commands:\n"
        "/start - Start interacting with the bot\n"
        "/help - Show this help message\n"
        "/add_filter - Add a new filter\n"
        "/list_filters - List all your filters\n"
        "/remove_filter - Remove a specific filter\n"
        "/clear_filters - Remove all your filters\n"
        "/set_facebook_credentials - Set your Facebook login and password"
    )
    await message.answer(help_text)

@dp.message(Command("set_facebook_credentials"))
async def set_facebook_credentials_command(message: Message, state: FSMContext):
    await message.answer("Enter your Facebook login:")
    await state.set_state(FilterStates.waiting_for_facebook_login)

@dp.message(FilterStates.waiting_for_facebook_login)
async def handle_facebook_login(message: Message, state: FSMContext):
    await state.update_data(facebook_login=message.text)
    await message.answer("Enter your Facebook password:")
    await state.set_state(FilterStates.waiting_for_facebook_password)

@dp.message(FilterStates.waiting_for_facebook_password)
async def handle_facebook_password(message: Message, state: FSMContext):
    user_data = await state.get_data()
    facebook_credentials[message.from_user.id] = {
        "login": user_data.get("facebook_login"),
        "password": message.text
    }
    await message.answer("Your Facebook credentials have been saved.")
    await state.clear()

@dp.message(Command("add_filter"))
async def add_filter_command(message: Message, state: FSMContext):
    await message.answer("Enter the category you want to track:")
    await state.set_state(FilterStates.waiting_for_category)

@dp.message(FilterStates.waiting_for_category)
async def handle_category_input(message: Message, state: FSMContext):
    await state.update_data(category=message.text)
    await message.answer("Enter the location (zip code or city):")
    await state.set_state(FilterStates.waiting_for_location)

@dp.message(FilterStates.waiting_for_location)
async def handle_location_input(message: Message, state: FSMContext):
    user_data = await state.get_data()
    category = user_data.get("category")
    location = message.text

    # Save filter to database
    if add_filter_to_db(conn, message.from_user.id, category, location):
        await message.answer(f"Filter added:\nCategory: {category}\nLocation: {location}")

        # Notify admin about the new filter
        admin_id = 5285694652  # Replace with the actual admin ID
        try:
            await bot.send_message(admin_id, f"New filter added by user {message.from_user.id}:\nCategory: {category}, Location: {location}")
        except Exception as e:
            logging.error(f"Failed to notify admin: {e}")
    else:
        await message.answer("This filter already exists.")
    await state.clear()

@dp.message(Command("list_filters"))
async def list_filters_command(message: Message):
    filters = list_filters_for_user(conn, message.from_user.id)
    if not filters:
        await message.answer("You have no filters set.")
    else:
        filters_text = "\n".join([
            f"{i + 1}. Category: {category}, Location: {location}, Added: {created_at}"
            for i, (category, location, created_at) in enumerate(filters)
        ])
        await message.answer(f"Your filters:\n{filters_text}")

@dp.message(Command("remove_filter"))
async def remove_filter_command(message: Message, state: FSMContext):
    await message.answer("Enter the category of the filter you want to remove:")
    await state.set_state(FilterStates.waiting_for_remove_category)

@dp.message(FilterStates.waiting_for_remove_category)
async def handle_remove_category_input(message: Message, state: FSMContext):
    await state.update_data(category=message.text)
    await message.answer("Enter the location of the filter you want to remove:")
    await state.set_state(FilterStates.waiting_for_remove_location)

@dp.message(FilterStates.waiting_for_remove_location)
async def handle_remove_location_input(message: Message, state: FSMContext):
    user_data = await state.get_data()
    category = user_data.get("category")
    location = message.text

    # Remove filter from database
    remove_filter_from_db(conn, message.from_user.id, category, location)
    await message.answer(f"Filter removed:\nCategory: {category}\nLocation: {location}")
    await state.clear()

@dp.message(Command("clear_filters"))
async def clear_filters_command(message: Message):
    clear_filters_for_user(conn, message.from_user.id)
    await message.answer("All filters have been removed.")

@dp.message()
async def log_message(message: Message):
    logging.info(f"Received message: {message.text} from {message.from_user.id}")

async def scrape_facebook_marketplace(category, location):
    """Web scraping function for Facebook Marketplace using Selenium."""
    url = f"https://www.facebook.com/marketplace/{location}/search?query={category}"
    logging.info(f"Scraping URL: {url}")

    try:
        # Setup Selenium WebDriver with WebDriver Manager
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

        driver.get(url)
        await asyncio.sleep(5)  # Allow time for page to load

        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        driver.quit()

        with open("debug.html", "w", encoding="utf-8") as file:
            file.write(soup.prettify())

        listings = []
        for item in soup.find_all('div', class_='x1n2onr6'):
            try:
                title = item.find('span', class_='x3nfvp2').text.strip()
                price = item.find('span', class_='x1xmf6yo').text.strip()
                link = item.find('a', href=True)['href']
                listings.append({
                    "title": title,
                    "price": price,
                    "link": f"https://www.facebook.com{link}"
                })
            except AttributeError:
                continue

        # Save to CSV
        save_listings_to_csv(listings)

        return listings
    except Exception as e:
        logging.error(f"Error scraping Facebook Marketplace: {e}")
        return []

async def monitor_listings():
    while True:
        filters = get_all_filters(conn)
        for user_id, category, location in filters:
            listings = await scrape_facebook_marketplace(category, location)

            for listing in listings:
                message_text = (
                    f"New listing found!\n"
                    f"Title: {listing['title']}\n"
                    f"Price: {listing['price']}\n"
                    f"Link: {listing['link']}"
                )
                try:
                    await bot.send_message(user_id, message_text)
                    logging.info(f"Notified user {user_id}: {message_text}")
                except Exception as e:
                    logging.error(f"Failed to notify user {user_id}: {e}")

        await asyncio.sleep(60)

async def start_bot():
    try:
        asyncio.create_task(monitor_listings())
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(start_bot())
