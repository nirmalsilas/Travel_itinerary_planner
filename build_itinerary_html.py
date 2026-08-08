"""
build_itinerary_html.py

Converts an itinerary JSON object into a single, self-contained HTML file
by embedding the data directly into the page (window.ITINERARY_DATA),
so the output opens standalone in a browser with no server required.

Usage:
    python build_itinerary_html.py itinerary.json itinerary_template.html output.html

Or import and call build_itinerary_html() directly from your LangChain script
right after you get structured output back from the model.
"""

import json
import sys
from pathlib import Path


def build_itinerary_html(json_path: str, template_path: str, output_path: str) -> None:
    data = json.loads(Path(json_path).read_text(encoding="utf-8"))
    template = Path(template_path).read_text(encoding="utf-8")

    # Embed the data as a global JS variable. The template's loadItineraryData()
    # checks for window.ITINERARY_DATA before falling back to fetch('itinerary.json'),
    # so this makes the output work as a plain double-click-to-open file.
    data_json = json.dumps(data, ensure_ascii=False, indent=None)
    data_script = f"<script>window.ITINERARY_DATA = {data_json};</script>"

    if "</head>" not in template:
        raise ValueError("Template is missing a </head> tag to inject data before.")

    html = template.replace("</head>", f"{data_script}\n</head>")
    Path(output_path).write_text(html, encoding="utf-8")
    print(f"Wrote {output_path} ({len(html):,} chars)")


def build_from_dict(data: dict, template_path: str, output_path: str) -> None:
    """Same as build_itinerary_html, but takes a Python dict directly —
    use this in your LangChain script right after with_structured_output()
    returns a Pydantic model (call .model_dump() on it first)."""
    template = Path(template_path).read_text(encoding="utf-8")
    data_json = json.dumps(data, ensure_ascii=False, indent=None)
    data_script = f"<script>window.ITINERARY_DATA = {data_json};</script>"

    if "</head>" not in template:
        raise ValueError("Template is missing a </head> tag to inject data before.")

    html = template.replace("</head>", f"{data_script}\n</head>")
    Path(output_path).write_text(html, encoding="utf-8")
    print(f"Wrote {output_path} ({len(html):,} chars)")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python build_itinerary_html.py <itinerary.json> <template.html> <output.html>")
        sys.exit(1)

    json_path, template_path, output_path = sys.argv[1], sys.argv[2], sys.argv[3]
    build_itinerary_html(json_path, template_path, output_path)
