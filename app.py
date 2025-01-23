import pandas as pd
import dash
from dash import dcc, html
import plotly.express as px
from htmlSections.release_decade_bar import ReleaseDecadeBar
from htmlSections.future_releases_scatter import FutureReleasesScatter
from htmlSections.votes_decade_bar import VotesDecadeBar
import htmlSections.section


# Initialize Dash app
app = dash.Dash(__name__)

# Load and preprocess data
data = pd.read_csv("./data/Imdb-Movie-Dataset.csv").drop_duplicates()
data["release_date"] = pd.to_datetime(data["release_date"], errors="coerce")

sections: list[htmlSections.section.Section] = [
    ReleaseDecadeBar(app=app, data=data),
    VotesDecadeBar(app=app, data=data),
    FutureReleasesScatter(app=app, data=data),
]

app.layout = [section.get_html() for section in sections]

# Run server
if __name__ == "__main__":
    app.run_server(debug=True)
