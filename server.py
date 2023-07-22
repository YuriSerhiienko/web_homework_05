import asyncio
import websockets
import aiohttp
import datetime
from aiofile import AIOFile
from aiopath import AsyncPath

async def fetch_exchange_rates(date):
    url = f"https://api.privatbank.ua/p24api/exchange_rates?json&date={date}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()

async def get_exchange_rates_for_last_days(num_days, currencies):
    current_date = datetime.datetime.now()
    exchange_rates = []

    for _ in range(num_days):
        date_str = current_date.strftime("%d.%m.%Y")
        data = await fetch_exchange_rates(date_str)

        rates = {}
        for rate in data['exchangeRate']:
            currency = rate['currency']
            if currency in currencies and rate['baseCurrency'] == 'UAH':
                rates[currency] = {'sale': rate['saleRate'], 'purchase': rate['purchaseRate']}

        exchange_rates.append({date_str: rates})
        current_date -= datetime.timedelta(days=1)

    return exchange_rates

async def handle_command(command):
    if command.startswith("exchange"):
        _, num_days, *currencies = command.split()
        num_days = int(num_days)
        currencies = set(currencies)
        rates = await get_exchange_rates_for_last_days(num_days, currencies)

        # Log the exchange command to a file
        log_file = AsyncPath("exchange_log.txt")
        async with AIOFile(log_file, "a") as afp:
            await afp.write(f"Received 'exchange' command: {command}\n")

        return rates
    else:
        return "Invalid command"

async def hello(websocket, path):
    async for message in websocket:
        print(f"<<< {message}")

        response = await handle_command(message)
        await websocket.send(str(response))
        print(f">>> {response}")

async def main():
    async with websockets.serve(hello, "localhost", 8765):
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())
