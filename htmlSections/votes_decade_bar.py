import dash
import pandas as pd
from dash import dcc, html
import plotly.express as px
from htmlSections.section import Section


class VotesDecadeBar(Section):

    def __init__(self, app: dash.Dash, data: pd.DataFrame) -> None:

        self.app: dash.Dash = app
        self.data: pd.DataFrame = data

        self.decade_counts = (
            self.data["decade"].value_counts().sort_index().reset_index()
        )
        self.decade_counts.columns = ["decade", "film_count"]

        self.vote_counts_by_decade = (
            self.data.groupby("decade")["vote_count"].sum().reset_index()
        )

        self.vote_chart = px.bar(
            self.vote_counts_by_decade,
            x="decade",
            y="vote_count",
            labels={"decade": "Decade", "vote_count": "Total Votes"},
            text="vote_count",
        )
        self.vote_chart.update_traces(textposition="outside")
        self.vote_chart.update_layout(xaxis_title="Decade", yaxis_title="Total Votes")

        self.div = dash.html.Div(
            [
                dash.html.H1(
                    "Anzahl der Votes die insgesamt in einer Decade abgegeben wurden"
                ),
                dash.dcc.Graph(figure=self.vote_chart),
            ]
        )

        self.register_callbacks()

    def get_html(self) -> dash.html.Div:

        return self.div

    def register_callbacks(self):
        return super().register_callbacks()
