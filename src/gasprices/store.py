import atexit

import psycopg


class Store:
    def __init__(self, dsn: str) -> None:
        self.con = psycopg.connect(dsn)
        atexit.register(self.con.close)

        schema = "gasprices"
        table_name = "prices"

        self._create_table(schema, table_name)
    
    def _create_table(self, schema: str, table_name: str) -> None:
        query_create_schema = f"CREATE SCHEMA IF NOT EXISTS {schema};"

        query_create_table = f"""
        CREATE TABLE IF NOT EXISTS {schema}.{table_name} (
            id SERIAL PRIMARY KEY,
            created TIMESTAMP NOT NULL,
            name TEXT NOT NULL,
            gas DOUBLE PRECISION,
            diesel DOUBLE PRECISION,
            lpg DOUBLE PRECISION,
            last_updated TIMESTAMP,
            location TEXT NOT NULL,
            lat DOUBLE PRECISION NOT NULL,
            lon DOUBLE PRECISION NOT NULL
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
