import os
import redis
import aiohttp
import asyncio
import xml.etree.ElementTree as ET


REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_DB = 0

CBR_URL = os.getenv('CBR_URL', 'https://www.cbr.ru/scripts/XML_daily.asp')


async def fetch_exchange_rates():
    async with aiohttp.ClientSession() as session:
        async with session.get(CBR_URL) as response:
            return await response.text()


def parse_exchange_rates(xml_data):
    root = ET.fromstring(xml_data)
    rates = {}
    for valute in root.findall('Valute'):
        char_code = valute.find('CharCode').text
        value = float(valute.find('Value').text.replace(',', '.'))
        rates[char_code] = value
    return rates


def save_to_redis(rates):
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)
    r.set("RUB", 1.0)
    for currency, rate in rates.items():
        r.set(currency, rate)


async def update_rates():
    xml_data = await fetch_exchange_rates()
    rates = parse_exchange_rates(xml_data)
    save_to_redis(rates)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(update_rates())
