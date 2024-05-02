from aiogram import Bot, Dispatcher, types, executor
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.storage import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import logging
from config import token 
import sqlite3
import time

chat = '-4144335544'
bot = Bot(token=token)
memory = MemoryStorage()
dp = Dispatcher(bot, storage=memory)
logging.basicConfig(level=logging.INFO)

connection = sqlite3.connect('intership.db')
cursor = connection.cursor()

cursor.execute("""CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY,
    username VARCHAR(255),
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    created VARCHAR(255)
);
""")

cursor.execute("""CREATE TABLE IF NOT EXISTS internship(
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    created VARCHAR(100)
);
""")

start_inline_buttons = [
    types.InlineKeyboardButton('Стажировка', callback_data='intership_callback'),
    types.InlineKeyboardButton('Наш сайт', url='https://geeks.kg/'),
    types.InlineKeyboardButton('Наш инстаграм', url='https://instagram.com/geeks_osh/'),
]
start_keyboard = types.InlineKeyboardMarkup().add(*start_inline_buttons)

class IntershipForm(StatesGroup):
    first_name = State()
    last_name = State()

@dp.message_handler(commands='start')
async def start(message: types.Message):
    cursor.execute(f"SELECT id FROM users WHERE id = {message.from_user.id};")
    result = cursor.fetchall()
    print(result)
    if result == []:
        cursor.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?);",
                       (message.from_user.id, message.from_user.username,
                        message.from_user.first_name, message.from_user.last_name,
                        time.ctime()))
        cursor.connection.commit()
    await message.answer(f"{message.from_user.full_name} привет", reply_markup=start_keyboard)

@dp.callback_query_handler(lambda call: call.data == "intership_callback")
async def intership_callback(callback: types.CallbackQuery):
    await callback.answer("Отлично! Теперь отправь мне своё имя и фамилию.")
    await IntershipForm.first_name.set()

@dp.message_handler(state=IntershipForm.first_name)
async def process_first_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['first_name'] = message.text
    await message.reply("Спасибо! Теперь отправь мне свою фамилию.")
    await IntershipForm.next()

@dp.message_handler(state=IntershipForm.last_name)
async def process_last_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['last_name'] = message.text
        
        cursor.execute("INSERT INTO internship (first_name, last_name, created) VALUES (?, ?, ?);",
                       (data.get('first_name', ''), data.get('last_name', ''), time.strftime('%Y-%m-%d %H:%M:%S')))
        cursor.connection.commit()
        
        
        if 'first_name' in data and 'last_name' in data:
        
            await bot.send_message(-1002113332966,
                                   f"Новая заявка на стажировку:\n"
                                   f"Имя: {data['first_name']}\n"
                                   f"Фамилия: {data['last_name']}")
            await message.reply("Спасибо! Ваша заявка на стажировку принята.")
        else:
            await message.reply("Извините, произошла ошибка. Пожалуйста, заполните все необходимые поля.")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)