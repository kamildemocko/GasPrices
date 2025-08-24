import sys
sys.path.insert(0, "../")

import os
import asyncio
from pathlib import Path

import httpx
from dotenv import load_dotenv

from shared.fetchers import fetch_url, fetch_urls_from_file
from shared.model import GasStationItem
from shared.store import Store


async def main() -> None:
    print("getting prices...")

    urls_path = Path("urls.txt")
    urls = fetch_urls_from_file(urls_path)

    pg_dsn = os.getenv("DSN", "")
    store = Store(pg_dsn)

    all_urls_responses: list[GasStationItem] = []

    async with httpx.AsyncClient() as client:
        tasks = [fetch_url(client, url) for url in urls]
        responses = await asyncio.gather(*tasks)
        responses_expanded = [item for sublist in responses for item in sublist]

        all_urls_responses.extend(responses_expanded)

    print("inserting into DB...")
    store.insert_prices(all_urls_responses)
    
    print("done")

if __name__ == "__main__":
    load_dotenv()
    asyncio.run(main())
