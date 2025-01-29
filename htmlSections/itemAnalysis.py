import dash
import pandas as pd
import plotly.express as px
from dash import dcc, html
from dash.dependencies import Input, Output
from pandas.api.types import is_numeric_dtype


class ItemAnalysis:
    def __init__(self, app: dash.Dash, data: pd.DataFrame) -> None:
        self.app: dash.Dash = app
        self.data: pd.DataFrame = data.copy()

        self.numeric_columns = [
            col for col in self.data.columns if is_numeric_dtype(self.data[col])
        ]

        columns_to_exclude = ["id", "decade", "adult"]
        self.numeric_columns = [
            col for col in self.numeric_columns if col not in columns_to_exclude
        ]

        self.div = html.Div(
            [
                html.H1("Item Analyse", style={"textAlign": "center"}),
                html.Label("Wählen Sie ein Attribut zur Analyse:"),
                dcc.Dropdown(
                    id="attribute-dropdown",
                    options=[
                        {"label": col, "value": col} for col in self.numeric_columns
                    ],
                    value=self.numeric_columns[0] if self.numeric_columns else None,
                ),
                html.Div(
                    [
                        html.Label("Runtime Outlier-Filter:"),
                        dcc.RadioItems(
                            id="runtime-filter-radio",
                            options=[
                                {"label": "Filter Runtime Outliers", "value": "filter"},
                                {"label": "No Filter", "value": "no_filter"},
                            ],
                            value="no_filter",
                            labelStyle={"display": "inline-block"},
                        ),
                    ]
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
                html.Div(id="statistical-summary2"),
                dcc.Graph(id="histogram"),
            ]
        )

        self.register_callbacks()

    def get_html(self) -> html.Div:
        return self.div

    def register_callbacks(self) -> None:
        @self.app.callback(
            [
                Output("statistical-summary2", "children"),
                Output("histogram", "figure"),
            ],
            [
                Input("attribute-dropdown", "value"),
                Input("runtime-filter-radio", "value"),
                Input("budget-threshold-input", "value"),
                Input("revenue-threshold-input", "value"),
            ],
        )
        def update_analysis(
            attribute, runtime_filter, budget_threshold, revenue_threshold
        ):
            if not attribute:
                return html.P("Bitte wählen Sie ein Attribut."), px.histogram()

            filtered_data = self.data.copy()

            if runtime_filter == "filter" and attribute == "runtime":
                filtered_data = self.filter_outliers(filtered_data, "runtime")

            filtered_data = self.filter_budget_revenue(
                filtered_data, budget_threshold, revenue_threshold
            )

            summary_stats = filtered_data[attribute].describe()

            stats_div = html.Div(
                [
                    html.H3(f"Statistische Kennzahlen für {attribute}"),
                    html.P(f"👤 Anzahl: {summary_stats['count']:.0f}"),
                    html.P(f"📊 Mittelwert: {summary_stats['mean']:.2f}"),
                    html.P(f"🔸 Median: {summary_stats['50%']:.2f}"),
                    html.P(f"📉 Minimum: {summary_stats['min']:.2f}"),
                    html.P(f"📈 Maximum: {summary_stats['max']:.2f}"),
                    html.P(f"📏 Standardabweichung: {summary_stats['std']:.2f}"),
                ]
            )

            histogram = px.histogram(
                filtered_data,
                x=attribute,
                title=f"Histogramm von {attribute}",
                nbins=20,
                labels={attribute: "Wert", "count": "Häufigkeit"},
            )

            return stats_div, histogram

    def filter_budget_revenue(
        self, data: pd.DataFrame, budget_threshold: float, revenue_threshold: float
    ) -> pd.DataFrame:
        if "budget" in data.columns and budget_threshold:
            data = data[data["budget"] >= budget_threshold]

        if "revenue" in data.columns and revenue_threshold:
            data = data[data["revenue"] >= revenue_threshold]

        return data

    def filter_outliers(self, data: pd.DataFrame, column: str) -> pd.DataFrame:
        if column not in data.columns or not is_numeric_dtype(data[column]):
            return data

        Q1 = data[column].quantile(0.25)
        Q3 = data[column].quantile(0.75)
        IQR = Q3 - Q1

        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR

        return data[(data[column] >= lower_bound) & (data[column] <= upper_bound)]
