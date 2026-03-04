"""fin-health dashboard — entry point."""

import subprocess
from pathlib import Path

from shiny import App, ui

from pages.company import company_server, company_ui
from pages.sector import sector_server, sector_ui

# Load custom CSS
CSS_PATH = Path(__file__).parent.parent / "assets" / "custom_styles.css"
with open(CSS_PATH, "r") as css_file:
    CUSTOM_CSS = ui.tags.style(css_file.read())

# Navbar with page tabs
nav_sector = ui.nav_panel("Sector Analysis", sector_ui())
nav_company = ui.nav_panel("Company Health", company_ui())
navbar = ui.page_navbar(
    nav_sector,
    nav_company,
    title="fin-health",
    id="main_nav",
    fillable=True,
)

# Footer
footer = ui.tags.footer(
    ui.tags.div(
        ui.p(
            "US Corporate Financial Health Dashboard | ",
            "Team: Jiro Amato, Seungmyun Park, Shruti Sasi, Luke Ni | ",
            ui.a("GitHub Repo", href="https://github.com/UBC-MDS/532-finance-health"),
            " | Last updated: "
            + subprocess.run(
                ["git", "log", "-1", "--format=%ci"], capture_output=True, text=True
            ).stdout.strip()[:10],
            style="text-align: center; font-size: 0.85em; color: #888;",
        ),
        class_="footer-container",
    )
)

app_ui = ui.page_fluid(CUSTOM_CSS, navbar, footer)


def server(input, output, session):
    sector_server(input, output, session)
    company_server(input, output, session)


app = App(app_ui, server)
