from dataclasses import dataclass
from datetime import datetime

import plotly.express as px
import polars as pl

@dataclass
class GasStationItem:
    name: str
    station: str
    gas: float | None
    diesel: float | None
    lpg: float | None
    last_updated: datetime | None
    location: str
    lat: float
    lon: float


@dataclass
class GasStationItems:
    items: list[GasStationItem]

    def create_html_graph(self) -> str:
        # Convert to DataFrame
        data = []
        for item in self.items:
            if item.last_updated:  # only include items with a timestamp
                if item.gas is not None:
                    data.append({"time": item.last_updated, "price": item.gas, "fuel": "Gas",
                                "station": item.station, "city": item.location,
                                "lat": item.lat, "lon": item.lon})
                if item.diesel is not None:
                    data.append({"time": item.last_updated, "price": item.diesel, "fuel": "Diesel",
                                "station": item.station, "city": item.location,
                                "lat": item.lat, "lon": item.lon})
                if item.lpg is not None:
                    data.append({"time": item.last_updated, "price": item.lpg, "fuel": "LPG",
                                "station": item.station, "city": item.location,
                                "lat": item.lat, "lon": item.lon})
        df = pl.DataFrame(data)

        # Create interactive line chart with dropdowns
        fig = px.line(
            df,
            x="time",
            y="price",
            color="fuel",
            facet_row="city",
            facet_col="station",
            title="Fuel Prices Over Time"
        )

        # Add clickable points -> open Google Maps
        fig.update_traces(
            mode="lines+markers",
            customdata=df[["lat", "lon"]],
            hovertemplate="Fuel: %{color}<br>Price: %{y}<br>Time: %{x}<br><extra></extra>"
        )

        fig.update_layout(
            updatemenus=[
                {
                    "buttons": [
                        {
                            "label": "All Stations",
                            "method": "update",
                            "args": [{"visible": [True] * len(fig.data)}]
                        }
                    ],
                    "direction": "down",
                    "showactive": True,
                }
            ]
        )

        # Add click behavior (JS snippet for Google Maps)
        fig.update_layout(
            clickmode="event+select"
        )

        js_code = """
        <script>
        document.querySelectorAll('.plotly-graph-div').forEach(function(gd) {
            gd.on('plotly_click', function(data) {
                var point = data.points[0];
                var lat = point.customdata[0];
                var lon = point.customdata[1];
                var url = "https://www.google.com/maps?q=" + lat + "," + lon;
                window.open(url, "_blank");
            });
        });
        </script>
        """

        # Save as self-contained HTML
        html_str = fig.to_html(include_plotlyjs="cdn", full_html=True)
        html_str = html_str.replace("</body>", js_code + "</body>")

        return html_str
