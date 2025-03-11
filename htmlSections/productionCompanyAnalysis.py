import dash
import pandas as pd
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px


class ProductionCompanyAnalysis:
    def __init__(self, app: dash.Dash, data: pd.DataFrame) -> None:
        self.app = app
        self.data = data.copy()

        # Ensure production_companies is treated as a list
        self.data["production_companies"] = self.data["production_companies"].str.split(
            ", "
        )

        # Explode so each company is treated individually
        self.exploded_data = self.data.explode("production_companies").dropna(
            subset=["production_companies"]
        )

        # Remove leading/trailing whitespace from company names
        self.exploded_data["production_companies"] = self.exploded_data[
            "production_companies"
        ].str.strip()

        # Count movies per production company
        company_counts = self.exploded_data["production_companies"].value_counts()

        # Filter companies with at least 5 movies
        valid_companies = company_counts[company_counts >= 5].index.tolist()
        self.filtered_data = self.exploded_data[
            self.exploded_data["production_companies"].isin(valid_companies)
        ]

        # Sorted list for dropdown
        unique_companies = sorted(valid_companies)

        # Layout
        self.div = html.Div(
            [
                html.H1("Production Companies and Movie Success"),
                # Dropdown to select a production company
                dcc.Dropdown(
                    id="production-company-dropdown",
                    options=[
                        {"label": company, "value": company}
                        for company in unique_companies
                    ],
                    value=unique_companies[0] if unique_companies else None,
                    placeholder="Select a production company",
                ),
                # Radio buttons for selecting metric (Revenue, Vote Average, Popularity)
                dcc.RadioItems(
                    id="metric-selector",
                    options=[
                        {"label": "Revenue", "value": "revenue"},
                        {"label": "Vote Average", "value": "vote_average"},
                        {"label": "Popularity", "value": "popularity"},
                    ],
                    value="revenue",
                    inline=True,
                ),
                # Store component to control visibility of aggregation radio items
                dcc.Store(id="aggregation-visibility-store", data=False),
                # Button to switch between SUM and AVERAGE revenue (initially hidden)
                dcc.RadioItems(
                    id="aggregation-selector",
                    options=[
                        {"label": "Average Revenue", "value": "mean"},
                        {"label": "Total Revenue", "value": "sum"},
                    ],
                    value="mean",
                    inline=True,
                    style={"display": "none"},  # Hide initially
                ),
                # Slider to select top companies
                html.Div(
                    [
                        html.Label("Select Top N Companies"),
                        dcc.Slider(
                            id="top-companies-slider",
                            min=5,
                            max=15,
                            step=5,
                            marks={5: "Top 5", 10: "Top 10", 15: "Top 15"},
                            value=5,
                        ),
                    ]
                ),
                # Graph to display the selected production company's data
                dcc.Graph(id="production-company-chart"),
                # Graph to display the top companies based on the selected metric
                dcc.Graph(id="top-companies-chart"),
            ]
        )

        self.register_callbacks()

    def get_html(self) -> html.Div:
        return self.div

    def register_callbacks(self):
        # Callback for controlling the visibility of the aggregation radio buttons
        @self.app.callback(
            Output("aggregation-selector", "style"),
            [Input("metric-selector", "value")],
        )
        def update_aggregation_visibility(selected_metric):
            if selected_metric == "revenue":
                return {"display": "inline-block"}  # Show when revenue is selected
            else:
                return {"display": "none"}  # Hide otherwise

        # Callback for updating the selected production company chart
        @self.app.callback(
            Output("production-company-chart", "figure"),
            [
                Input("production-company-dropdown", "value"),
                Input("metric-selector", "value"),
                Input("aggregation-selector", "value"),
            ],
        )
        def update_chart(selected_company, selected_metric, aggregation_method):
            if not selected_company:
                return px.bar(title="No data available")

            # Filter data for the selected company
            company_data = self.filtered_data[
                self.filtered_data["production_companies"] == selected_company
            ]

            # Handle different metrics and aggregation methods
            if selected_metric in ["revenue", "popularity"]:
                if aggregation_method == "sum":
                    company_stats = (
                        company_data.groupby("production_companies")[selected_metric]
                        .sum()
                        .reset_index()
                    )
                    title_suffix = "Total"
                else:
                    company_stats = (
                        company_data.groupby("production_companies")[selected_metric]
                        .mean()
                        .reset_index()
                    )
                    title_suffix = "Average"
            elif selected_metric == "vote_average":
                # Vote average does not use sum/mean aggregation options
                company_stats = (
                    company_data.groupby("production_companies")[selected_metric]
                    .mean()
                    .reset_index()
                )
                title_suffix = "Average"

            # Create bar chart
            fig = px.bar(
                company_stats,
                x="production_companies",
                y=selected_metric,
                text=selected_metric,
                labels={
                    "production_companies": "Production Company",
                    selected_metric: selected_metric.capitalize(),
                },
                title=f"{selected_company}: {title_suffix} {selected_metric.capitalize()}",
            )

            fig.update_traces(texttemplate="%{text:.2s}")
            fig.update_layout(xaxis={"categoryorder": "total descending"})

            return fig

        # Callback for updating the top companies chart
        @self.app.callback(
            Output("top-companies-chart", "figure"),
            [
                Input("metric-selector", "value"),
                Input("aggregation-selector", "value"),
                Input("top-companies-slider", "value"),
            ],
        )
        def update_top_companies_chart(selected_metric, aggregation_method, top_n):
            # Aggregate the data for the selected metric and aggregation method
            if selected_metric in ["revenue", "popularity"]:
                if aggregation_method == "sum":
                    company_stats = (
                        self.filtered_data.groupby("production_companies")[
                            selected_metric
                        ]
                        .sum()
                        .reset_index()
                    )
                    title_suffix = "Total"
                else:
                    company_stats = (
                        self.filtered_data.groupby("production_companies")[
                            selected_metric
                        ]
                        .mean()
                        .reset_index()
                    )
                    title_suffix = "Average"
            elif selected_metric == "vote_average":
                company_stats = (
                    self.filtered_data.groupby("production_companies")[selected_metric]
                    .mean()
                    .reset_index()
                )
                title_suffix = "Average"

            # Sort by the selected metric and get the top N companies
            company_stats_sorted = company_stats.sort_values(
                by=selected_metric, ascending=False
            ).head(top_n)

            # Create bar chart for top companies
            fig = px.bar(
                company_stats_sorted,
                x="production_companies",
                y=selected_metric,
                text=selected_metric,
                labels={
                    "production_companies": "Production Company",
                    selected_metric: selected_metric.capitalize(),
                },
                title=f"Top {top_n} Companies: {title_suffix} {selected_metric.capitalize()}",
            )

            fig.update_traces(texttemplate="%{text:.2s}")
            fig.update_layout(xaxis={"categoryorder": "total descending"})

            return fig
