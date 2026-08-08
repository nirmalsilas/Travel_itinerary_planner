# AI Travel Itinerary Generator

A web-based travel planner that uses Groq or OpenAI to generate personalized day-by-day itineraries. It can also find travel images through Pexels and optionally export the itinerary as a PDF.

## Features

- FastAPI web application
- Groq or OpenAI itinerary generation
- Structured output validated with Pydantic
- Pexels image population
- HTML itinerary output
- Optional PDF export
- Supports destinations, dates, trip length, travelers, budget, currency, pace, interests, and special notes

## Requirements

- Windows 10 or Windows 11
- Python 3.10 or newer
- Internet connection
- Groq or OpenAI API key
- Pexels API key

## Project Files

| File | Purpose |
| --- | --- |
| `app.py` | FastAPI web server |
| `trip_input_form.html` | Browser form |
| `generate_itinerary_groq.py` | Groq/OpenAI itinerary generation |
| `itinerary_models.py` | Pydantic itinerary schema |
| `build_itinerary_html.py` | Builds the final HTML file |
| `image_populator.py` | Retrieves images from Pexels |
| `html_to_pdf.py` | Converts HTML to PDF |
| `itinerary_template.html` | HTML itinerary template |
| `generated_itineraries/` | Generated HTML and PDF files |
| `.env` | Local API keys; never commit this file |
| `requirements.txt` | Python dependencies |

## 1. Open the Project

Open PowerShell in the project folder:

```powershell
cd C:\AI_Projects\travel
```

## 2. Create a Virtual Environment

Create an isolated Python environment for the project:

```powershell
python -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, allow locally created scripts once:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Then activate the environment again:

```powershell
.\.venv\Scripts\Activate.ps1
```

## 3. Install Dependencies

Upgrade `pip` and install the packages listed in `requirements.txt`:

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

To enable PDF export, install the Playwright browser binaries:

```powershell
python -m playwright install
```

## 4. Configure Environment Variables

The web form accepts either a Groq key or an OpenAI key for each itinerary request. Do not put those provider keys in the browser form if you are sharing your screen.

The application uses Pexels to find itinerary images. Create a `.env` file in the project folder with your Pexels key:

```dotenv
PEXELS_API_KEY=your_pexels_api_key
```

Do not add spaces around the `=` character. Never commit `.env` or share its contents.

## 5. Start the Application

With the virtual environment activated, start the FastAPI server:

```powershell
python -m uvicorn app:app --reload
```

Open the application at:

```text
http://127.0.0.1:8000/
```

In the form:

1. Select `Groq` or `OpenAI`.
2. Enter the matching API key.
3. Complete the trip details.
4. Select `Generate itinerary`.

The key is sent with the current request and is not written to the generated itinerary files.

## Windows Shortcut

You can also run:

```powershell
.\start_app.bat
```

The batch file creates `.venv` and installs dependencies on the first run, then starts the server and opens the browser.

## Troubleshooting

Check that the virtual environment is active when the prompt begins with `(.venv)`. If `fastapi` or another package is missing, run:

```powershell
python -m pip install -r requirements.txt
```

If the browser shows an old version of the form, force-refresh with `Ctrl+F5` and open `http://127.0.0.1:8000/` rather than opening a generated HTML file directly.

To validate the Python files without making an API request:

```powershell
python -m py_compile app.py generate_itinerary_groq.py
```