"""Page 1: Sector Analysis — UI layout and server logic."""

import pandas as pd
from shiny import reactive, render, ui
from shinywidgets import output_widget, render_altair

from charts.altair_charts import (
    build_metric_trend,
    build_peer_scatter,
    build_sector_bar,
)
from components.kpi_card import kpi_card
from data import ALL_SECTORS, METRIC_CHOICES, df


def sector_ui():
    """Return the full Page 1 layout (sidebar + KPI row + chart row + peer row)."""
    # Sidebar inputs
    year_slider = ui.input_slider(
        id="p1_year_range",
        label="Period",
        min=int(df["Year"].min()),
        max=int(df["Year"].max()),
        value=[int(df["Year"].min()), int(df["Year"].max())],
        sep="",
    )
    sector_select = ui.input_selectize(
        id="p1_sector",
        label="Sector",
        choices=["All"] + ALL_SECTORS,
        selected="All",
    )
    metric_select = ui.input_selectize(
        id="p1_metric",
        label="Metric",
        choices=list(METRIC_CHOICES.keys()),
        selected="Net Profit Margin",
    )
    sidebar = ui.sidebar(
        ui.h4("Analytics Filters"),
        year_slider,
        sector_select,
        metric_select,
        open="desktop",
    )

    # KPI cards
    card_avg_margin = kpi_card(
        header="Avg Profit Margin",
        value_id="p1_avg_margin",
        trend_id="p1_margin_trend",
        label_id="p1_margin_badge",
    )
    card_top_sector = kpi_card(
        header="Top Sector",
        value_id="p1_top_sector",
        label_id="p1_index_performance_display",
    )
    card_revenue_growth = kpi_card(
        header="Revenue Growth",
        value_id="p1_revenue_growth_value",
        trend_id="p1_revenue_trend",
        label_id="p1_revenue_growth_label",
    )
    kpi_row = ui.layout_columns(
        card_avg_margin,
        card_top_sector,
        card_revenue_growth,
        col_widths=[4, 4, 4],
    )

    # Chart cards
    card_sector_profitability = ui.card(
        ui.card_header("Sector Profitability"),
        output_widget("p1_chart_a"),
        full_screen=True,
    )
    card_trend = ui.card(
        ui.card_header(ui.output_ui("trend_header")),
        output_widget("p1_chart_b"),
        full_screen=True,
    )
    chart_row = ui.layout_columns(
        card_sector_profitability,
        card_trend,
        col_widths=[6, 6],
    )

    # Peer + Table cards
    card_peer = ui.card(
        ui.card_header("Peer Benchmarking"),
        output_widget("p1_chart_c"),
        full_screen=True,
    )
    card_details = ui.card(
        ui.card_header("Company Details"),
        ui.output_data_frame("p1_table_d"),
    )
    peer_row = ui.layout_columns(
        card_peer,
        card_details,
        col_widths=[6, 6],
    )

    return ui.layout_sidebar(
        sidebar,
        ui.page_fillable(
            ui.h2("US Corporate Profitability Analytics"),
            kpi_row,
            chart_row,
            peer_row,
        ),
    )


def sector_server(input, output, session):
    """All Page 1 reactive calcs and renderers."""

    @reactive.calc
    def p1_selected_metric():
        metric = input.p1_metric()
        if not metric or metric not in METRIC_CHOICES:
            return "Net Profit Margin"
        return metric

    @reactive.calc
    def p1_filtered_data():
        year_min, year_max = input.p1_year_range()
        sector = input.p1_sector()
        if not sector:
            sector = "All"
        filtered = df[(df["Year"] >= year_min) & (df["Year"] <= year_max)]
        if sector != "All":
            filtered = filtered[filtered["Category"] == sector]
        return filtered

    # --- KPI outputs ---

    @render.text
    def p1_avg_margin():
        filtered = p1_filtered_data()
        if filtered.empty:
            return "Data Unavailable"
        avg = filtered["Net Profit Margin"].mean()
        return f"{avg:.1f}%"

    @render.ui
    def p1_margin_trend():
        filtered_df = p1_filtered_data()
        if filtered_df.empty:
            return ui.tags.span()
        years = sorted(filtered_df["Year"].unique())
        if len(years) < 2:
            return ui.tags.span()
        current_year_margin = filtered_df[filtered_df["Year"] == years[-1]][
            "Net Profit Margin"
        ].mean()
        previous_year_margin = filtered_df[filtered_df["Year"] == years[-2]][
            "Net Profit Margin"
        ].mean()
        if pd.isna(current_year_margin) or pd.isna(previous_year_margin):
            return ui.tags.span()
        is_positive = current_year_margin >= previous_year_margin
        trend_char = "▲" if is_positive else "▼"
        trend_class = "up" if is_positive else "down"
        return ui.tags.span(trend_char, class_=f"trend-indicator {trend_class}")

    @render.ui
    def p1_margin_badge():
        filtered = p1_filtered_data()
        if filtered.empty:
            return ui.tags.span()
        n = filtered["Company"].nunique()
        return ui.tags.p(
            f"BASED ON {n} COMPANIES",
            class_="kpi-label",
            style="margin-top: 0.5rem;",
        )

    @render.text
    def p1_top_sector():
        filtered = p1_filtered_data()
        if filtered.empty:
            return "Data Unavailable"
        top = filtered.groupby("Category")["Net Profit Margin"].mean().idxmax()
        return top

    @reactive.calc
    def p1_index_margin():
        filtered_df = p1_filtered_data()
        if filtered_df.empty:
            return 0.0
        total_revenue = filtered_df["Revenue"].sum()
        total_net_income = filtered_df["Net Income"].sum()
        if total_revenue == 0:
            return 0.0
        return (total_net_income / total_revenue) * 100

    @render.ui
    def p1_index_performance_display():
        margin = p1_index_margin()
        return ui.tags.p(
            "INDEX PERFORMANCE: ",
            ui.tags.strong(f"{margin:.1f}%"),
            " NET PROFIT MARGIN",
            class_="kpi-label",
        )

    @reactive.calc
    def p1_revenue_change():
        filtered_df = p1_filtered_data()
        yearly_revenue = (
            filtered_df.groupby("Year")["Revenue"].sum().sort_index(ascending=False)
        )
        if len(yearly_revenue) < 2:
            return None
        current = yearly_revenue.iloc[0]
        previous = yearly_revenue.iloc[1]
        if pd.isna(current) or pd.isna(previous) or previous == 0:
            return None
        revenue_growth = (current - previous) / previous * 100
        return {"value": revenue_growth, "is_positive": revenue_growth >= 0}

    @render.text
    def p1_revenue_growth_value():
        change = p1_revenue_change()
        if change is None:
            return "Data Unavailable"
        sign = "+" if change["is_positive"] else ""
        return f"{sign}{change['value']:.1f}%"

    @render.ui
    def p1_revenue_growth_label():
        return ui.tags.p(
            "YEAR OVER YEAR",
            class_="kpi-label",
            style="margin-top: 0.5rem;",
        )

    @render.ui
    def p1_revenue_trend():
        change = p1_revenue_change()
        if change is None:
            return ui.tags.span()
        trend_char = "▲" if change["is_positive"] else "▼"
        trend_class = "up" if change["is_positive"] else "down"
        return ui.tags.span(trend_char, class_=f"trend-indicator {trend_class}")

    # --- Chart outputs ---

    @render_altair
    def p1_chart_a():
        filtered = p1_filtered_data()
        metric = p1_selected_metric()
        unit = METRIC_CHOICES[metric]
        return build_sector_bar(filtered, metric, unit)

    @render.ui
    def trend_header():
        min_year, max_year = input.p1_year_range()
        return f"Trend - {p1_selected_metric()}  ({min_year}-{max_year})"

    @render_altair
    def p1_chart_b():
        filtered = p1_filtered_data()
        metric = p1_selected_metric()
        unit = METRIC_CHOICES[metric]
        return build_metric_trend(filtered, metric, unit)

    @render_altair
    def p1_chart_c():
        filtered = p1_filtered_data()
        metric = p1_selected_metric()
        unit = METRIC_CHOICES[metric]
        return build_peer_scatter(filtered, metric, unit)

    @render.data_frame
    def p1_table_d():
        filtered = p1_filtered_data()
        cols = [
            "Company",
            "Category",
            "Year",
            "Revenue",
            "Net Income",
            "Net Profit Margin",
        ]
        return filtered[cols]
