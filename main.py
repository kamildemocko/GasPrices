import asyncio
from dataclasses import dataclass
import re
from datetime import datetime

import httpx
from selectolax.parser import HTMLParser
import arrow


URLS: list[str] = [
    "https://cerpacie-stanice.spotreba.sk/slovensko/kosice-i/?gas-station=Slovnaft",
    # "https://cerpacie-stanice.spotreba.sk/slovensko/kosice-ii/?gas-station=Slovnaft",
    # "https://cerpacie-stanice.spotreba.sk/slovensko/kosice-iii/?gas-station=Slovnaft",
    # "https://cerpacie-stanice.spotreba.sk/slovensko/kosice-iv/?gas-station=Slovnaft",
]


@dataclass
class Item:
    name: str
    gas: float | None
    diesel: float | None
    lpg: float | None
    last_updated: datetime | None
    location: str
    lat: float
    lon: float


def _parse_price(value: str | None) -> float | None:
    if value is None:
        return None

    if "---" in value:
        return None
    
    r = re.search("[0-9,]+", value)
    if r is None:
        return None
    
    value_dot = r.group(0).replace(",", ".")

    return float(value_dot)


def _parse_date(value: str | None) -> datetime | None:
    if value is None:
        return None

    r = re.search(r"\d{1,2}\.\d{1,2}\.\d{4}", value)
    if r is None:
        return None
    
    return arrow.get(r.group(0), "DD.MM.YYYY").datetime


def _parse_latlon(value: str | None) -> tuple[float, float]:
    if value is None:
        return 0, 0

    r = re.findall(r"-?\d{1,3}\.\d{1,6}", value)
    if r is None:
        return 0, 0
    
    assert len(r) == 2
    
    return float(r[0]), float(r[1])


def _parse_url(response: httpx.Response) -> list[Item]:
    tree = HTMLParser(response.content)
    items = tree.css(".gas_block_1")

    gas_stations =[]
    for item in items:
        title = item.css_first("h2")
        city = item.css_first("p a")
        assert title is not None
        assert city is not None

        latlon_holder = item.css_first("p")
        assert latlon_holder
        latlon = _parse_latlon(latlon_holder.text())

        prices_node = item.css_first(".gas_inf")
        assert prices_node is not None

        fuel_nodes = prices_node.css(".fuel")
        assert fuel_nodes is not None
        assert len(fuel_nodes) == 3

        gas = fuel_nodes[0]
        diesel = fuel_nodes[1]
        lpg = fuel_nodes[2]

        last_updated = prices_node.css_first(".last_upd_fuel")
        last_updated = "" if last_updated is None else last_updated.text()

        gas_stations.append(Item(
            name=title.text(),
            gas=_parse_price(gas.text()),
            diesel=_parse_price(diesel.text()),
            lpg=_parse_price(lpg.text()),
            last_updated=_parse_date(last_updated),
            location=city.text(),
            lat=latlon[0],
            lon=latlon[1],
        ))
    
    return gas_stations


async def job(client: httpx.AsyncClient, url: str) -> list[Item]:
    try:
        res = await client.get(url)
        res.raise_for_status()
    except httpx.HTTPError as hte:
        print(f"error fetching {url}: {hte}")
        return []

    return _parse_url(res)


async def main() -> None:
    async with httpx.AsyncClient() as client:
        tasks = [job(client, url) for url in URLS]
        responses = await asyncio.gather(*tasks)

        print(responses)


if __name__ == "__main__":
    asyncio.run(main())
