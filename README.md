# Gas Prices Scraper and Visualizer

A Python application that scrapes gas station prices from websites and visualizes the data through an interactive web interface.

## Features

- Scrapes fuel prices (gas, diesel, LPG) from specified websites
- Stores historical price data in a PostgreSQL database
- Provides an API to query historical prices
- Visualizes price trends with interactive Plotly charts
- Includes clickable map integration via Google Maps

## Requirements

- PostgreSQL database
- Environment variables for database connection

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/kamildemocko/GasPrices.git
    cd gasprices
    ```

2. Set up a virtual environment and dependencies:
    ```bash
    uv sync
    ```


3. Create a `.env` file with your PostgreSQL connection string:
    ```
    DSN=postgresql://username:password@localhost:5432/database
    ```

## Usage

### Running the scraper

The scraper reads URLs from `urls.txt` and stores the collected data in the database:

```bash
uv run gasprices/scrapper.py
```

### Running the API server

Start the FastAPI server to access the web visualization:

```bash
uv run gasprices/api.py
```

Then navigate to `http://localhost:8000/prices/{days}` where `{days}` is the number of days of historical data to display.

## Project Structure

- `gasprices/scrapper.py`: Main script for scraping fuel prices
- `gasprices/api.py`: FastAPI server for data visualization
- `gasprices/shared/`:
  - `fetchers.py`: Functions to fetch and parse webpage data
  - `model.py`: Data models and visualization logic
  - `store.py`: Database interactions

## Data Sources

Gas station prices are scraped from websites listed in `urls.txt`. Add or remove URLs as needed, using the `#` character for comments.
