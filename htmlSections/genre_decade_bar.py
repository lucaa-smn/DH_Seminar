import pandas as pd
import dash
from dash import dcc, html
import plotly.express as px
from htmlSections.section import Section


class GenreDecadeBar(Section):
    def __init__(self, app: dash.Dash, data: pd.DataFrame) -> None:

        self.app: dash.Dash = app
        self.data: pd.DataFrame = data

        # Expand the genres into multiple rows
        genres_data = (
            self.data.assign(genres=self.data["genres"].str.split(","))
            .explode("genres")
            .dropna(subset=["genres"])
        )

        # Group by decade and genre to count the number of films
        self.genre_decade_counts = (
            genres_data.groupby(["decade", "genres"])
            .size()
            .reset_index(name="film_count")
        )

        # Create a bar chart using Plotly Express
        self.bar_chart = px.bar(
            self.genre_decade_counts,
            x="decade",
            y="film_count",
            color="genres",
            title="Most Popular Genres over Time",
            labels={
                "decade": "Decade",
                "film_count": "Number of Films",
                "genres": "Genre",
            },
        )
        self.bar_chart.update_layout(
            xaxis_title="Decade",
            yaxis_title="Number of Films",
            barmode="stack",
        )

        # Create the HTML structure
        self.div = html.Div(
            [
                html.H1("Most Popular Genres Over Time", style={"textAlign": "center"}),
                dcc.Graph(figure=self.bar_chart),
            ]
        )

        self.register_callbacks()

    def get_html(self) -> html.Div:
        return self.div

    def register_callbacks(self):
        pass
