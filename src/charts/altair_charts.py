"""Pure Altair chart builder functions — no Shiny imports."""

import altair as alt
import pandas as pd

from components.empty_chart import empty_chart


def build_sector_bar(data: pd.DataFrame, metric: str, unit: str) -> alt.Chart:
    """Bar chart of average metric by sector."""
    if data.empty:
        return empty_chart()
    avg_by_sector = data.groupby("Category")[metric].mean().reset_index()
    if avg_by_sector.empty:
        return empty_chart()
    return (
        alt.Chart(avg_by_sector)
        .mark_bar()
        .encode(
            x=alt.X("Category:N", title="Sector", sort="-y"),
            y=alt.Y(f"{metric}:Q", title=f"{metric} {unit}"),
            color=alt.Color(
                "Category:N",
                scale=alt.Scale(scheme="viridis"),
                legend=None,
            ),
            tooltip=["Category", alt.Tooltip(f"{metric}:Q", format=".2f")],
        )
        .properties(title=f"Average {metric} by Sector", width="container")
    )


def build_metric_trend(data: pd.DataFrame, metric: str, unit: str) -> alt.Chart:
    """Line chart of metric trend over time by sector."""
    if data.empty:
        return empty_chart()
    observed_trend = data.groupby(["Year", "Category"], as_index=False)[metric].mean()
    if observed_trend.empty:
        return empty_chart()
    return (
        alt.Chart(observed_trend)
        .mark_line(point=True)
        .encode(
            alt.X("Year:O", title="Year"),
            alt.Y(f"{metric}:Q", title=f"{metric} {unit}"),
            color=alt.Color("Category:N", scale=alt.Scale(scheme="viridis")),
            tooltip=["Year", "Category", alt.Tooltip(f"{metric}:Q", format=".2f")],
        )
    )


def build_peer_scatter(data: pd.DataFrame, metric: str, unit: str) -> alt.Chart:
    """Scatter plot of Revenue vs selected metric."""
    if data.empty:
        return empty_chart()
    return (
        alt.Chart(data)
        .mark_circle(size=60)
        .encode(
            x=alt.X("Revenue:Q", title="Revenue ($)"),
            y=alt.Y(f"{metric}:Q", title=f"{metric} {unit}"),
            color=alt.Color("Category:N", scale=alt.Scale(scheme="viridis")),
            tooltip=[
                "Company",
                "Category",
                "Year:O",
                alt.Tooltip("Revenue:Q", format=",.0f"),
                alt.Tooltip(f"{metric}:Q", format=",.2f"),
            ],
        )
        .properties(title=f"Revenue vs {metric}", width="container")
    )


def build_revenue_over_time(data: pd.DataFrame, company: str) -> alt.Chart:
    """Bar chart of yearly revenue for a single company (Page 2)."""
    if data.empty:
        return empty_chart()
    return (
        alt.Chart(data)
        .mark_bar()
        .encode(
            x=alt.X("Year:O", title="Year"),
            y=alt.Y("Revenue:Q", title="Revenue ($ millions)"),
            tooltip=[
                alt.Tooltip("Year:O"),
                alt.Tooltip("Revenue:Q", format=",.0f"),
            ],
        )
        .properties(
            title=f"Revenue Over Time — {company}",
            width="container",
        )
    )


def build_ratio_over_time(data: pd.DataFrame, company: str, metric: str) -> alt.Chart:
    """Line chart of a ratio metric over time for a single company (Page 2)."""
    if data.empty:
        return empty_chart()
    return (
        alt.Chart(data)
        .mark_line(point=True)
        .encode(
            x=alt.X("Year:O", title="Year"),
            y=alt.Y(f"{metric}:Q", title=metric),
            tooltip=[
                alt.Tooltip("Year:O"),
                alt.Tooltip(f"{metric}:Q", format=".2f"),
            ],
        )
        .properties(
            title=f"{metric} Over Time — {company}",
            width="container",
        )
    )


def build_cash_flows(data: pd.DataFrame, company: str) -> alt.Chart:
    """Grouped bar chart of Operating, Investing, Financing cash flows (Page 2)."""
    if data.empty:
        return empty_chart()

    cf_cols = {
        "Cash Flow from Operating": "Operating",
        "Cash Flow from Investing": "Investing",
        "Cash Flow from Financial Activities": "Financing",
    }
    melted = data[["Year"] + list(cf_cols.keys())].melt(
        id_vars="Year", var_name="Flow Type", value_name="Amount"
    )
    melted["Flow Type"] = melted["Flow Type"].map(cf_cols)

    return (
        alt.Chart(melted)
        .mark_bar()
        .encode(
            x=alt.X("Year:O", title="Year"),
            y=alt.Y("Amount:Q", title="Cash Flow ($ millions)"),
            color=alt.Color(
                "Flow Type:N",
                scale=alt.Scale(scheme="tableau10"),
            ),
            xOffset="Flow Type:N",
            tooltip=[
                alt.Tooltip("Year:O"),
                alt.Tooltip("Flow Type:N"),
                alt.Tooltip("Amount:Q", format=",.0f"),
            ],
        )
        .properties(
            title=f"Cash Flows — {company}",
            width="container",
        )
    )
