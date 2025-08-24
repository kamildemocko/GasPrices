from dataclasses import dataclass
from datetime import datetime


@dataclass
class GasStationItem:
    name: str
    gas: float | None
    diesel: float | None
    lpg: float | None
    last_updated: datetime | None
    location: str
    lat: float
    lon: float
