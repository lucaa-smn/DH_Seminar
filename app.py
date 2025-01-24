import pandas as pd
import dash
from dash import dcc, html
from htmlSections.release_decade_bar import ReleaseDecadeBar
from htmlSections.future_releases_scatter import FutureReleasesScatter
from htmlSections.votes_decade_bar import VotesDecadeBar
from htmlSections.genre_decade_bar import GenreDecadeBar
import htmlSections.section


app = dash.Dash(__name__)

data = pd.read_csv("./data/Imdb-Movie-Dataset.csv").drop_duplicates()
data["release_date"] = pd.to_datetime(data["release_date"], errors="coerce")

filtered_data = data[data["release_date"] < pd.Timestamp("2025-01-01")].copy()
filtered_data["decade"] = (filtered_data["release_date"].dt.year // 10) * 10

sections: list[htmlSections.section.Section] = [
    ReleaseDecadeBar(app=app, data=filtered_data),
    VotesDecadeBar(app=app, data=filtered_data),
    FutureReleasesScatter(app=app, data=data),
    GenreDecadeBar(app=app, data=filtered_data),
]

app.layout = html.Div([section.get_html() for section in sections])

if __name__ == "__main__":
    app.run_server(debug=True)
