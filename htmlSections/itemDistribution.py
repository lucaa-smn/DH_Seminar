import dash
import pandas as pd
import plotly.express as px
from dash import dcc, html
from dash.dependencies import Input, Output
from pandas.api.types import is_numeric_dtype


class ItemDistribution:

    def __init__(self, app: dash.Dash, data: pd.DataFrame) -> None:
        self.app: dash.Dash = app
        self.data: pd.DataFrame = data

        self.numeric_columns = [
            col for col in self.data.columns if is_numeric_dtype(self.data[col])
        ]

        self.div = html.Div(
            [
                html.H1("Verteilung der Items", style={"textAlign": "center"}),
                html.Label("Wählen Sie ein Attribut zur Visualisierung:"),
                dcc.Dropdown(
                    id="attribute-dropdown",
                    options=[
                        {"label": col, "value": col} for col in self.numeric_columns
                    ],
                    value=self.numeric_columns[0] if self.numeric_columns else None,
                ),
                dcc.Graph(id="item-histogram-plot"),
            ]
        )

        self.register_callbacks()

    def get_html(self) -> html.Div:
        return self.div

    def register_callbacks(self) -> None:
        @self.app.callback(
            Output("item-histogram-plot", "figure"),
            Input("attribute-dropdown", "value"),
        )
        def update_histogram(attribute: str) -> px.histogram:
            if not attribute:
                return px.histogram()

            fig = px.histogram(
                self.data,
                x=attribute,
                title=f"Verteilung von {attribute}",
                labels={attribute: "Wert", "count": "Häufigkeit"},
                nbins=20,
            )
            fig.update_layout(
                xaxis_title=attribute,
                yaxis_title="Häufigkeit",
                template="plotly_white",
            )
            return fig
