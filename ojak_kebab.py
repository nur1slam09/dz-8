from aiogram import Bot, Dispatcher,types, executor
from aiogram.dispatcher.storage import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from config import token 
import logging, sqlite3, time

chat_id = '-4143412669'
bot = Bot(token=token)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
logging.basicConfig(level=logging.INFO)



connection = sqlite3.connect('customer.db')
cursor = connection.cursor()
cursor.execute(f"""CREATE TABLE IF NOT EXISTS users(
    id INTEGER,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    username VARCHAR(100),
    date_joined VARCHAR(100)
    );
    """)
cursor.connection.commit()


cursor.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR(100),
        title TEXT,
        phone_number VARCHAR(100),
        address VARCHAR(100)
    );
""")
cursor.connection.commit()


start_keyboard = [
    types.KeyboardButton("Меню"),
    types.KeyboardButton("О нас"),
    types.KeyboardButton("Адрес"),
    types.KeyboardButton("Контакты"),
    types.KeyboardButton("Заказать еду")
]


start_button = types.ReplyKeyboardMarkup(resize_keyboard=True).add(*start_keyboard)


@dp.message_handler(commands='start')
async def start(message: types.Message):
    print(message)
    cursor.execute("SELECT id FROM users WHERE id = ?", (message.from_user.id,))
    output_cursor = cursor.fetchall()
    print(output_cursor)
    if output_cursor == []:
        cursor.execute("""
            INSERT INTO users (id, first_name, last_name, username, date_joined)
            VALUES (?, ?, ?, ?, ?)
        """, (
            message.from_user.id, message.from_user.first_name,
            message.from_user.last_name, message.from_user.username,
            time.ctime()
        ))
        cursor.connection.commit()
    await message.answer(f"Здравствуйте, {message.from_user.full_name}! Добро пожаловать в Oja Kebab!", reply_markup=start_button)




@dp.message_handler(text='Меню')
async def menu(message:types.Message):
    await message.answer_photo("https://plovnaya1.com/thumb/2/4u536ODndldp0QgIbKuM_A/r/d/lyulya-kebab_iz_govyadiny.jpg")
    await message.answer("Люля Кебаб - 180 сом")
    
    await message.answer_photo("https://nambafood.kg/dish_image/163137.png")
    await message.answer("Форель на мангале целиком - 710 сом")    
    
    await message.answer_photo("https://nambafood.kg/dish_image/163145.png")
    await message.answer("Форель на мангале кусочками - 1140 сом")
    
    await message.answer_photo("https://nambafood.kg/dish_image/48353.png")
    await message.answer("Шашлык из курицы - 400 сом")
      
    await message.answer_photo("https://nambafood.kg/dish_image/150933.png")
    await message.answer("Шашлык из баранины - 460 сом")
   


@dp.message_handler(text='О нас')
async def about_us(message:types.Message):
    await message.reply(f"""Кафе "Ожак Кебап" на протяжении 18 лет радует своих гостей с изысканными турецкими блюдами в особенности своим кебабом. Наше кафе отличается от многих кафе своими доступными ценами и быстрым сервисом. В 2016 году по голосованию на сайте "Horeca" были удостоены "Лучшее кафе на каждый день" и мы стараемся оправдать доверие наших гостей. Мы не добавляем консерванты, усилители вкуса, красители, ароматизаторы, растительные и животные жиры, вредные добавки с маркировкой «Е». У нас строгий контроль качества: наши филиалы придерживаются норм Кырпотребнадзор и санэпидемстанции. Мы используем только сертифицированную мясную и рыбную продукцию от крупных поставщиков.""")
    

@dp.message_handler(text='Адрес')
async def address(message:types.Message):
        await message.answer("Наш адресс: Курманжан-Датка 246, Ош +996700505333")
        await message.answer_location(40.526666914745896, 72.7953323597276)
    
@dp.message_handler(text='Контакты')
async def contact(message:types.Message):
    await message.answer("""+996700505333 \n+996777515515  \nВы можете забронировать столик!""")
    
       
    
    
    
class OrderFoodState(StatesGroup):
    name = State()
    title = State()
    phone_number = State()
    address = State()


@dp.message_handler(text='Заказать еду')
async def ordes(message:types.Message):
    await message.answer('Введите ваше имя')
    await OrderFoodState.name.set()


@dp.message_handler(state=OrderFoodState.name)
async def processtitle(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text

    await message.answer("Что хотите заказать?")
    await OrderFoodState.next()

@dp.message_handler(state=OrderFoodState.title)
async def process_food(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['title'] = message.text

    await message.answer("Введите свой номер телефона")
    await OrderFoodState.next() 
    
    
@dp.message_handler(state=OrderFoodState.phone_number)
async def process(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['phone_number'] = message.text

    await message.answer("Введите свой адрес")
    await OrderFoodState.next()


@dp.message_handler(state=OrderFoodState.address)
async def food_title(message: types.Message, state: FSMContext):
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
    connection.commit()
    await message.answer("Ваш заказ принять.\n Вам напишут наши операторы!")
    await state.finish()
    await bot.send_message(chat_id=chat_id, text=f"New order received:\nName: {name}\nTitle: {title}\nPhone Number: {phone_number}\nAddress: {address}")
    
    
    
executor.start_polling(dp, skip_updates=True)