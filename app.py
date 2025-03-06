import pandas as pd
import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, callback, Input, Output

# Importing Section Components
from htmlSections.release_decade_bar import ReleaseDecadeBar
from htmlSections.future_releases_scatter import FutureReleasesScatter
from htmlSections.votes_decade_bar import VotesDecadeBar
from htmlSections.biggest_genre_decade import BiggestGenreChart
from htmlSections.genrePopularityOverDecades import GenrePopularityOverDecades
from htmlSections.itemAnalysis import ItemAnalysis
from htmlSections.GenreMovieRankingOverDecades import GenreVoteAverageOverDecades
import htmlSections.section

# Initialize Dash app with Bootstrap theme
app = dash.Dash(
    __name__, external_stylesheets=[dbc.themes.LUX], suppress_callback_exceptions=True
)

# Load and preprocess data
data = pd.read_csv("./data/Imdb-Movie-Dataset.csv").drop_duplicates()
data["release_date"] = pd.to_datetime(data["release_date"], errors="coerce")
filtered_data = data[data["release_date"] < pd.Timestamp("2025-01-01")].copy()
filtered_data["decade"] = (filtered_data["release_date"].dt.year // 10) * 10

# Section Components
sections = {
    "Overview": ItemAnalysis(app=app, data=filtered_data),
    "Release Decades": ReleaseDecadeBar(app=app, data=filtered_data),
    "Votes Per Decade": VotesDecadeBar(app=app, data=filtered_data),
    "Future Releases": FutureReleasesScatter(app=app, data=data),
    "Biggest Genre": BiggestGenreChart(app=app, data=filtered_data),
    "Genre Popularity": GenrePopularityOverDecades(app=app, data=data),
    "Genre Ranking": GenreVoteAverageOverDecades(app=app, data=data),
}

# Sidebar Layout
sidebar = dbc.Card(
    dbc.CardBody(
        [
            html.H4("Navigation", className="text-center"),
            html.Hr(),
            dbc.Nav(
                [
                    dbc.NavLink(name, href=f"/{name.replace(' ', '_')}", active="exact")
                    for name in sections.keys()
                ],
                vertical=True,
                pills=True,
            ),
        ]
    ),
    className="shadow",
    style={
        "height": "100vh",
        "width": "250px",
        "position": "fixed",
        "top": "0",
        "left": "0",
    },
)

# Main Content Area
content = html.Div(id="page-content", className="p-4", style={"margin-left": "270px"})

# App Layout with Sidebar-Only Navigation
app.layout = html.Div(
    [
        dcc.Location(id="url"),  # Used to keep track of the URL
        sidebar,  # Sidebar for navigation
        content,  # Dynamic content area
    ]
)


# Callback to update content based on URL
@callback(Output("page-content", "children"), Input("url", "pathname"))
def display_page(pathname):
    # Extract tab name from URL
    page_key = pathname.strip("/").replace("_", " ")

    # Show corresponding content if tab name exists in sections
    if page_key in sections:
        return dbc.Card(
            dbc.CardBody(sections[page_key].get_html()), className="shadow p-4"
        )
    return html.H4("404 - Page Not Found", className="text-center text-danger")


# Run Server
if __name__ == "__main__":
    app.run_server(debug=True)
