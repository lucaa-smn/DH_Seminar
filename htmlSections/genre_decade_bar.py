import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px


class GenreDecadeAnalysis:
    def __init__(self, app: dash.Dash, data: pd.DataFrame) -> None:
        self.app = app
        self.data = data

        # Explode genres into individual rows
        self.data["genres"] = self.data["genres"].str.split(", ")
        self.exploded_data = self.data.explode("genres").dropna(subset=["genres"])

        # Precompute the single most popular genre per decade
        self.most_popular_genres = (
            self.exploded_data.groupby(["decade", "genres"])
            .size()
            .reset_index(name="film_count")
            .sort_values(["decade", "film_count"], ascending=[True, False])
            .groupby("decade")
            .first()
            .reset_index()
        )

        # Create Dash layout
        self.div = html.Div(
            [
                html.H1("Genre Analysis Over Decades", style={"textAlign": "center"}),
                dcc.Graph(id="most-popular-genre-chart"),
                html.H3("Select a Decade to View Genre Distribution"),
                dcc.Dropdown(
                    id="decade-dropdown",
                    options=[
                        {"label": str(decade), "value": decade}
                        for decade in sorted(self.data["decade"].unique())
                    ],
                    value=sorted(self.data["decade"].unique())[0],
                ),
                dcc.Graph(id="genre-distribution-chart"),
            ]
        )

        # Register callbacks
        self.register_callbacks()

    def get_html(self) -> html.Div:
        return self.div

    def register_callbacks(self):
        @self.app.callback(
            Output("most-popular-genre-chart", "figure"),
            Input("decade-dropdown", "value"),
        )
        def update_most_popular_chart(selected_decade):
            fig = px.bar(
                self.most_popular_genres,
                x="decade",
                y="film_count",
                color="genres",
                title="Biggest Genre per Decade",
                labels={"film_count": "Number of Films", "genres": "Genre"},
            )
            fig.update_layout(
                xaxis_title="Decade",
                yaxis_title="Number of Films",
                xaxis=dict(categoryorder="total ascending"),
            )
            return fig

        @self.app.callback(
            Output("genre-distribution-chart", "figure"),
            Input("decade-dropdown", "value"),
        )
        def update_genre_distribution_chart(selected_decade):
            # Filter data for the selected decade
            decade_data = self.exploded_data[
                self.exploded_data["decade"] == selected_decade
            ]

            # Group and count genres
            genre_counts = (
                decade_data.groupby("genres")
                .size()
                .reset_index(name="film_count")
                .sort_values(by="film_count", ascending=False)
            )

            fig = px.bar(
                genre_counts,
                x="genres",
                y="film_count",
                title=f"Genre Distribution in {selected_decade}",
                labels={"genres": "Genre", "film_count": "Number of Films"},
            )
            fig.update_layout(
                xaxis_title="Genre",
                yaxis_title="Number of Films",
                xaxis=dict(categoryorder="total descending"),
            )
            return fig
