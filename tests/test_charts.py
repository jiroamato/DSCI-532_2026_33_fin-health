import altair as alt
import pandas as pd

from charts.altair_charts import (
    build_sector_bar,
    build_metric_trend,
    build_peer_scatter,
    build_revenue_over_time,
    build_ratio_over_time,
    build_cash_flows,
)
from data import df


def test_build_sector_bar_returns_chart():
    chart = build_sector_bar(df, "Net Profit Margin", "%")
    assert isinstance(chart, alt.Chart)


def test_build_sector_bar_empty_data():
    chart = build_sector_bar(pd.DataFrame(), "Net Profit Margin", "%")
    assert isinstance(chart, alt.Chart)


def test_build_metric_trend_returns_chart():
    chart = build_metric_trend(df, "ROE", "%")
    assert isinstance(chart, alt.Chart)


def test_build_metric_trend_empty_data():
    chart = build_metric_trend(pd.DataFrame(), "ROE", "%")
    assert isinstance(chart, alt.Chart)


def test_build_peer_scatter_returns_chart():
    chart = build_peer_scatter(df, "Net Profit Margin", "%")
    assert isinstance(chart, alt.Chart)


def test_build_peer_scatter_empty_data():
    chart = build_peer_scatter(pd.DataFrame(), "Net Profit Margin", "%")
    assert isinstance(chart, alt.Chart)


def test_build_revenue_over_time_returns_chart():
    aapl = df[df["Company"] == "AAPL"]
    chart = build_revenue_over_time(aapl, "AAPL")
    assert isinstance(chart, alt.Chart)


def test_build_ratio_over_time_returns_chart():
    aapl = df[df["Company"] == "AAPL"]
    chart = build_ratio_over_time(aapl, "AAPL", "Current Ratio")
    assert isinstance(chart, alt.Chart)


def test_build_cash_flows_returns_chart():
    aapl = df[df["Company"] == "AAPL"]
    chart = build_cash_flows(aapl, "AAPL")
    assert isinstance(chart, alt.Chart)
