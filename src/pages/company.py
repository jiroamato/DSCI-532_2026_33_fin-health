"""Page 2: Company Financial Health — UI layout and server logic."""

from shiny import reactive, ui

from data import ALL_SECTORS, CATEGORY_COMPANIES


def company_ui():
    """Return the full Page 2 layout."""
    # Sidebar inputs
    category_select = ui.input_select(
        id="category",
        label="Industry",
        choices=ALL_SECTORS,
        selected=ALL_SECTORS[0],
    )
    company_select = ui.input_select(
        id="company",
        label="Company",
        choices=[],
    )
    year_select = ui.input_select(
        id="year",
        label="Year",
        choices=[str(y) for y in range(2023, 2008, -1)],
        selected="2022",
    )
    sidebar = ui.sidebar(
        ui.h4("Analytics Filters"),
        category_select,
        company_select,
        year_select,
        open="desktop",
    )

    # Profitability cards (hardcoded placeholders — replaced by Task 6)
    card_npm = ui.card(
        ui.card_header("Net Profit Margin"),
        ui.div(
            ui.span("25.3%", class_="kpi-value"),
            ui.br(),
            ui.span("[Sparkline chart placeholder]", class_="kpi-label"),
        ),
    )
    card_roe = ui.card(
        ui.card_header("Return on Equity (ROE)"),
        ui.div(
            ui.span("196.96%", class_="kpi-value"),
            ui.br(),
            ui.span("[Sparkline chart placeholder]", class_="kpi-label"),
        ),
        style="height: calc(50% - 0.5rem);",
    )
    card_rev_income = ui.card(
        ui.card_header("Revenue & Net Income"),
        ui.tags.span("REVENUE", class_="kpi-label"),
        ui.div(
            ui.span("$394,328M", class_="kpi-value"),
            ui.br(),
            ui.span("Revenue", class_="kpi-label"),
            ui.br(),
            ui.br(),
            ui.span("$99,803M", class_="kpi-value"),
            ui.br(),
            ui.span("Net Income", class_="kpi-label"),
        ),
    )
    card_rev_time = ui.card(
        ui.card_header("Revenue Over Time"),
        ui.p("[Bar chart placeholder — yearly revenue from 2009-2023]"),
        full_screen=True,
    )
    profitability_section = ui.div(
        ui.div("PROFITABILITY", class_="section-label section-label-blue"),
        ui.layout_columns(
            card_npm,
            card_roe,
            card_rev_income,
            card_rev_time,
            col_widths=[3, 3, 3, 3],
        ),
        class_="grid-section",
    )

    # Financial Health cards (hardcoded placeholders — replaced by Task 7)
    card_current_ratio = ui.card(
        ui.card_header("Current Ratio"),
        ui.div(
            ui.span("0.88", class_="kpi-value"),
            ui.br(),
            ui.span("Current Ratio over time", class_="kpi-label"),
        ),
        ui.p("[Line chart placeholder]"),
        full_screen=True,
    )
    card_debt_equity = ui.card(
        ui.card_header("Debt / Equity Ratio"),
        ui.div(
            ui.span("2.37", class_="kpi-value"),
            ui.br(),
            ui.span("Debt/Equity over time", class_="kpi-label"),
        ),
        ui.p("[Line chart placeholder]"),
        full_screen=True,
    )
    card_cash_flows = ui.card(
        ui.card_header("Cash Flows"),
        ui.div(
            ui.span("Operating: $122,151M", class_="kpi-label"),
            ui.br(),
            ui.span("Investing: -$22,354M", class_="kpi-label"),
            ui.br(),
            ui.span("Financing: -$110,749M", class_="kpi-label"),
        ),
        ui.p("[Grouped bar chart placeholder]"),
        full_screen=True,
    )
    health_section = ui.div(
        ui.div("FINANCIAL HEALTH", class_="section-label section-label-red"),
        ui.layout_columns(
            card_current_ratio,
            card_debt_equity,
            card_cash_flows,
            col_widths=[4, 4, 4],
        ),
        class_="grid-section",
    )

    return ui.layout_sidebar(
        sidebar,
        ui.page_fillable(
            ui.h2("Financial Health Dashboard"),
            ui.p(
                "A comprehensive KPI dashboard highlighting key financial metrics of public companies."
            ),
            profitability_section,
            health_section,
        ),
    )


def company_server(input, output, session):
    """Page 2 reactive logic."""

    @reactive.effect
    @reactive.event(input.category)
    def _update_company_choices():
        companies = CATEGORY_COMPANIES.get(input.category(), [])
        selected = companies[0] if companies else None
        ui.update_select("company", choices=companies, selected=selected)
