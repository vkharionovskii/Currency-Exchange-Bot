import os
import redis
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message

TOKEN = os.getenv('TELEGRAM_TOKEN')
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_DB = 0

bot = Bot(token=TOKEN)
dp = Dispatcher()

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)


@dp.message(Command("start"))
async def start_command(message: Message):
    await message.answer(
        "Добро пожаловать! Я бот для получения актуальных курсов валют.\n"
        "Вы можете использовать следующие команды:\n"
        "/exchange <валюта1> <валюта2> <сумма> - для конвертации валюты\n"
        "/rates - для получения текущих курсов валют\n"
        "/help - для получения справки"
    )


@dp.message(Command("help"))
async def help_command(message: Message):
    await message.answer(
        "Справка по использованию бота:\n"
        "/exchange <валюта1> <валюта2> <сумма> - конвертирует указанную сумму из одной валюты в другую.\n"
        "Например, /exchange USD RUB 10 покажет, сколько рублей стоит 10 долларов.\n"
        "/rates - показывает текущие курсы валют.\n"
        "/start - приветственное сообщение.\n"
        "/help - это сообщение."
    )


@dp.message(Command("exchange"))
async def exchange_rate(message: Message):
    try:
        splited_msg = message.text.split()
        if len(splited_msg) < 4:
            raise Exception('Недостаточно аргументов: Используй - /exchange <валюта1> <валюта2> <сумма>')
        _, from_currency, to_currency, amount = splited_msg
        amount = float(amount)
        from_rate = r.get(from_currency.upper())
        to_rate = r.get(to_currency.upper())
        if from_rate is None or to_rate is None:
            raise Exception('Указана неизвестная валюта')
        from_rate = float(from_rate)
        to_rate = float(to_rate)
        result = (from_rate / to_rate) * amount
        await message.answer(f"{amount} {from_currency.upper()} = {result:.4f} {to_currency.upper()}")
    except Exception as e:
        await message.answer(f"Ошибка: {e}")


@dp.message(Command("rates"))
async def current_rates(message: Message):
    keys = r.keys()
    rates = {key.decode(): r.get(key).decode() for key in keys}
    rates_message = "\n".join([f"{currency}: {rate}" for currency, rate in rates.items()])
    await message.answer(rates_message)


@dp.message()
async def exchange_rate(message: Message):
    await help_command(message)


async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
