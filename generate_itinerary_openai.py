"""
generate_itinerary_openai.py

End-to-end: prompt -> LangChain (OpenAI) structured output -> Pydantic model -> HTML file.

Requires: pip install langchain langchain-openai pydantic --break-system-packages
Set OPENAI_API_KEY in your environment before running.
"""

import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
import os

load_dotenv()

from itinerary_models import Itinerary
from build_itinerary_html import build_from_dict

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
  in a separate step. Still provide a descriptive "alt" text for each.
- heroMark should be a single evocative kanji/glyph for the destination if it has
  an associated culture that uses one, otherwise a simple relevant symbol.
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

# gpt-4o / gpt-4o-mini / gpt-4.1 all support structured output via function calling.
# Use a mini model for cheaper iteration while testing the prompt, upgrade for final quality.
llm = ChatOpenAI(
    model="gpt-4o",
    api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0.4,
)

structured_llm = llm.with_structured_output(Itinerary)

chain = prompt | structured_llm


def generate(
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
):
    result: Itinerary = chain.invoke({
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

    data = result.model_dump()
    build_from_dict(data, template_path, output_path)
    return data


if __name__ == "__main__":
    generate(
        destination="Wayanad, Kerala, India",
        start_date="2026-04-10",
        days=5,
        travelers="2 adults",
        budget="Mid-range",
        budget_currency="INR",
        pace="Moderate",
        interests="temples, food, photography, quiet hidden gems",
        special_notes="Traveling from Bengaluru, India. Prefer walkable neighborhoods.",
        output_path="output_itinerary.html",
    )
