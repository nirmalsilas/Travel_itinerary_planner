"""
generate_itinerary_groq.py

End-to-end: prompt -> LangChain (Groq) structured output -> Pydantic model
-> Pexels image population -> HTML file.

Requires: pip install langchain langchain-groq pydantic python-dotenv requests --break-system-packages
Set GROQ_API_KEY and PEXELS_API_KEY in your environment (or .env) before running.
"""

import os
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

load_dotenv()

from itinerary_models import Itinerary
from build_itinerary_html import build_from_dict
from image_populator import populate_images
from html_to_pdf import convert_html_to_pdf


SYSTEM_PROMPT = """
You are an expert travel planner with deep knowledge of destinations, logistics,
transportation, budgeting, local culture, food, and tourism.
Generate a premium-quality itinerary that is practical, realistic, and easy to follow.
Guidelines:
- Create a logical day-by-day plan; group nearby attractions to reduce travel time.
- Match recommendations to the traveler's budget and pace.
- Recommend real, actual places whenever possible. If uncertain, make reasonable
  assumptions rather than inventing facts.
- For every "image" field, leave url as an empty string "" — images are sourced
  in a separate step. Still provide a descriptive "alt" text for each, written as
  2-4 concrete keywords describing the visual subject (e.g. "waterfall lush forest",
  not a full sentence) since this text is used directly as an image search query.
- Populate "budget" using the currency specified in the human message.
- Keep prose concise and professional. Avoid generic filler.
"""

HUMAN_PROMPT = """
Create a travel itinerary using these details.

Destination: {destination}
Start date: {start_date}
Trip length: {days} days
Travelers: {travelers}
Budget: {budget}
Budget currency for the Budget section: {budget_currency}
Pace: {pace}
Interests: {interests}
Special notes: {special_notes}

Populate every field of the provided schema. Create one Day entry per day of
the trip (exactly {days} days), each with 5-7 beats. Personalize everything
for {destination} and prioritize experiences related to {interests}.
"""

prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("human", HUMAN_PROMPT),
])

def build_chain(provider: str, api_key: str):
    if provider == "groq":
        llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            api_key=api_key,
            temperature=0.4,
        )
    elif provider == "openai":
        llm = ChatOpenAI(
            model="gpt-4o",
            api_key=api_key,
            temperature=0.4,
        )
    else:
        raise ValueError("provider must be groq or openai")

    return prompt | llm.with_structured_output(Itinerary)


def generate(
    provider: str,
    api_key: str,
    destination: str,
    start_date: str,
    days: int,
    travelers: str,
    budget: str,
    budget_currency: str,
    pace: str,
    interests: str,
    special_notes: str,
    output_path: str = "output_itinerary.html",
    template_path: str = "itinerary_template.html",
    populate_photos: bool = True,
    max_retries: int = 2,
    generate_pdf: bool = False,
    pdf_path: str | None = None,
):
    if not api_key:
        raise ValueError("An API key is required.")

    chain = build_chain(provider, api_key)
    last_err = None
    result: Itinerary | None = None

    for attempt in range(max_retries + 1):
        try:
            result = chain.invoke({
                "destination": destination,
                "start_date": start_date,
                "days": days,
                "travelers": travelers,
                "budget": budget,
                "budget_currency": budget_currency,
                "pace": pace,
                "interests": interests,
                "special_notes": special_notes,
            })
            break
        except Exception as e:
            last_err = e
            print(f"[generate] Attempt {attempt + 1} failed: {e}")

    if result is None:
        raise RuntimeError(
            f"Itinerary generation failed after {max_retries + 1} attempts: {last_err}"
        )

    data = result.model_dump()

    if populate_photos:
        try:
            populate_images(data, destination=destination)
        except Exception as e:
            # Don't let image sourcing failures kill the whole run —
            # the HTML can still render with empty image URLs / alt text.
            print(f"[generate] Warning: image population failed: {e}")

    build_from_dict(data, template_path, output_path)

    if generate_pdf:
        target_pdf = pdf_path or output_path.rsplit(".", 1)[0] + ".pdf"
        try:
            convert_html_to_pdf(output_path, target_pdf)
            print(f"[generate] PDF saved to {target_pdf}")
        except Exception as e:
            # Common cause on Windows: missing GTK3 runtime for WeasyPrint.
            print(f"[generate] Warning: PDF conversion failed: {e}")

    return data


if __name__ == "__main__":
    generate(
        destination="Nara, Japan",
        start_date="2026-04-10",
        days=5,
        travelers="2 adults",
        budget="Mid-range",
        budget_currency="INR",
        pace="Moderate",
        interests="temples, food, photography, quiet hidden gems",
        special_notes="Traveling from Bengaluru, India. Prefer walkable neighborhoods.",
        output_path="output_itinerary.html",
        generate_pdf=True,
    )
