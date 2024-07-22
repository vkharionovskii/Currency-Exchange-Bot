import asyncio
from datetime import datetime, timedelta
from rates_updater import update_rates

async def schedule_updates():
    while True:
        try:
            await update_rates()
            print(f"Rates updated at {datetime.now()}")
        except Exception as e:
            print(f"Error updating rates: {e}")
        await asyncio.sleep(24 * 60 * 60)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(schedule_updates())
