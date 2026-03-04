"""Page 3: AI Explorer — natural-language data filtering with querychat."""

import os
from functools import cache

import querychat
from chatlas import ChatGithub
from shiny import reactive, render, ui
from shinywidgets import output_widget, render_altair

from charts.altair_charts import (
    build_company_comparison_bar,
    build_company_trend,
    build_metric_trend,
    build_sector_bar,
    build_single_company_summary,
)
from components.empty_chart import empty_chart
from data import ALL_SECTORS, METRIC_CHOICES, df

DATA_DESCRIPTION = """
US Corporate financial statement data (2009–2023), covering 12 publicly
traded companies across 8 sectors.

Company-sector mapping:
- BANK: AIG, BCS
- ELEC: INTC, NVDA
- FINANCE: SHLDQ
- FINTECH: PYPL
- FOOD: MCD
- IT: AAPL, GOOG, MSFT
- LOGI: AMZN
- MANUFACTURING: PCG

Column descriptions (with approximate value ranges):
- Year: fiscal year (2009–2023)
- Company: ticker symbol (AAPL, GOOG, MSFT, AMZN, INTC, NVDA, PYPL, MCD, AIG, BCS, SHLDQ, PCG)
- Category: sector (BANK, ELEC, FINANCE, FINTECH, FOOD, IT, LOGI, MANUFACTURING)
- Market Cap(in B USD): market capitalization in billions (~$1B–$3,000B)
- Revenue: annual revenue in millions USD (~$500M–$400,000M)
- Gross Profit: gross profit in millions USD (~$100M–$170,000M)
- Net Income: net income in millions USD (~-$25,000M–$100,000M)
- Earning Per Share: earnings per share in USD (~-$30–$6)
- EBITDA: earnings before interest, taxes, depreciation, amortization in millions USD (~-$5,000M–$130,000M)
- Share Holder Equity: total shareholder equity in millions USD (~-$15,000M–$270,000M)
- Cash Flow from Operating: operating cash flow in millions USD (~-$5,000M–$120,000M)
- Cash Flow from Investing: investing cash flow in millions USD (~-$50,000M–$30,000M)
- Cash Flow from Financial Activities: financing cash flow in millions USD (~-$120,000M–$30,000M)
- Current Ratio: current assets / current liabilities; >1 = healthy liquidity (~0.5–4.0)
- Debt/Equity Ratio: total debt / shareholder equity (~-10–30)
- ROE: return on equity in percent (~-80%–+160%)
- ROA: return on assets in percent (~-15%–+30%)
- ROI: return on investment in percent (~-20%–+50%)
- Net Profit Margin: net income / revenue in percent (~-50%–+35%)
- Free Cash Flow per Share: free cash flow per share in USD (~-$5–$7)
- Return on Tangible Equity: return on tangible equity in percent (~-200%–+200%)
- Number of Employees: headcount (~10,000–1,600,000)
- Inflation Rate(in US): US inflation rate for that year in percent (~0.1%–8%)
"""

GREETING = """
Hi! I can help you explore the financial dataset. Try one of these:

**Filter:** <span class="suggestion">Show tech companies with net profit margin above 20%</span>

**Compare:** <span class="suggestion">Rank all companies by ROE in 2023</span>

**Aggregate:** <span class="suggestion">What is the average revenue by sector?</span>

**Health check:** <span class="suggestion">Which companies have a current ratio below 1?</span>
"""

EXTRA_INSTRUCTIONS = """
You are a financial data analyst assistant. Follow these rules strictly:

1. **Always use `querychat_query` before reporting any statistics.** Never guess,
   estimate, or hallucinate numbers. If you cannot answer from the data, say so.

2. Structure every response in this format:
   - **Filters applied:** list the filters used (or "None" if showing all data)
   - **Key stats:** 2-3 notable numbers from the query result
   - **Insight:** one sentence interpreting the result
   - **Try next:** one clickable follow-up suggestion as
     `<span class="suggestion">suggestion text</span>`

3. When the user asks about a sector, use the Category column (e.g., IT, BANK).
   When they mention a company name, map it to the ticker in the Company column.

4. Keep responses concise — no more than 5 sentences outside the structured format.
"""


@cache
def _get_qc():
    """Lazily create the QueryChat instance (deferred until first use)."""
    return querychat.QueryChat(
        df,
        "financial_data",
        data_description=DATA_DESCRIPTION,
        extra_instructions=EXTRA_INSTRUCTIONS,
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
    years = [str(y) for y in sorted(df["Year"].unique())]
    sidebar = ui.sidebar(
        ui.input_selectize(
            "ai_sector", "Sector", choices=["All"] + ALL_SECTORS, selected="All"
        ),
        ui.input_selectize("ai_year", "Year", choices=["All"] + years, selected="All"),
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

    @reactive.effect
    def _sync_dropdowns():
        sector = input.ai_sector()
        year = input.ai_year()
        clauses = []
        parts = []
        if sector != "All":
            clauses.append(f"Category = '{sector}'")
            parts.append(sector)
        if year != "All":
            clauses.append(f"Year = {year}")
            parts.append(year)
        if clauses:
            qc_vals.sql.set(
                f"SELECT * FROM financial_data WHERE {' AND '.join(clauses)}"
            )
            qc_vals.title.set(" — ".join(parts))
        else:
            qc_vals.sql.set(None)
            qc_vals.title.set(None)

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

    def _data_shape(filtered):
        """Return (n_companies, n_sectors, n_years) for adaptive chart selection."""
        return (
            filtered["Company"].nunique(),
            filtered["Category"].nunique(),
            filtered["Year"].nunique(),
        )

    @render_altair
    def ai_chart_a():
        filtered = qc_vals.df()
        metric = input.ai_metric()
        unit = METRIC_CHOICES.get(metric, "")
        if filtered.empty:
            return empty_chart()
        n_companies, n_sectors, n_years = _data_shape(filtered)
        if n_companies == 1:
            return build_single_company_summary(filtered, metric, unit)
        if n_sectors == 1 or n_years == 1:
            return build_company_comparison_bar(filtered, metric, unit)
        return build_sector_bar(filtered, metric, unit)

    @render_altair
    def ai_chart_b():
        filtered = qc_vals.df()
        metric = input.ai_metric()
        unit = METRIC_CHOICES.get(metric, "")
        if filtered.empty:
            return empty_chart()
        n_companies, n_sectors, n_years = _data_shape(filtered)
        if n_years == 1:
            return build_company_comparison_bar(filtered, metric, unit)
        if n_companies <= 5:
            return build_company_trend(filtered, metric, unit)
        return build_metric_trend(filtered, metric, unit)

    @render.download(filename="filtered_financial_data.csv")
    def ai_download():
        filtered = qc_vals.df()
        yield filtered.to_csv(index=False)
