import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
from pandas.api.types import is_numeric_dtype
from htmlSections.section import Section


class Statistical_Evaluation(Section):

    def __init__(self, app: dash.Dash, data: pd.DataFrame) -> None:
        self.app: dash.Dash = app
        self.data: pd.DataFrame = data.copy()

        # Identify numeric columns
        self.numeric_columns = [
            col for col in self.data.columns if is_numeric_dtype(self.data[col])
        ]
        columns_to_exclude = ["id", "decade", "adult"]
        self.numeric_columns = [
            col for col in self.numeric_columns if col not in columns_to_exclude
        ]

        self.div = html.Div(
            [
                html.H1("Statistische Auswertung", style={"textAlign": "center"}),
                html.Label("Wählen Sie ein Attribut zur Analyse:"),
                dcc.Dropdown(
                    id="stat-attribute-dropdown",
                    options=[
                        {"label": col, "value": col} for col in self.numeric_columns
                    ],
                    value=self.numeric_columns[0] if self.numeric_columns else None,
                ),
                html.Div(id="statistical-summary"),
            ]
        )

        self.register_callbacks()

    def get_html(self) -> html.Div:
        return self.div

    def register_callbacks(self):
        @self.app.callback(
            Output("statistical-summary", "children"),
            Input("stat-attribute-dropdown", "value"),
        )
        def update_statistical_analysis(attribute: str):
            if not attribute:
                return html.P("Bitte wählen Sie ein Attribut.")

            # Compute summary statistics
            summary_stats = self.data[attribute].describe()

            # Create summary output
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

            return ((stats_div),)
