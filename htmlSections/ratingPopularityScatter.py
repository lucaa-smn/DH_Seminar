import dash
import pandas as pd
from dash import html, dcc
import plotly.express as px
from dash.dependencies import Input, Output
from htmlSections.section import Section


class RatingPopularityScatter(Section):
    def __init__(self, app: dash.Dash, data: pd.DataFrame) -> None:
        self.app: dash.Dash = app
        self.data: pd.DataFrame = data

        # Handle outliers: Filter data based on percentiles for vote_average and popularity
        self.filtered_data = self.remove_outliers(data)

        # Initial scatter plot
        self.scatter_fig = self.create_scatter_figure(self.filtered_data)

        # Create layout for Dash app
        self.div = html.Div(
            [
                html.H1("Rating vs. Popularity Analysis"),
                dcc.Graph(id="scatter-graph", figure=self.scatter_fig),
            ]
        )

        self.register_callbacks()

    def get_html(self) -> html.Div:
        return self.div

    def register_callbacks(self):
        return super().register_callbacks()

    def remove_outliers(self, data: pd.DataFrame) -> pd.DataFrame:
        """Remove outliers based on percentile filtering."""
        lower_percentile = 0.01
        upper_percentile = 0.99

        vote_avg_lower = data["vote_average"].quantile(lower_percentile)
        vote_avg_upper = data["vote_average"].quantile(upper_percentile)

        popularity_lower = data["popularity"].quantile(lower_percentile)
        popularity_upper = data["popularity"].quantile(upper_percentile)

        # Filter based on percentile thresholds
        filtered_data = data[
            (data["vote_average"] >= vote_avg_lower)
            & (data["vote_average"] <= vote_avg_upper)
            & (data["popularity"] >= popularity_lower)
            & (data["popularity"] <= popularity_upper)
        ]

        return filtered_data

    def create_scatter_figure(self, data: pd.DataFrame):
        """Generate scatter plot figure."""
        fig = px.scatter(
            data,
            x="vote_average",
            y="popularity",
            hover_data=["title", "vote_count", "release_date"],
            labels={"vote_average": "Vote Average", "popularity": "Popularity"},
            title="Correlation Between Movie Ratings and Popularity",
        )

        fig.update_traces(marker=dict(size=8, opacity=0.7))
        fig.update_layout(
            xaxis_title="Vote Average",
            yaxis_title="Popularity",
        )

        return fig
