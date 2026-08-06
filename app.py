"""
app.py

FastAPI wrapper around generate_itinerary_groq.generate().
Serves the trip_input_form.html and exposes POST /generate.

Run with:  uvicorn app:app --reload
"""

import os
import uuid
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from generate_itinerary_groq import generate

app = FastAPI(title="Travel Itinerary Generator")

OUTPUT_DIR = Path("generated_itineraries")
OUTPUT_DIR.mkdir(exist_ok=True)

# Serves whatever lands in OUTPUT_DIR at /files/<name>
app.mount("/files", StaticFiles(directory=OUTPUT_DIR), name="files")


class TripRequest(BaseModel):
    destination: str
    start_date: str
    days: int
    travelers: str
    budget: str
    budget_currency: str
    pace: str
    interests: str
    special_notes: str = ""
    generate_pdf: bool = False


@app.get("/")
def index():
    # trip_input_form.html sitting alongside app.py
    return FileResponse("trip_input_form.html")


@app.post("/generate")
def generate_endpoint(req: TripRequest):
    if req.days < 1 or req.days > 30:
        raise HTTPException(400, "days must be between 1 and 30.")
    if not req.destination.strip():
        raise HTTPException(400, "destination is required.")

    run_id = uuid.uuid4().hex[:8]
    html_name = f"itinerary_{run_id}.html"
    html_path = OUTPUT_DIR / html_name

    try:
        generate(
            destination=req.destination,
            start_date=req.start_date,
            days=req.days,
            travelers=req.travelers,
            budget=req.budget,
            budget_currency=req.budget_currency,
            pace=req.pace,
            interests=req.interests,
            special_notes=req.special_notes,
            output_path=str(html_path),
            generate_pdf=req.generate_pdf,
        )
    except Exception as e:
        # Covers Groq errors, structured-output failures after retries, etc.
        raise HTTPException(500, f"Itinerary generation failed: {e}")

    if not html_path.exists():
        raise HTTPException(500, "Generation finished but no HTML file was produced.")

    result = {"output_url": f"/files/{html_name}"}

    pdf_path = html_path.with_suffix(".pdf")
    if req.generate_pdf and pdf_path.exists():
        result["pdf_url"] = f"/files/{pdf_path.name}"

    return JSONResponse(result)