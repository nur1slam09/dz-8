from aiogram.dispatcher.filters.state import State, StatesGroup             
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram import Bot, Dispatcher, types, executor
from aiogram.dispatcher.storage import FSMContext
from config import token
import logging, time, sqlite3,random

bot = Bot(token=token)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
logging.basicConfig(level=logging.INFO)

connection = sqlite3.connect('logis.db')
cursor = connection.cursor()

cursor.execute("""CREATE TABLE IF NOT EXISTS users(
    user_id INTEGER,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    phone  VARCHAR(100),
    region VARCHAR(30),
    created VARCAR(30)
);
""")

cursor.execute("""CREATE TABLE IF NOT EXISTS code(
    user VARCHAR(100),
    code VARCHAR(100),
    date VARCHAR(100)
);
""")

start_buttons = [
    types.KeyboardButton("Регистрация"),
    types.KeyboardButton("Шаблон регистрации"),
    types.KeyboardButton("О нас")  
]

start_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True).add(*start_buttons)

@dp.message_handler(commands='start')
async def start(message:types.Message):
    await message.answer("Привет, я чат- бот карго  компании Geeks!", 
    reply_markup=start_keyboard)
    
@dp.message_handler(text="Шаблон регистрации")
async def register_template(message:types.Message):
    await message.answer("""Для того, чтобы зарегистрироваться вам нужно:
1.Введите имя
2.Введите фамилию
3.Введите регион
Вот эти данные вам нужны для регистрации """)
    
class UserRegisterState(StatesGroup):
    first_name = State()
    last_name = State()
    phone = State()
    region = State()

@dp.message_handler(text="Регистрация")
async def register_template(message:types.Message):
    await message.answer("Для регистрации в нашем карго, нам нужно от вас:")
    await message.answer("Имя, фамилия, номер, регион")
    await message.answer("Введите свое имя:")
    await UserRegisterState.first_name.set()
    
@dp.message_handler(state=UserRegisterState.first_name)
async def get_last_name(message:types.Message, state:FSMContext):
    await state.update_data(first_name=message.text)
    await message.answer("Введите фамилию:")
    await UserRegisterState.last_name.set()
    
@dp.message_handler(state=UserRegisterState.last_name)
async def get_phone(message:types.Message, state:FSMContext):
    await state.update_data(last_name=message.text)
    await message.answer("Введите номер:")
    await UserRegisterState.phone.set()
    
@dp.message_handler(state=UserRegisterState.phone)
async def get_region(message:types.Message, state:FSMContext):
    await state.update_data(phone=message.text)
    await message.answer("Введите регион:")
    await UserRegisterState.region.set()
    
@dp.message_handler(state=UserRegisterState.region)
async def save_user_data(message:types.Message, state:FSMContext):
    await state.update_data(region=message.text)
    data = await state.get_data()
    user_id = message.from_user.id
    created = time.ctime()
    code = random.randint(1,99999)  

    cursor.execute("""
        INSERT INTO users (user_id, first_name, last_name, phone, region, created)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (user_id, data['first_name'], data['last_name'], data['phone'], data['region'], created))
    connection.commit()

    cursor.execute("""
        INSERT INTO code (user_id, code, date)
        VALUES (?, ?, ?)
    """, (user_id, code, created))
    connection.commit()

    await message.answer("Спасибо за регистрацию! Ваши данные были успешно сохранены в нашей базе данных.")
    
         
executor.start_polling(dp, skip_updates=True)


