import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px


class GenrePopularityOverDecades:
    def __init__(self, app: dash.Dash, data: pd.DataFrame) -> None:
        self.app = app

        # Make a copy of the data to prevent modification issues
        self.data = data.copy()

        # Convert release_date to datetime and filter out future movies
        self.data["release_date"] = pd.to_datetime(
            self.data["release_date"], errors="coerce"
        )
        self.data = self.data[self.data["release_date"].dt.year < 2025]

        # Create a decade column
        self.data["decade"] = (self.data["release_date"].dt.year // 10) * 10

        # Ensure genres column is properly formatted
        self.data["genres"] = (
            self.data["genres"]
            .astype(str)
            .str.replace(r"[\[\]']", "", regex=True)  # Remove brackets and quotes
            .str.split(", ")  # Split into lists
        )

        # Explode genres into separate rows
        self.exploded_data = self.data.explode("genres")

        # Clean genre names (remove extra spaces)
        self.exploded_data["genres"] = self.exploded_data["genres"].str.strip()

        # Drop rows where genres are empty or NaN
        self.exploded_data = self.exploded_data.dropna(subset=["genres"])
        self.exploded_data = self.exploded_data[self.exploded_data["genres"] != ""]

        # Compute average (or total) popularity per genre per decade
        self.genre_popularity = self.exploded_data.groupby(
            ["decade", "genres"], as_index=False
        )[
            "popularity"
        ].mean()  # Use .sum() if you want total popularity

        # Get available decades and prevent IndexError
        decades = sorted(self.genre_popularity["decade"].unique())
        default_decade = decades[0] if decades else None  # Avoid IndexError

        # Create the HTML layout
        self.div = html.Div(
            [
                html.H1(
                    "Genre Popularity Across Decades", style={"textAlign": "center"}
                ),
                html.H3("Select a Decade to View Genre Ranking"),
                dcc.Dropdown(
                    id="decade-dropdown-genre-popularity",
                    options=[
                        {"label": str(decade), "value": decade} for decade in decades
                    ],
                    value=default_decade,  # Prevent IndexError
                    placeholder="Select a decade" if not decades else None,
                ),
                dcc.Graph(id="decade-genre-ranking-chart"),
            ]
        )

        self.register_callbacks()

    def get_html(self) -> html.Div:
        return self.div

    def register_callbacks(self):
        @self.app.callback(
            Output("decade-genre-ranking-chart", "figure"),
            Input("decade-dropdown-genre-popularity", "value"),
        )
        def update_decade_genre_ranking_chart(selected_decade):
            if selected_decade is None:
                return px.bar(title="No Data Available")

            filtered_popularity = self.genre_popularity[
                self.genre_popularity["decade"] == selected_decade
            ]

            fig = px.bar(
                filtered_popularity,
                x="genres",
                y="popularity",
                color="popularity",
                title=f"Genre Ranking in {selected_decade}",
                labels={"genres": "Genre", "popularity": "Average Popularity"},
                text="popularity",
            )
            fig.update_traces(texttemplate="%{text:.2f}")
            fig.update_layout(
                xaxis_title="Genre",
                yaxis_title="Average Popularity",
                xaxis=dict(categoryorder="total descending"),
                coloraxis_colorbar=dict(title="Average Popularity"),
            )
            return fig
