import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px


class GenreVoteAverageOverDecades:
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

        self.genre_vote_average = (
            self.exploded_data.groupby(["decade", "genres"])["vote_average"]
            .mean()
            .reset_index(name="average_vote")
        )

        self.div = html.Div(
            [
                html.H1(
                    "Average Vote Score of Genres Over Decades",
                    style={"textAlign": "center"},
                ),
                html.H3("Select a Genre to View Rating Trends"),
                dcc.Dropdown(
                    id="genre-dropdown-vote-average",
                    options=[
                        {"label": genre, "value": genre}
                        for genre in sorted(self.genre_vote_average["genres"].unique())
                    ],
                    value=sorted(self.genre_vote_average["genres"].unique())[0],
                ),
                dcc.Graph(id="genre-vote-trend-chart"),
            ]
        )

        self.register_callbacks()

    def get_html(self) -> html.Div:
        return self.div

    def register_callbacks(self):

        @self.app.callback(
            Output("genre-vote-trend-chart", "figure"),
            Input("genre-dropdown-vote-average", "value"),
        )
        def update_genre_vote_trend_chart(selected_genre):
            # Filter data for the selected genre
            filtered_votes = self.genre_vote_average[
                self.genre_vote_average["genres"] == selected_genre
            ]

            fig = px.bar(
                filtered_votes,
                x="decade",
                y="average_vote",
                color="average_vote",
                title=f"Average Vote Score for {selected_genre} Over Decades",
                labels={"decade": "Decade", "average_vote": "Average Vote Score"},
                text="average_vote",
            )
            fig.update_traces(texttemplate="%{text:.2f}")
            fig.update_layout(
                xaxis_title="Decade",
                yaxis_title="Average Vote Score",
                xaxis=dict(type="category"),
                coloraxis_colorbar=dict(title="Average Vote Score"),
            )
            return fig
