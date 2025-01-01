import asyncio
import json

from aiogram import types
from aiogram import Bot, Dispatcher
from aiogram.fsm.context import FSMContext
from aiogram.filters.command import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo

bot = Bot(token = "7722907926:AAHe9pfBs74AbiC49nPpx8IcS9NpJ-vC-ew")
dp = Dispatcher()

@dp.message (Command('start'))
async def start(message: types.Message, state: FSMContext):
    item1 = KeyboardButton (text="Vybrat product", web_app=WebAppInfo (url='https://174a-213-230-102-203.ngrok-free.app'))
    keyboard=ReplyKeyboardMarkup (keyboard=[[item1]], resize_keyboard=True)
    await bot.send_message(message.from_user.id, "Dobro pojalovat v *Burger Food Is Good",reply_markup = keyboard, parse_mode="Markdown")

@dp.message()
async def web_app(callback_query):
    json_data = callback_query.web_app_data.data
    parsed_data = json.loads(json_data)
    message = ""
    for i, item in enumerate(parsed_data['items'], start = 1):
        position = int(item['id'].replace('item',''))
        message += f"Position{position}\n"
        message += f"Price:{item['price']}\n\n"

    message += f"Total price: {parsed_data['totalPrice']}"

    await bot.send_message(callback_query.from_user.id, f"""
    {message}
    """)
    await bot.send_message('-1002063166054', f"""New Order{message}""")

async def main():
    await dp.start_polling(bot)
if __name__ == "_main__":
    asyncio.run(main())