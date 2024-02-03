import asyncio
import logging
from datetime import datetime, timedelta

import websockets
from aiofiles import open as aio_open
from websockets import WebSocketServerProtocol
from websockets.exceptions import ConnectionClosedOK
import httpx

logging.basicConfig(level=logging.INFO)

currencies = ['USD', 'EUR']


async def request(url: str) -> dict | str:
    async with httpx.AsyncClient() as client:
        r = await client.get(url)
        if r.status_code == 200:
            result = r.json()
            return result
        else:
            return "Сервер впав ("


async def get_exchange(index_day: int = 0):
    if 0 <= index_day <= 10:
        d = datetime.now() - timedelta(days=int(index_day))
        shift = d.strftime("%d.%m.%Y")
    else:
        return "Invalid index for exchange command. Please use 'exchange' or 'exchange <index>' (2-10 days)."

    try:
        response = await request(f"https://api.privatbank.ua/p24api/exchange_rates?json&date={shift}")

        if 'exchangeRate' in response:
            exchange_rates = response['exchangeRate']
            formatted_result = {
                shift: {currency: {'sale': 0, 'purchase': 0} for currency in currencies}
            }

            for rate in exchange_rates:
                currency_code = rate.get('currency', '')
                if currency_code in currencies:
                    formatted_result[shift][currency_code]['sale'] = rate.get('saleRateNB', 0)
                    formatted_result[shift][currency_code]['purchase'] = rate.get('purchaseRateNB', 0)

            # Log exchange command
            await log_exchange_command(shift)

            return [formatted_result]
        else:
            print(f"No exchange rates found for {shift}")
            return None

    except httpx.HTTPError as err:
        print(f"HTTP error: {err}")
        return None


async def log_exchange_command(shift: str):
    async with aio_open('exchange_log.txt', 'a') as file:
        await file.write(f'{datetime.now()} Executed \'exchange\' command for date: {shift}\n')


class Server:
    clients = set()

    async def register(self, ws: WebSocketServerProtocol):
        ws.name = "User"  # You can set a default name for the user
        self.clients.add(ws)
        logging.info(f'{ws.remote_address} connects')

    async def unregister(self, ws: WebSocketServerProtocol):
        self.clients.remove(ws)
        logging.info(f'{ws.remote_address} disconnects')

    async def send_to_clients(self, message: str):
        if self.clients:
            [await client.send(message) for client in self.clients]

    async def ws_handler(self, ws: WebSocketServerProtocol):
        await self.register(ws)
        try:
            await self.distribute(ws)
        except ConnectionClosedOK:
            pass
        finally:
            await self.unregister(ws)

    async def distribute(self, ws: WebSocketServerProtocol):
        async for message in ws:
            if message.startswith("exchange"):
                try:
                    _, *rest = message.split()
                    if not rest:
                        # No index provided, use default (today)
                        exchange = await get_exchange()
                    else:
                        index_day = int(rest[0])
                        exchange = await get_exchange(index_day)
                    await self.send_to_clients(str(exchange))
                except ValueError:
                    await ws.send("Invalid command. Please use 'exchange' or 'exchange <index>' (2-10 days).")
            elif message == 'Hello server':
                await self.send_to_clients("Привіт мої карапузи!")
            else:
                await self.send_to_clients(f"{ws.name}: {message}")


async def main():
    server = Server()
    async with websockets.serve(server.ws_handler, '0.0.0.0', 8080):
        await asyncio.Future()  # run forever


if __name__ == '__main__':
    asyncio.run(main())
