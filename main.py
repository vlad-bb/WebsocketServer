import sys
import json
import argparse
from datetime import datetime, timedelta
import httpx
import asyncio
import platform


class HttpError(Exception):
    pass


async def request(url: str):
    async with httpx.AsyncClient() as client:
        r = await client.get(url)
        if r.status_code == 200:
            result = r.json()
            return result
        else:
            raise HttpError(f"Error status: {r.status_code} for {url}")


async def main(index_day, currencies):
    d = datetime.now() - timedelta(days=int(index_day))
    shift = d.strftime("%d.%m.%Y")
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

            return [formatted_result]
        else:
            print(f"No exchange rates found for {shift}")
            return None
    except HttpError as err:
        print(f"HTTP error: {err}")
        return None


def parse_arguments():
    parser = argparse.ArgumentParser(description="Retrieve exchange rates.")
    parser.add_argument("index_day", type=int, help="Number of days to look back")
    parser.add_argument("--currencies", nargs="+", default=["USD", "EUR"], help="Additional currencies to include")
    return parser.parse_args()


if __name__ == '__main__':
    if platform.system() == "Windows":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    args = parse_arguments()
    result = asyncio.run(main(args.index_day, args.currencies))
    if result:
        print(json.dumps(result, indent=2))
    else:
        print("No data to display.")
