import dash
import pandas as pd
from dash import html, dcc
import plotly.express as px
from dash.dependencies import Input, Output
from htmlSections.section import Section


class RuntimePopularityRevenue(Section):
    def __init__(self, app: dash.Dash, data: pd.DataFrame) -> None:
        self.app = app
        self.data = data

        # Clean and filter data
        self.filtered_data = self.remove_outliers(self.data)

        # Initial scatter plot (default: runtime vs popularity)
        self.scatter_fig = self.create_scatter_figure(
            self.filtered_data, "popularity", False
        )

        # Layout with dropdown and filter button
        self.div = html.Div(
            [
                html.H1("Runtime vs. Popularity/Revenue Analysis"),
                # Dropdown for metric selection
                html.Label("Select Metric:"),
                dcc.Dropdown(
                    id="metric-dropdown",
                    options=[
                        {"label": "Popularity", "value": "popularity"},
                        {"label": "Revenue", "value": "revenue"},
                    ],
                    value="popularity",  # Default selection
                ),
                # Button to filter movies with vote_count <= 5
                dcc.Checklist(
                    id="vote-filter-toggle",
                    options=[
                        {"label": "Exclude movies with ≤5 votes", "value": "filter"}
                    ],
                    value=[],  # Default: No filtering
                    inline=True,
                ),
                # Graph
                dcc.Graph(id="runtime-scatter-graph", figure=self.scatter_fig),
            ]
        )

        self.register_callbacks()

    def get_html(self) -> html.Div:
        return self.div

    def register_callbacks(self):
        @self.app.callback(
            Output("runtime-scatter-graph", "figure"),
            [Input("metric-dropdown", "value"), Input("vote-filter-toggle", "value")],
        )
        def update_scatter(selected_metric, vote_filter):
            """Update scatter plot based on selected metric and vote count filter."""
            apply_filter = "filter" in vote_filter
            return self.create_scatter_figure(
                self.filtered_data, selected_metric, apply_filter
            )

    def remove_outliers(self, data: pd.DataFrame) -> pd.DataFrame:
        """Removes extreme outliers for better visualization."""
        lower_quantile = 0.01
        upper_quantile = 0.99

        # Define quantile thresholds
        runtime_lower = data["runtime"].quantile(lower_quantile)
        runtime_upper = data["runtime"].quantile(upper_quantile)

        pop_lower = data["popularity"].quantile(lower_quantile)
        pop_upper = data["popularity"].quantile(upper_quantile)

        rev_lower = data["revenue"].quantile(lower_quantile)
        rev_upper = data["revenue"].quantile(upper_quantile)

        # Filter data within quantile ranges
        filtered_data = data[
            (data["runtime"] >= runtime_lower)
            & (data["runtime"] <= runtime_upper)
            & (data["popularity"] >= pop_lower)
            & (data["popularity"] <= pop_upper)
            & (data["revenue"] >= rev_lower)
            & (data["revenue"] <= rev_upper)
        ]

        return filtered_data

    def create_scatter_figure(
        self, data: pd.DataFrame, metric: str, filter_votes: bool
    ):
        """Generates scatter plot based on selected metric (popularity or revenue)."""
        if filter_votes:
            data = data[data["vote_count"] > 5]

        fig = px.scatter(
            data,
            x="runtime",
            y=metric,
            hover_data=["title", "release_date", "vote_average", "vote_count"],
            labels={"runtime": "Runtime (minutes)", metric: metric.capitalize()},
            title=f"Runtime vs. {metric.capitalize()}",
        )

        fig.update_traces(marker=dict(size=8, opacity=0.7))
        fig.update_layout(
            xaxis_title="Runtime (minutes)",
            yaxis_title=metric.capitalize(),
        )

        return fig
