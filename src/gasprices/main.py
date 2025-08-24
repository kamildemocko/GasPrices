import asyncio
from pathlib import Path

import httpx

from fetchers import fetch_url, fetch_urls_from_file
from model import GasStationItem


async def main() -> None:
    urls_path = Path("urls.txt")
    urls = fetch_urls_from_file(urls_path)

    all_urls_responses: list[list[GasStationItem]] = []

    async with httpx.AsyncClient() as client:
        tasks = [fetch_url(client, url) for url in urls]
        responses = await asyncio.gather(*tasks)

        all_urls_responses.extend(responses)

    print(all_urls_responses)


if __name__ == "__main__":
    asyncio.run(main())
