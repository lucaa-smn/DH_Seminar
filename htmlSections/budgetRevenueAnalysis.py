import dash
import pandas as pd
from dash import html, dcc, callback, Input, Output
import plotly.express as px
from htmlSections.section import Section


class BudgetRevenueScatter(Section):
    def __init__(self, app: dash.Dash, data: pd.DataFrame) -> None:
        self.app: dash.Dash = app
        self.data: pd.DataFrame = data

        # Filter out rows where budget or revenue is zero (to avoid misleading points)
        self.filtered_data = data[(data["budget"] > 0) & (data["revenue"] > 0)]

        # Initial scatter plot
        self.scatter_fig = self.create_figure(self.filtered_data)

        self.div = html.Div(
            [
                html.H1("Budget vs. Revenue Analysis"),
                html.Button(
                    "Toggle Popularity Filter", id="popularity-filter-btn", n_clicks=0
                ),
                dcc.Graph(id="budget-revenue-graph", figure=self.scatter_fig),
            ]
        )

        self.register_callbacks()

    def get_html(self) -> html.Div:
        return self.div

    def register_callbacks(self):
        @self.app.callback(
            Output("budget-revenue-graph", "figure"),
            Input("popularity-filter-btn", "n_clicks"),
        )
        def update_graph(n_clicks):
            if n_clicks % 2 == 1:
                filtered_df = self.filtered_data[self.filtered_data["popularity"] >= 1]
            else:
                filtered_df = self.filtered_data

            return self.create_figure(filtered_df)

    def create_figure(self, data):
        fig = px.scatter(
            data,
            x="budget",
            y="revenue",
            hover_data=["title", "vote_average", "popularity"],
            labels={"budget": "Budget (USD)", "revenue": "Revenue (USD)"},
            title="Budget vs. Revenue Correlation",
        )
        fig.update_traces(marker=dict(size=8, opacity=0.7))
        fig.update_layout(xaxis_type="log", yaxis_type="log")
        return fig
