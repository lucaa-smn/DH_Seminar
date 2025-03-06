import dash
import pandas as pd
import plotly.express as px
from dash import dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
from pandas.api.types import is_numeric_dtype


class ItemAnalysis:
    def __init__(self, app: dash.Dash, data: pd.DataFrame) -> None:
        self.app: dash.Dash = app
        self.data: pd.DataFrame = data.copy()

        # Filtering numeric columns
        self.numeric_columns = [
            col for col in self.data.columns if is_numeric_dtype(self.data[col])
        ]
        columns_to_exclude = ["id", "decade", "adult"]
        self.numeric_columns = [
            col for col in self.numeric_columns if col not in columns_to_exclude
        ]

        self.div = html.Div(
            [
                # Title
                html.H1(
                    "Item Analysis", style={"textAlign": "center", "color": "#333"}
                ),
                # Dropdown for selecting attribute
                html.Label("Select Attribute for Analysis:"),
                dcc.Dropdown(
                    id="attribute-dropdown",
                    options=[
                        {"label": col, "value": col} for col in self.numeric_columns
                    ],
                    value=self.numeric_columns[0] if self.numeric_columns else None,
                    style={"width": "100%", "margin-bottom": "20px"},
                ),
                # Runtime Filter Section
                html.Div(
                    [
                        html.Label("Runtime Outlier Filter:"),
                        dcc.RadioItems(
                            id="runtime-filter-radio",
                            options=[
                                {"label": "Filter Runtime Outliers", "value": "filter"},
                                {"label": "No Filter", "value": "no_filter"},
                            ],
                            value="no_filter",
                            labelStyle={
                                "display": "inline-block",
                                "margin-right": "20px",
                            },
                        ),
                    ],
                    style={"margin-bottom": "20px"},
                ),
                # Budget and Revenue Thresholds
                html.Div(
                    [
                        dbc.Row(
                            [
                                dbc.Col(html.Label("Budget Threshold:"), width=4),
                                dbc.Col(
                                    dcc.Input(
                                        id="budget-threshold-input",
                                        type="number",
                                        value=0,
                                        debounce=True,
                                        style={"width": "100%"},
                                    ),
                                    width=8,
                                ),
                            ],
                            style={"margin-bottom": "15px"},
                        ),
                        dbc.Row(
                            [
                                dbc.Col(html.Label("Revenue Threshold:"), width=4),
                                dbc.Col(
                                    dcc.Input(
                                        id="revenue-threshold-input",
                                        type="number",
                                        value=0,
                                        debounce=True,
                                        style={"width": "100%"},
                                    ),
                                    width=8,
                                ),
                            ],
                            style={"margin-bottom": "30px"},
                        ),
                    ]
                ),
                # Statistical Summary
                html.Div(id="statistical-summary2", style={"margin-bottom": "30px"}),
                # Histogram Graph
                dcc.Graph(id="histogram"),
            ],
            style={"padding": "20px"},
        )

        # Registering the callbacks
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
                return (
                    html.P("Please select an attribute for analysis."),
                    px.histogram(),
                )

            # Filter data based on user input
            filtered_data = self.data.copy()

            # Filter out runtime outliers if selected
            if runtime_filter == "filter" and attribute == "runtime":
                filtered_data = self.filter_outliers(filtered_data, "runtime")

            # Apply budget and revenue thresholds
            filtered_data = self.filter_budget_revenue(
                filtered_data, budget_threshold, revenue_threshold
            )

            # Generate summary stats
            summary_stats = filtered_data[attribute].describe()

            stats_div = html.Div(
                [
                    html.H3(f"Statistical Summary for {attribute}"),
                    html.P(f"👤 Count: {summary_stats['count']:.0f}"),
                    html.P(f"📊 Mean: {summary_stats['mean']:.2f}"),
                    html.P(f"🔸 Median: {summary_stats['50%']:.2f}"),
                    html.P(f"📉 Min: {summary_stats['min']:.2f}"),
                    html.P(f"📈 Max: {summary_stats['max']:.2f}"),
                    html.P(f"📏 Std Dev: {summary_stats['std']:.2f}"),
                ],
                style={
                    "border": "1px solid #ccc",
                    "padding": "15px",
                    "border-radius": "5px",
                },
            )

            # Create histogram
            histogram = px.histogram(
                filtered_data,
                x=attribute,
                title=f"Histogram of {attribute}",
                nbins=20,
                labels={attribute: "Value", "count": "Frequency"},
                template="plotly_dark",  # Use a dark theme for plotly
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

        # Calculate IQR for outlier detection
        Q1 = data[column].quantile(0.25)
        Q3 = data[column].quantile(0.75)
        IQR = Q3 - Q1

        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR

        return data[(data[column] >= lower_bound) & (data[column] <= upper_bound)]
