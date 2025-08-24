import atexit

import psycopg
import arrow

from shared.model import GasStationItems, GasStationItem


class Store:
    def __init__(self, dsn: str) -> None:
        self.con = psycopg.connect(dsn)
        atexit.register(self.con.close)

        self.schema = "gasprices"
        self.table_name = "prices"

        self._create_table(self.schema, self.table_name)
    
    def _create_table(self, schema: str, table_name: str) -> None:
        query_create_schema = f"CREATE SCHEMA IF NOT EXISTS {schema};"

        query_create_table = f"""
        CREATE TABLE IF NOT EXISTS {schema}.{table_name} (
            id SERIAL PRIMARY KEY,
            created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            name TEXT NOT NULL,
            station TEXT NOT NULL,
            gas DOUBLE PRECISION,
            diesel DOUBLE PRECISION,
            lpg DOUBLE PRECISION,
            last_updated TIMESTAMP,
            location TEXT NOT NULL,
            lat DOUBLE PRECISION NOT NULL,
            lon DOUBLE PRECISION NOT NULL,
            CONSTRAINT uniq_name_station_last_updated UNIQUE(name, station, last_updated)
        );
        """

        query_create_indexes = f"""
        CREATE INDEX IF NOT EXISTS idx_fuel_location ON {schema}.{table_name}(location);
        CREATE INDEX IF NOT EXISTS idx_fuel_created ON {schema}.{table_name}(created);
        """

        with self.con.cursor() as cur:
            cur.execute(query_create_schema)  # type: ignore
            cur.execute(query_create_table)  # type: ignore
            cur.execute(query_create_indexes)  # type: ignore
        
        self.con.commit()
    
    def insert_prices(self, items: GasStationItems) -> None:
        query = f"""
        INSERT INTO {self.schema}.{self.table_name}
        (name, station, gas, diesel, lpg, last_updated, location, lat, lon)
        VALUES
        (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (name, station, last_updated) DO NOTHING;
        """

        data = [
            (i.name, i.station, i.gas, i.diesel, i.lpg, i.last_updated, i.location, i.lat, i.lon) 
            for i in items
        ]

        with self.con.cursor() as cur:
            cur.executemany(query, data)  # type: ignore
        
        self.con.commit()
    
    def get_prices_days(self, days: int) -> GasStationItems:
        today = arrow.now()
        then = today.shift(days=int(f"-{days}"))
        query = f"""
        SELECT name, station, gas, diesel, lpg, last_updated, location, lat, lon 
        FROM {self.schema}.{self.table_name}
        WHERE created >= %s AND created <= %s
        """
        
        with self.con.cursor() as cur:
            cur.execute(query, (then.datetime, today.datetime))
            rows = cur.fetchall()
            items = [GasStationItem(*row) for row in rows]
        
        return GasStationItems(items=items)
