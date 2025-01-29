import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px


class GenrePopularityOverDecades:
    def __init__(self, app: dash.Dash, data: pd.DataFrame) -> None:
        self.app = app

        self.data = data.copy()

        self.data["release_date"] = pd.to_datetime(
            self.data["release_date"], errors="coerce"
        )

        self.data = self.data[self.data["release_date"].dt.year < 2025]

        self.data["decade"] = (self.data["release_date"].dt.year // 10) * 10

        self.data["genres"] = self.data["genres"].str.split(", ")
        self.exploded_data = self.data.explode("genres").dropna(subset=["genres"])

        # Calculate average popularity per genre per decade
        self.genre_popularity = (
            self.exploded_data.groupby(["decade", "genres"])["popularity"]
            .mean()
            .reset_index(name="average_popularity")
        )

        self.div = html.Div(
            [
                html.H1(
                    "Genre Popularity Across Decades", style={"textAlign": "center"}
                ),
                html.H3("Select a Decade to View Genre Ranking"),
                dcc.Dropdown(
                    id="decade-dropdown-genre-popularity",
                    options=[
                        {"label": str(decade), "value": decade}
                        for decade in sorted(self.genre_popularity["decade"].unique())
                    ],
                    value=sorted(self.genre_popularity["decade"].unique())[0],
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
            filtered_popularity = self.genre_popularity[
                self.genre_popularity["decade"] == selected_decade
            ]

            fig = px.bar(
                filtered_popularity,
                x="genres",
                y="average_popularity",
                color="average_popularity",
                title=f"Genre Ranking in {selected_decade}",
                labels={"genres": "Genre", "average_popularity": "Average Popularity"},
                text="average_popularity",
            )
            fig.update_traces(texttemplate="%{text:.2f}")
            fig.update_layout(
                xaxis_title="Genre",
                yaxis_title="Average Popularity",
                xaxis=dict(categoryorder="total descending"),
                coloraxis_colorbar=dict(title="Average Popularity"),
            )
            return fig
