import dash
import pandas as pd
import plotly.express as px
from dash import dcc, html
from dash.dependencies import Input, Output
from pandas.api.types import is_numeric_dtype


class ItemDistribution:

    def __init__(self, app: dash.Dash, data: pd.DataFrame) -> None:
        self.app: dash.Dash = app
        self.data: pd.DataFrame = data.copy()

        self.numeric_columns = [
            col for col in self.data.columns if is_numeric_dtype(self.data[col])
        ]

        columns_to_exclude = ["id", "decade"]
        self.numeric_columns = [
            col for col in self.numeric_columns if col not in columns_to_exclude
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
                html.Div(
                    [
                        html.Label("Budget Threshold:"),
                        dcc.Input(
                            id="budget-threshold-input",
                            type="number",
                            value=0,
                            debounce=True,
                        ),
                        html.Br(),
                        html.Label("Revenue Threshold:"),
                        dcc.Input(
                            id="revenue-threshold-input",
                            type="number",
                            value=0,
                            debounce=True,
                        ),
                    ]
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
            [
                Input("attribute-dropdown", "value"),
                Input("budget-threshold-input", "value"),
                Input("revenue-threshold-input", "value"),
            ],
        )
        def update_histogram(
            attribute: str,
            runtime_filter: str,
            budget_threshold: float,
            revenue_threshold: float,
        ) -> px.histogram:
            if not attribute:
                return px.histogram()

            filtered_data = self.data.copy()

            filtered_data = filter_budget_revenue(
                filtered_data, budget_threshold, revenue_threshold
            )

            fig = px.histogram(
                filtered_data,
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

        def filter_budget_revenue(
            data: pd.DataFrame, budget_threshold: float, revenue_threshold: float
        ) -> pd.DataFrame:
            filtered_data = data[data["budget"] >= budget_threshold]

            filtered_data = filtered_data[filtered_data["revenue"] >= revenue_threshold]

            return filtered_data
