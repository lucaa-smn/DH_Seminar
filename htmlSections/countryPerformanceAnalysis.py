import dash
import pandas as pd
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px


class CountryPerformanceAnalysis:
    def __init__(self, app: dash.Dash, data: pd.DataFrame) -> None:
        self.app = app
        self.data = data.copy()

        # Ensure production_countries is treated as a list
        self.data["production_countries"] = self.data["production_countries"].str.split(
            ", "
        )

        # Explode so each country is treated individually
        self.exploded_data = self.data.explode("production_countries").dropna(
            subset=["production_countries"]
        )

        # Remove leading/trailing whitespace from country names
        self.exploded_data["production_countries"] = self.exploded_data[
            "production_countries"
        ].str.strip()

        # Count movies per country
        country_counts = self.exploded_data["production_countries"].value_counts()

        # Filter countries with at least 5 movies
        valid_countries = country_counts[country_counts >= 5].index.tolist()
        self.filtered_data = self.exploded_data[
            self.exploded_data["production_countries"].isin(valid_countries)
        ]

        # Sorted list for dropdown
        unique_countries = sorted(valid_countries)

        # Layout
        self.div = html.Div(
            [
                html.H1("Country Performance and Movie Success"),
                # Dropdown to select a country
                dcc.Dropdown(
                    id="production-country-dropdown",
                    options=[
                        {"label": country, "value": country}
                        for country in unique_countries
                    ],
                    value=unique_countries[0] if unique_countries else None,
                    placeholder="Select a production country",
                ),
                # Radio buttons for selecting metric (Revenue, Popularity, or Vote Average)
                dcc.RadioItems(
                    id="metric-selector-countries",
                    options=[
                        {"label": "Revenue", "value": "revenue"},
                        {"label": "Popularity", "value": "popularity"},
                        {"label": "Vote Average", "value": "vote_average"},
                    ],
                    value="revenue",
                    inline=True,
                ),
                # Store component to control visibility of aggregation radio items
                dcc.Store(id="aggregation-visibility-store-countries", data=False),
                # Button to switch between SUM and AVERAGE revenue (initially hidden)
                dcc.RadioItems(
                    id="aggregation-selector-countries",
                    options=[
                        {"label": "Average Revenue", "value": "mean"},
                        {"label": "Total Revenue", "value": "sum"},
                    ],
                    value="mean",
                    inline=True,
                    style={"display": "none"},  # Hide initially
                ),
                # Slider to select top countries
                html.Div(
                    [
                        html.Label("Select Top N Countries"),
                        dcc.Slider(
                            id="top-countries-slider",
                            min=5,
                            max=15,
                            step=5,
                            marks={5: "Top 5", 10: "Top 10", 15: "Top 15"},
                            value=5,
                        ),
                    ]
                ),
                # Graph to display the selected production country's data
                dcc.Graph(id="production-country-chart"),
                # Graph to display the top countries based on the selected metric
                dcc.Graph(id="top-countries-chart"),
            ]
        )

        self.register_callbacks()

    def get_html(self) -> html.Div:
        return self.div

    def register_callbacks(self):
        @self.app.callback(
            Output("aggregation-selector-countries", "style"),
            [Input("metric-selector-countries", "value")],
        )
        def update_aggregation_visibility(selected_metric):
            if selected_metric == "revenue":
                return {"display": "inline-block"}  # Show when revenue is selected
            else:
                return {
                    "display": "none"
                }  # Hide when vote_average or popularity is selected

        @self.app.callback(
            Output("production-country-chart", "figure"),
            [
                Input("production-country-dropdown", "value"),
                Input("metric-selector-countries", "value"),
                Input("aggregation-selector-countries", "value"),
            ],
        )
        def update_chart(selected_country, selected_metric, aggregation_method):
            if not selected_country:
                return px.bar(title="No data available")

            # Filter data for the selected country
            country_data = self.filtered_data[
                self.filtered_data["production_countries"] == selected_country
            ]

            # For vote_average, no need for aggregation (it's a single value per movie)
            if selected_metric == "vote_average":
                country_stats = (
                    country_data.groupby("production_countries")[selected_metric]
                    .mean()
                    .reset_index()
                )
                title_suffix = "Average"
            else:
                # Aggregate data based on user selection (SUM or MEAN)
                if aggregation_method == "sum":
                    country_stats = (
                        country_data.groupby("production_countries")[selected_metric]
                        .sum()
                        .reset_index()
                    )
                    title_suffix = "Total"
                else:
                    country_stats = (
                        country_data.groupby("production_countries")[selected_metric]
                        .mean()
                        .reset_index()
                    )
                    title_suffix = "Average"

            # Create bar chart
            fig = px.bar(
                country_stats,
                x="production_countries",
                y=selected_metric,
                text=selected_metric,
                labels={
                    "production_countries": "Production Country",
                    selected_metric: selected_metric.capitalize(),
                },
                title=f"{selected_country}: {title_suffix} {selected_metric.capitalize()}",
            )

            fig.update_traces(texttemplate="%{text:.2s}")
            fig.update_layout(xaxis={"categoryorder": "total descending"})

            return fig

        @self.app.callback(
            Output("top-countries-chart", "figure"),
            [
                Input("metric-selector-countries", "value"),
                Input("aggregation-selector-countries", "value"),
                Input("top-countries-slider", "value"),
            ],
        )
        def update_top_countries_chart(selected_metric, aggregation_method, top_n):
            # Aggregate the data for the selected metric and aggregation method
            if selected_metric == "vote_average":
                country_stats = (
                    self.filtered_data.groupby("production_countries")[selected_metric]
                    .mean()
                    .reset_index()
                )
                title_suffix = "Average"
            else:
                if aggregation_method == "sum":
                    country_stats = (
                        self.filtered_data.groupby("production_countries")[
                            selected_metric
                        ]
                        .sum()
                        .reset_index()
                    )
                    title_suffix = "Total"
                else:
                    country_stats = (
                        self.filtered_data.groupby("production_countries")[
                            selected_metric
                        ]
                        .mean()
                        .reset_index()
                    )
                    title_suffix = "Average"

            # Sort by the selected metric and get the top N countries
            country_stats_sorted = country_stats.sort_values(
                by=selected_metric, ascending=False
            ).head(top_n)

            # Create bar chart for top countries
            fig = px.bar(
                country_stats_sorted,
                x="production_countries",
                y=selected_metric,
                text=selected_metric,
                labels={
                    "production_countries": "Production Country",
                    selected_metric: selected_metric.capitalize(),
                },
                title=f"Top {top_n} Countries: {title_suffix} {selected_metric.capitalize()}",
            )

            fig.update_traces(texttemplate="%{text:.2s}")
            fig.update_layout(xaxis={"categoryorder": "total descending"})

            return fig
