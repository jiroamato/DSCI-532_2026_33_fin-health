"""Page 3: AI Explorer — natural-language data filtering with querychat."""

import os
from functools import cache

import querychat
from chatlas import ChatGithub
from shiny import render, ui
from shinywidgets import output_widget, render_altair

from charts.altair_charts import build_metric_trend, build_sector_bar
from components.empty_chart import empty_chart
from data import METRIC_CHOICES, df

DATA_DESCRIPTION = """
US Corporate financial statement data (2009–2023), covering 12 publicly
traded companies across 8 sectors.

Column descriptions:
- Year: fiscal year (2009–2023)
- Company: ticker symbol (AAPL, GOOG, MSFT, AMZN, INTC, NVDA, PYPL, MCD, AIG, BCS, SHLDQ, PCG)
- Category: sector (BANK, ELEC, FINANCE, FINTECH, FOOD, IT, LOGI, MANUFACTURING)
- Market Cap(in B USD): market capitalization in billions
- Revenue: annual revenue in millions USD
- Gross Profit: gross profit in millions USD
- Net Income: net income in millions USD
- Earning Per Share: earnings per share in USD
- EBITDA: earnings before interest, taxes, depreciation, and amortization in millions USD
- Share Holder Equity: total shareholder equity in millions USD
- Cash Flow from Operating: operating cash flow in millions USD
- Cash Flow from Investing: investing cash flow in millions USD
- Cash Flow from Financial Activities: financing cash flow in millions USD
- Current Ratio: current assets / current liabilities (>1 = healthy liquidity)
- Debt/Equity Ratio: total debt / shareholder equity
- ROE: return on equity (%)
- ROA: return on assets (%)
- ROI: return on investment (%)
- Net Profit Margin: net income / revenue (%)
- Free Cash Flow per Share: free cash flow per share in USD
- Return on Tangible Equity: return on tangible equity (%)
- Number of Employees: headcount
- Inflation Rate(in US): US inflation rate for that year (%)
"""

GREETING = """
Hi! I can help you explore the financial dataset. Try one of these:

* <span class="suggestion">Show tech companies with profit margin above 20%</span>
* <span class="suggestion">Compare all companies in 2022</span>
* <span class="suggestion">Filter to banks with high debt/equity ratio</span>
* <span class="suggestion">Which company had the highest ROE?</span>
"""


@cache
def _get_qc():
    """Lazily create the QueryChat instance (deferred until first use)."""
    return querychat.QueryChat(
        df,
        "financial_data",
        data_description=DATA_DESCRIPTION,
        greeting=GREETING,
        client=ChatGithub(model="gpt-4.1-mini"),
    )


def _has_token():
    """Check whether GITHUB_TOKEN is available."""
    return bool(os.environ.get("GITHUB_TOKEN"))


def ai_explorer_ui():
    """Return the AI Explorer page layout."""
    if not _has_token():
        return ui.page_fillable(
            ui.h2("AI Explorer"),
            ui.card(
                ui.card_header("Configuration Required"),
                ui.p(
                    "Set the GITHUB_TOKEN environment variable to enable the AI Explorer."
                ),
            ),
        )

    qc = _get_qc()
    sidebar = ui.sidebar(
        qc.ui(),
        open="desktop",
        width=400,
    )

    data_card = ui.card(
        ui.card_header(
            ui.div(
                ui.output_text("ai_title"),
                ui.span(" | "),
                ui.output_text("ai_row_count", inline=True),
            )
        ),
        ui.output_data_frame("ai_data_table"),
        ui.download_button("ai_download", "Download CSV"),
        full_screen=True,
    )

    metric_select = ui.input_selectize(
        id="ai_metric",
        label="Metric",
        choices=list(METRIC_CHOICES.keys()),
        selected="Net Profit Margin",
    )

    chart_row = ui.layout_columns(
        ui.card(
            ui.card_header("Sector Profitability"),
            output_widget("ai_chart_a"),
            full_screen=True,
        ),
        ui.card(
            ui.card_header("Metric Trend"),
            output_widget("ai_chart_b"),
            full_screen=True,
        ),
        col_widths=[6, 6],
    )

    return ui.layout_sidebar(
        sidebar,
        ui.page_fillable(
            ui.h2("AI Explorer"),
            metric_select,
            data_card,
            chart_row,
        ),
    )


def ai_explorer_server(input, output, session):
    """Server logic for the AI Explorer page."""
    if not _has_token():
        return

    qc = _get_qc()
    qc_vals = qc.server()

    @render.text
    def ai_title():
        title = qc_vals.title()
        return title if title else "Filtered Data"

    @render.data_frame
    def ai_data_table():
        return qc_vals.df()

    @render.text
    def ai_row_count():
        filtered = qc_vals.df()
        return f"{len(filtered)} rows"

    @render_altair
    def ai_chart_a():
        filtered = qc_vals.df()
        metric = input.ai_metric()
        unit = METRIC_CHOICES.get(metric, "")
        if filtered.empty:
            return empty_chart()
        return build_sector_bar(filtered, metric, unit)

    @render_altair
    def ai_chart_b():
        filtered = qc_vals.df()
        metric = input.ai_metric()
        unit = METRIC_CHOICES.get(metric, "")
        if filtered.empty:
            return empty_chart()
        return build_metric_trend(filtered, metric, unit)

    @render.download(filename="filtered_financial_data.csv")
    def ai_download():
        filtered = qc_vals.df()
        yield filtered.to_csv(index=False)
