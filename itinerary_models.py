"""
itinerary_models.py

Pydantic models matching itinerary_template.html's expected JSON shape.
Pass Itinerary as the schema to LangChain's with_structured_output() so the
LLM's response comes back already validated and ready to render.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class ImageRef(BaseModel):
    url: str
    alt: str = ""


class HeroFact(BaseModel):
    label: str
    value: str


class Hero(BaseModel):
    eyebrow: str
    titleHtml: str = Field(description="May contain <br> and <em> tags for emphasis")
    subtitle: str
    image: Optional[ImageRef] = None
    facts: List[HeroFact]


class OverviewItem(BaseModel):
    label: str
    value: str
    accent: bool = False


class Location(BaseModel):
    name: str
    address: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None


class Beat(BaseModel):
    time: str = Field(description="24-hour clock time, e.g. '08:00'")
    kind: str = Field(description="Morning | Activity | Lunch | Main attraction | Coffee / Rest | Evening | Dinner")
    text: str
    durationMinutes: Optional[int] = None
    cost: Optional[str] = None
    location: Optional[Location] = None
    image: Optional[ImageRef] = None


class GalleryImage(BaseModel):
    url: str
    alt: str = ""
    caption: str = ""


class Day(BaseModel):
    number: int
    date: Optional[str] = Field(default=None, description="ISO date, e.g. '2026-04-10'")
    theme: str = Field(description="Short label, e.g. 'FUSHIMI & GION'")
    title: str
    coverImage: Optional[ImageRef] = None
    beats: List[Beat]
    gallery: Optional[List[GalleryImage]] = None
    tip: str


class Hotel(BaseModel):
    title: str
    text: str
    price: Optional[str] = None
    rating: Optional[float] = None
    address: Optional[str] = None
    image: Optional[ImageRef] = None
    bookingUrl: Optional[str] = None


class Restaurant(BaseModel):
    title: str
    text: str
    cuisine: Optional[str] = None
    priceLevel: Optional[str] = None
    address: Optional[str] = None
    image: Optional[ImageRef] = None
    bookingUrl: Optional[str] = None


class TransportItem(BaseModel):
    title: str
    text: str


class BudgetRow(BaseModel):
    label: str
    value: str


class BudgetTotal(BaseModel):
    label: str
    value: str


class Budget(BaseModel):
    currency: str = Field(description="ISO currency code, e.g. 'INR' or 'JPY'")
    rows: List[BudgetRow]
    total: BudgetTotal
    note: str


class PackingItem(BaseModel):
    title: str
    text: str


class Tip(BaseModel):
    key: str
    text: str
    image: Optional[ImageRef] = None


class Itinerary(BaseModel):
    destination: str
    hero: Hero
    overview: List[OverviewItem]
    days: List[Day]
    hotels: List[Hotel]
    restaurants: List[Restaurant]
    transport: List[TransportItem]
    budget: Budget
    packing: List[PackingItem]
    tips: List[Tip]
    footer: str
