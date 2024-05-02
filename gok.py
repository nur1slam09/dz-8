from aiogram import Bot, Dispatcher, types, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from config import token
from logging import basicConfig, INFO
import sqlite3
from datetime import datetime

bot = Bot(token)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
basicConfig(level=INFO)

class OrderFoodState(StatesGroup):
    name = State()
    title = State()
    phone_number = State()
    address = State()

connect = sqlite3.connect('ojak_kebap.db')
cursor = connect.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username VARCHAR(100),
        first_name VARCHAR(100),
        last_name VARCHAR(100),
        date_joined DATETIME
);''')

connect.commit()
cursor.execute(''' CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR(100),
        title TEXT,
        phone_number VARCHAR(100),
        address VARCHAR(100)
);''')
connect.commit()



start_buttons = [
    types.KeyboardButton('О нас'),
    types.KeyboardButton('Меню'),
    types.KeyboardButton('Адрес'),
    types.KeyboardButton('Заказать еду'),
]
start_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True).add(*start_buttons)


@dp.message_handler(commands='start')
async def start(message:types.Message):
    cursor=connect.cursor()
    cursor.execute(f"SELECT id FROM users WHERE id = {message.from_user.id};")
    res = cursor.fetchall()
    if not res:
        cursor.execute(f"""INSERT INTO users (id, username, first_name, last_name, date_joined) VALUES (
            {message.from_user.id},
            '{message.from_user.first_name}',
            '{message.from_user.last_name}',
            '{message.from_user.username}',
            '{datetime.now()}'
);""")
        
        cursor.connection.commit()
@dp.message_handler(text='Меню')
async def manu(message:types.Message):
    await message.answer("Шашлыки'🖇\nhttps://nambafood.kg/ojak-kebap", reply_markup=start_keyboard)


@dp.message_handler(text='О нас')
async def about(message:types.Message):
    await message.answer('''Кафе "Ожак Кебап" на протяжении 18 лет радует своих гостей с изысканными турецкими блюдами в особенности своим кебабом.

Наше кафе отличается от многих кафе своими доступными ценами и быстрым сервисом.

В 2016 году по голосованию на сайте "Horeca" были удостоены "Лучшее кафе на каждый день" и мы стараемся оправдать доверие наших гостей.

Мы не добавляем консерванты, усилители вкуса, красители, ароматизаторы, растительные и животные жиры, вредные добавки с маркировкой «Е». У нас строгий контроль качества: наши филиалы придерживаются норм Кырпотребнадзор и санэпидемстанции. Мы используем только сертифицированную мясную и рыбную продукцию от крупных поставщиков''')


@dp.message_handler(text = 'Адрес')
async def address(message: types.Message):
    await message.answer(" Адрес:  234، 246 Курманжан-Датка ул., Ош")
   


@dp.message_handler(text='Заказать еду')
async def about(message:types.Message):
    await message.answer('Введите ваше имя: ')
    await OrderFoodState.name.set()


@dp.message_handler(state=OrderFoodState.name)
async def process_food_title(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text
    await message.answer("Что хотите заказать?")
    await OrderFoodState.next()

@dp.message_handler(state=OrderFoodState.title)
async def process_food_title(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['title'] = message.text
    await message.answer("Введите свой номер телефона: ")
    await OrderFoodState.next()
    
@dp.message_handler(state=OrderFoodState.phone_number)
async def process_food_title(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['phone_number'] = message.text
    await message.answer("Введите свой адрес:")
    await OrderFoodState.next()


@dp.message_handler(state=OrderFoodState.address)
async def process_food_title(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['address'] = message.text

    async with state.proxy() as data:
        name = data['name']
        title = data['title']
        phone_number = data['phone_number']
        address = data['address']

    cursor.execute('''
        INSERT INTO orders (name, title, phone_number, address )
        VALUES (?, ?, ?, ?)
    ''', (name, title, phone_number, address))
    connect.commit()

    await message.answer("Ваш заказ принять.")


executor.start_polling(dp)

    
         






