import dash
import pandas as pd
from dash import html, dcc, callback, Input, Output
import plotly.express as px
from htmlSections.section import Section


class PopularityCorrelationScatter(Section):
    def __init__(self, app: dash.Dash, data: pd.DataFrame) -> None:
        self.app: dash.Dash = app
        self.data: pd.DataFrame = data

        # Filter out rows where budget or revenue is zero (to avoid misleading points)
        self.filtered_data = self.data.copy()
        # data[(data["budget"] > 0) & (data["revenue"] > 0)]

        # Initial scatter plot
        self.scatter_fig = self.create_figure(self.filtered_data, "popularity")

        self.div = html.Div(
            [
                html.H1("Budget Correlation Analysis"),
                dcc.Dropdown(
                    id="attribute-selector-popularity",
                    options=[
                        {"label": "Revenue", "value": "revenue"},
                        {"label": "Vote Average", "value": "vote_average"},
                    ],
                    value="revenue",
                    clearable=False,
                    style={"width": "50%"},
                ),
                dcc.Graph(id="popularity-attribute-graph", figure=self.scatter_fig),
            ]
        )

        self.register_callbacks()

    def get_html(self) -> html.Div:
        return self.div

    def register_callbacks(self):
        @self.app.callback(
            Output("popularity-attribute-graph", "figure"),
            Input("attribute-selector-popularity", "value"),
        )
        def update_graph(selected_attribute):
            return self.create_figure(self.filtered_data, selected_attribute)

    def create_figure(self, data, y_attribute):
        fig = px.scatter(
            data,
            x="popularity",
            y=y_attribute,
            hover_data=["title", "vote_average", "popularity", "revenue"],
            labels={
                "popularity": "Popularity",
                y_attribute: y_attribute.replace("_", " ").title(),
            },
            title=f"Popularität vs. {y_attribute.replace('_', ' ').title()} Correlation",
        )
        fig.update_traces(marker=dict(size=8, opacity=0.7))
        fig.update_layout(xaxis_type="log", yaxis_type="log")
        return fig
