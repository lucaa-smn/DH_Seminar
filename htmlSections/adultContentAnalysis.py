import dash
import pandas as pd
from dash import html, dcc
import plotly.express as px
from dash.dependencies import Input, Output
from htmlSections.section import Section


class AdultContentAnalysis(Section):
    def __init__(self, app: dash.Dash, data: pd.DataFrame) -> None:
        self.app = app
        self.data = data.copy()

        # Ensure 'adult' column is treated as a boolean
        self.data["adult"] = self.data["adult"].astype(bool)

        # Layout with dropdown and toggle filter
        self.div = html.Div(
            [
                html.H1("Adult Content and Average  Revenue / Vote Average Analysis"),
                # Dropdown for metric selection
                html.Label("Select Metric:"),
                dcc.Dropdown(
                    id="metric-dropdown-adult",
                    options=[
                        {"label": "Average Revenue", "value": "revenue"},
                        {"label": "Vote Average", "value": "vote_average"},
                    ],
                    value="revenue",  # Default selection
                ),
                # Checkbox to filter low vote count movies
                dcc.Checklist(
                    id="vote-filter-toggle-adult",
                    options=[
                        {"label": "Exclude movies with ≤5 votes", "value": "filter"}
                    ],
                    value=[],  # Default: No filtering
                    inline=True,
                ),
                # Graph
                dcc.Graph(id="adult-content-bar-chart"),
            ]
        )

        self.register_callbacks()

    def get_html(self) -> html.Div:
        return self.div

    def register_callbacks(self):
        @self.app.callback(
            Output("adult-content-bar-chart", "figure"),
            [
                Input("metric-dropdown-adult", "value"),
                Input("vote-filter-toggle-adult", "value"),
            ],
        )
        def update_chart(selected_metric, vote_filter):
            """Update the bar chart based on the selected metric and filtering option."""
            data = self.data.copy()
            apply_filter = "filter" in vote_filter

            if apply_filter:
                data = data[data["vote_count"] > 5]

            # Group by 'adult' column and calculate mean for the selected metric
            grouped_data = data.groupby("adult")[selected_metric].mean().reset_index()

            # Convert boolean values to labels
            grouped_data["adult"] = grouped_data["adult"].replace(
                {True: "Adult", False: "Non-Adult"}
            )

            # Create bar chart
            fig = px.bar(
                grouped_data,
                x="adult",
                y=selected_metric,
                color="adult",
                title=f"Comparison of Adult and Non-Adult Movies by {selected_metric.capitalize()}",
                labels={
                    "adult": "Movie Type",
                    selected_metric: selected_metric.capitalize(),
                },
            )

            fig.update_layout(
                xaxis_title="Movie Type",
                yaxis_title=selected_metric.capitalize(),
            )

            return fig
