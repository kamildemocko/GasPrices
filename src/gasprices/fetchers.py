import re
from datetime import datetime
from pathlib import Path

import arrow
import httpx
from selectolax.parser import HTMLParser

from model import GasStationItem


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


def _parse_url(response: httpx.Response) -> list[GasStationItem]:
    tree = HTMLParser(response.content)
    items = tree.css(".gas_block_1")

    gas_stations =[]
    for item in items:
        title = item.css_first("h2")
        assert title is not None

        title_parts = title.text().split("/", maxsplit=1)
        assert len(title_parts) == 2
        station = title_parts[0]
        name = title_parts[1]

        city = item.css_first("p a")
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
        gas_price = _parse_price(gas.text())
        diesel = fuel_nodes[1]
        diesel_price = _parse_price(diesel.text())
        lpg = fuel_nodes[2]
        lpg_price = _parse_price(lpg.text())

        if gas_price is None and diesel_price is None and lpg_price is None:
            continue

        last_updated = prices_node.css_first(".last_upd_fuel")
        last_updated = "" if last_updated is None else last_updated.text()

        if last_updated == "":
            continue

        gas_stations.append(GasStationItem(
            name=name.strip(),
            station=station.strip(),
            gas=gas_price,
            diesel=diesel_price,
            lpg=lpg_price,
            last_updated=_parse_date(last_updated),
            location=city.text(),
            lat=latlon[0],
            lon=latlon[1],
        ))
    
    return gas_stations


async def fetch_url(client: httpx.AsyncClient, url: str) -> list[GasStationItem]:
    try:
        res = await client.get(url)
        res.raise_for_status()

    except httpx.HTTPError as hte:
        print(f"error fetching {url}: {hte}")
        return []

    return _parse_url(res)


def fetch_urls_from_file(path: Path) -> list[str]:
    urls: list[str] = []

    with path.open("r", encoding="utf-8") as file:
        for line in file.readlines():
            if line.startswith("#"):
                continue

            urls.append(line.strip())
    
    return urls
