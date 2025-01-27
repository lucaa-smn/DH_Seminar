import pandas as pd
import dash
from dash import dcc, html
from htmlSections.release_decade_bar import ReleaseDecadeBar
from htmlSections.future_releases_scatter import FutureReleasesScatter
from htmlSections.votes_decade_bar import VotesDecadeBar
from htmlSections.biggest_genre_decade import BiggestGenreChart
from htmlSections.genrePopularityOverDecades import GenrePopularityOverDecades
from htmlSections.itemDistribution import ItemDistribution
import htmlSections.section

app = dash.Dash(__name__)

# Load and preprocess data
data = pd.read_csv("./data/Imdb-Movie-Dataset.csv").drop_duplicates()
data["release_date"] = pd.to_datetime(data["release_date"], errors="coerce")
filtered_data = data[data["release_date"] < pd.Timestamp("2025-01-01")].copy()
filtered_data["decade"] = (filtered_data["release_date"].dt.year // 10) * 10

# Define sections
general_data_sections: list[htmlSections.section.Section] = [
    ItemDistribution(app=app, data=filtered_data),
    ReleaseDecadeBar(app=app, data=filtered_data),
    VotesDecadeBar(app=app, data=filtered_data),
    FutureReleasesScatter(app=app, data=data),
]

genre_analysis_sections: list[htmlSections.section.Section] = [
    BiggestGenreChart(app=app, data=filtered_data),
    GenrePopularityOverDecades(app=app, data=data),
]

# App layout
app.layout = html.Div(
    [
        # General description
        html.Div(
            [
                html.H1(
                    "IMDb Movie Data Dashboard",
                    style={"text-align": "center", "margin-bottom": "20px"},
                ),
                html.P(
                    "This dashboard provides an analysis of IMDb movie data, including release trends, "
                    "popular genres, and votes across decades. Explore insights into general data and genre-specific trends.",
                    style={
                        "text-align": "center",
                        "font-size": "18px",
                        "max-width": "800px",
                        "margin": "0 auto",
                        "margin-bottom": "40px",
                    },
                ),
            ],
            style={"padding": "20px"},
        ),
        # General Data section
        html.Div(
            [
                html.H1(
                    "General Data",
                    style={"text-align": "center", "margin-bottom": "20px"},
                ),
                *[section.get_html() for section in general_data_sections],
            ],
            style={"margin-bottom": "60px"},
        ),  # Adds extra spacing after General Data
        # Genre Analysis section
        html.Div(
            [
                html.H1(
                    "Genre Analysis",
                    style={"text-align": "center", "margin-bottom": "20px"},
                ),
                *[section.get_html() for section in genre_analysis_sections],
            ]
        ),
    ],
    style={"font-family": "Arial, sans-serif", "padding": "20px"},
)  # General page styling

if __name__ == "__main__":
    app.run_server(debug=True)
