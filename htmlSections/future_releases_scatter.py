import dash
import pandas as pd
from dash import html, dcc
import plotly.express as px
from htmlSections.section import Section


class FutureReleasesScatter(Section):

    def __init__(self, app: dash.Dash, data: pd.DataFrame) -> None:

        self.app: dash.Dash = app
        self.data: pd.DataFrame = data

        self.future_movies = data[data["release_date"] > pd.Timestamp("2024-12-31")]

        self.table_fig = px.scatter(
            self.future_movies,
            x="release_date",
            y="title",
            hover_data=["vote_average", "popularity", "budget"],
            labels={"release_date": "Release Date", "title": "Movie Title"},
        )
        self.table_fig.update_traces(marker=dict(size=10), mode="markers+text")

        self.div = dash.html.Div(
            [
                dash.html.H1("Zuküntige Filmveröffentlichungen"),
                dash.dcc.Graph(figure=self.table_fig),
            ]
        )

        self.register_callbacks()

    def get_html(self) -> dash.html.Div:

        return self.div

    def register_callbacks(self):
        return super().register_callbacks()
