import dash
import pandas as pd
from dash import html, dcc, callback, Input, Output
import plotly.express as px
from htmlSections.section import Section


class AttributeCorrelationScatter(Section):
    def __init__(self, app: dash.Dash, data: pd.DataFrame) -> None:
        self.app: dash.Dash = app
        self.data: pd.DataFrame = data

        # Initial scatter plot
        self.scatter_fig = self.create_figure(self.data, "budget", "revenue")

        self.div = html.Div(
            [
                html.H1("Attribute Correlation Analysis"),
                html.Label("Select X-Axis Attribute:"),
                dcc.Dropdown(
                    id="x-attribute-selector",
                    options=[
                        {"label": "Revenue", "value": "revenue"},
                        {"label": "Budget", "value": "budget"},
                        {"label": "Popularity", "value": "popularity"},
                        {"label": "Vote Count", "value": "vote_count"},
                        {"label": "Vote Average", "value": "vote_average"},
                        {"label": "Runtime", "value": "runtime"},
                    ],
                    value="budget",
                    clearable=False,
                    style={"width": "50%"},
                ),
                html.Label("Select Y-Axis Attribute:"),
                dcc.Dropdown(
                    id="y-attribute-selector",
                    options=[
                        {"label": "Revenue", "value": "revenue"},
                        {"label": "Budget", "value": "budget"},
                        {"label": "Popularity", "value": "popularity"},
                        {"label": "Vote Count", "value": "vote_count"},
                        {"label": "Vote Average", "value": "vote_average"},
                        {"label": "Runtime", "value": "runtime"},
                    ],
                    value="revenue",
                    clearable=False,
                    style={"width": "50%"},
                ),
                dcc.Graph(id="attribute-scatter-graph", figure=self.scatter_fig),
            ]
        )

        self.register_callbacks()

    def get_html(self) -> html.Div:
        return self.div

    def register_callbacks(self):
        @self.app.callback(
            Output("attribute-scatter-graph", "figure"),
            Input("x-attribute-selector", "value"),
            Input("y-attribute-selector", "value"),
        )
        def update_graph(x_attribute, y_attribute):
            return self.create_figure(self.data, x_attribute, y_attribute)

    def create_figure(self, data, x_attribute, y_attribute):
        fig = px.scatter(
            data,
            x=x_attribute,
            y=y_attribute,
            hover_data=["title", "vote_average", "popularity"],
            labels={
                x_attribute: x_attribute.replace("_", " ").title(),
                y_attribute: y_attribute.replace("_", " ").title(),
            },
            title=f"{x_attribute.replace('_', ' ').title()} vs. {y_attribute.replace('_', ' ').title()} Correlation",
        )
        fig.update_traces(marker=dict(size=8, opacity=0.7))
        fig.update_layout(xaxis_type="log", yaxis_type="log")
        return fig
