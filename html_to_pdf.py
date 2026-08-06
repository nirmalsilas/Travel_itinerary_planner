"""
html_to_pdf.py

Convert HTML to PDF using Playwright.

Installation:

pip install playwright

Then install Chromium:

playwright install chromium
"""

from pathlib import Path
from playwright.sync_api import sync_playwright


def convert_html_to_pdf(html_path: str, pdf_path: str) -> str:
    html_file = Path(html_path).resolve()

    with sync_playwright() as p:
        browser = p.chromium.launch()

        page = browser.new_page()

        page.goto(html_file.as_uri())

        page.pdf(
            path=pdf_path,
            format="A4",
            print_background=True,
            margin={
                "top": "10mm",
                "bottom": "10mm",
                "left": "10mm",
                "right": "10mm",
            },
        )

        browser.close()

    return pdf_path


if __name__ == "__main__":
    convert_html_to_pdf(
        "output_itinerary.html",
        "output_itinerary.pdf",
    )

    print("PDF saved to output_itinerary.pdf")