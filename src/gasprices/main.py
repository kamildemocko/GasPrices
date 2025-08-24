import asyncio
from pathlib import Path

import httpx

from fetchers import fetch_url


async def main() -> None:
    urls_path = Path("urls.txt")

    urls: list[str] = []
    with urls_path.open("r", encoding="utf-8") as file:
        for line in file.readlines():
            if line.startswith("#"):
                continue

            urls.append(line.strip())

    async with httpx.AsyncClient() as client:
        tasks = [fetch_url(client, url) for url in urls]
        responses = await asyncio.gather(*tasks)

        print(responses)


if __name__ == "__main__":
    asyncio.run(main())
