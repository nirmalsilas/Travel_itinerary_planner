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
        page.wait_for_load_state("networkidle")
        page.wait_for_function(
            "Array.from(document.images).every((image) => image.complete)"
        )

        page.pdf(
            path=pdf_path,
            format="A4",
            print_background=True,
            display_header_footer=False,
            margin={
                "top": "0mm",
                "bottom": "0mm",
                "left": "0mm",
                "right": "0mm",
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