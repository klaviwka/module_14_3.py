from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor

API_TOKEN = ''
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


class UserState(StatesGroup):
    waiting_for_weight = State()
    waiting_for_growth = State()
    waiting_for_age = State()


keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
button_calculate = KeyboardButton('Рассчитать')
button_info = KeyboardButton('Информация')
button_buy = KeyboardButton('Купить')
keyboard.add(button_calculate, button_info, button_buy)


products_info = [
    ('Product1', 'Описание 1', 100, r'C:\pythonlesson\lesson14.1\files\photo1.jpeg'),
    ('Product2', 'Описание 2', 200, r'C:\pythonlesson\lesson14.1\files\photo2.jpg'),
    ('Product3', 'Описание 3', 300, r'C:\pythonlesson\lesson14.1\files\photo3.jpg'),
    ('Product4', 'Описание 4', 400, r'C:\pythonlesson\lesson14.1\files\photo4.jpg')
]

@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    await message.answer('Привет! Я бот, помогающий твоему здоровью.\nВыберите действие:', reply_markup=keyboard)

@dp.message_handler(lambda message: message.text.lower() == 'рассчитать')
async def process_calculation(message: types.Message):
    await UserState.waiting_for_weight.set()
    await message.answer("Введите ваш вес (в кг):")

@dp.message_handler(state=UserState.waiting_for_weight)
async def process_weight(message: types.Message, state: FSMContext):
    try:
        weight = float(message.text)
        await state.update_data(weight=weight)

        await UserState.waiting_for_growth.set()
        await message.answer("Введите ваш рост (в см):")
    except ValueError:
        await message.answer("Пожалуйста, введите корректное число для веса.")

@dp.message_handler(state=UserState.waiting_for_growth)
async def process_growth(message: types.Message, state: FSMContext):
    try:
        growth = float(message.text)
        await state.update_data(growth=growth)

        await UserState.waiting_for_age.set()
        await message.answer("Введите ваш возраст (в годах):")
    except ValueError:
        await message.answer("Пожалуйста, введите корректное число для роста.")

@dp.message_handler(state=UserState.waiting_for_age)
async def process_age(message: types.Message, state: FSMContext):
    try:
        age = int(message.text)
        user_data = await state.get_data()

        weight = user_data['weight']
        growth = user_data['growth']


        calories = 10 * weight + 6.25 * growth - 5 * age + 5

        await message.answer(f"Ваши суточные калории: {calories:.2f} ккал.")
        await state.finish()
    except ValueError:
        await message.answer("Пожалуйста, введите корректное число для возраста.")

@dp.message_handler(lambda message: message.text.lower() == 'купить')
async def get_buying_list(message: types.Message):
    await message.answer("Вот наши продукты:")


    for name, description, price, photo_path in products_info:
        with open(photo_path, 'rb') as photo:
            await message.answer_photo(photo=photo, caption=f'{name}\nОписание: {description}\nЦена: {price} руб.')


    inline_keyboard = InlineKeyboardMarkup(row_width=2)

    for name, description, price, photo_path in products_info:

        inline_button = InlineKeyboardButton(name, callback_data=name)
        inline_keyboard.add(inline_button)

    await message.answer("Нажмите кнопку для покупки одного из продуктов:", reply_markup=inline_keyboard)

@dp.callback_query_handler(lambda call: call.data in [product[0] for product in products_info])
async def send_confirm_message(call: types.CallbackQuery):
    await call.message.answer("Вы успешно приобрели продукт!")
    await bot.answer_callback_query(call.id)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
