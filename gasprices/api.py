import os
import uvicorn

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from dotenv import load_dotenv

from shared.store import Store
from shared.model import GasStationItems


load_dotenv()
app = FastAPI(title="Gas Prices API")


pg_dsn = os.getenv("DSN", "")
store = Store(pg_dsn)

@app.get("/prices/{days}", response_class=HTMLResponse)
async def get_prices_city(days: int) -> str:
    try:
        prices = store.get_prices_days(days)
        return prices.create_html_graph()
    
    except HTTPException as hte:
        raise HTTPException(status_code=500, detail=str(hte))


if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
