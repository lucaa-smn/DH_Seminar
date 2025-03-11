import pandas as pd
import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, callback, Input, Output

# Importing Section Components
from htmlSections.release_decade_bar import ReleaseDecadeBar

# from htmlSections.future_releases_scatter import FutureReleasesScatter
from htmlSections.votes_decade_bar import VotesDecadeBar
from htmlSections.biggest_genre_decade import BiggestGenreChart
from htmlSections.genrePopularityOverDecades import GenrePopularityOverDecades
from htmlSections.itemAnalysis import ItemAnalysis
from htmlSections.GenreMovieRankingOverDecades import GenreVoteAverageOverDecades
from htmlSections.budgetRevenueAnalysis import BudgetRevenueScatter
from htmlSections.ratingPopularityScatter import RatingPopularityScatter
from htmlSections.runtimePopularityRevenue import RuntimePopularityRevenue
from htmlSections.adultContentAnalysis import AdultContentAnalysis
from htmlSections.productionCompanyAnalysis import ProductionCompanyAnalysis
from htmlSections.countryPerformanceAnalysis import CountryPerformanceAnalysis

# Initialize Dash app with Bootstrap theme
app = dash.Dash(
    __name__, external_stylesheets=[dbc.themes.LUX], suppress_callback_exceptions=True
)

# Load and preprocess data
data = pd.read_csv("./data/Imdb-Movie-Dataset.csv").drop_duplicates()
data["release_date"] = pd.to_datetime(data["release_date"], errors="coerce")

# Filter out rows where revenue is <= 0
filtered_data = data[data["revenue"] > 0].copy()
filtered_data = filtered_data[filtered_data["runtime"] > 0].copy()

# Adjust vote_average for any misformatted values (values greater than 10)
# We'll assume any value above 10 is a misformatted number (e.g., 8364 should be 8.364)
filtered_data["vote_average"] = filtered_data["vote_average"].apply(
    lambda x: x / 1000 if x > 10 else x
)

# Convert release_date to datetime and filter for movies released before 2025
filtered_data["release_date"] = pd.to_datetime(
    filtered_data["release_date"], errors="coerce"
)
filtered_data = filtered_data[
    filtered_data["release_date"] < pd.Timestamp("2025-01-01")
].copy()

# Add a decade column for analysis
filtered_data["decade"] = (filtered_data["release_date"].dt.year // 10) * 10

# Section Components
sections = {
    "Overview": ItemAnalysis(app=app, data=filtered_data),
    "Releases Per Decade": ReleaseDecadeBar(app=app, data=filtered_data),
    "Votes Per Decade": VotesDecadeBar(app=app, data=filtered_data),
    # "Future Releases": FutureReleasesScatter(app=app, data=data),
    "Biggest Genre over Decades": BiggestGenreChart(app=app, data=filtered_data),
    "Genre Popularity over Decades": GenrePopularityOverDecades(
        app=app, data=filtered_data
    ),
    "Genre Ranking over Decades": GenreVoteAverageOverDecades(
        app=app, data=filtered_data
    ),
    "Budget vs. Revenue Analysis": BudgetRevenueScatter(app=app, data=filtered_data),
    "Rating vs. Popularity Analysis": RatingPopularityScatter(
        app=app, data=filtered_data
    ),
    "Runtime vs. Popularity/Revenue Analysis": RuntimePopularityRevenue(
        app=app, data=filtered_data
    ),
    "Adult Content Analysis": AdultContentAnalysis(app=app, data=filtered_data),
    "Production Company Analysis": ProductionCompanyAnalysis(
        app=app, data=filtered_data
    ),
    "Country Performance Analysis": CountryPerformanceAnalysis(
        app=app, data=filtered_data
    ),
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

# Welcome Message when no page is selected
welcome_message = dbc.Card(
    dbc.CardBody(
        [
            html.H3("Welcome to the Movie Data Dashboard!", className="text-center"),
            html.P(
                "This dashboard provides insights into various aspects of movies, including their release decades, votes, genres, and more.",
                className="text-center",
            ),
            html.P(
                "To get started, please choose a section from the navigation menu on the left.",
                className="text-center",
            ),
            html.Hr(),
            html.P(
                "Explore the data by clicking one of the links in the sidebar.",
                className="text-center",
            ),
        ]
    ),
    className="shadow p-4",
)

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

    # If no page selected, show welcome message
    return welcome_message


# Run Server
if __name__ == "__main__":
    app.run_server(debug=True)
