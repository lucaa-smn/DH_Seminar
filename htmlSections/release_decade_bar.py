import pandas as pd
import dash
from dash import dcc, html
import plotly.express as px
from htmlSections.section import Section


class ReleaseDecadeBar(Section):

    def __init__(self, app: dash.Dash, data: pd.DataFrame) -> None:

        self.app: dash.Dash = app
        self.data: pd.DataFrame = data

        self.decade_counts = (
            self.data["decade"].value_counts().sort_index().reset_index()
        )
        self.decade_counts.columns = ["decade", "film_count"]

        self.bar_chart = px.bar(
            self.decade_counts,
            x="decade",
            y="film_count",
            labels={"decade": "Decade", "film_count": "Number of Films"},
            text="film_count",
        )
        self.bar_chart.update_traces(textposition="outside")
        self.bar_chart.update_layout(
            xaxis_title="Decade", yaxis_title="Number of Films"
        )

        self.div = dash.html.Div(
            [
                dash.html.H1("Veröffentlichte Filme per Decade"),
                dash.dcc.Graph(figure=self.bar_chart),
            ]
        )

        self.register_callbacks()

    def get_html(self) -> dash.html.Div:

        return self.div

    def register_callbacks(self):
        return super().register_callbacks()
