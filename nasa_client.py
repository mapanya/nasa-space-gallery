"""All communication with NASA's public services lives in this file.
Keeping it separate from app.py means the web pages never need to knowhow NASA's services work. 
They simply ask this file for clean data."""

import os

import requests

APOD_URL = "https://api.nasa.gov/planetary/apod"
IMAGE_LIBRARY_URL = "https://images-api.nasa.gov/search"

# Seconds to wait for NASA before giving up.
REQUEST_TIMEOUT = 15

# The rovers offered in the drop-down list on the Mars page.
ROVERS = ["Curiosity", "Perseverance", "Opportunity", "Spirit"]


class NasaError(Exception):
    """Raised when NASA cannot be reached or returns a problem."""


def get_api_key():
    """Read the NASA key from the environment.

    DEMO_KEY is NASA's shared public key. It works without signing up
    but only allows a small number of requests per hour.
    """
    return os.getenv("NASA_API_KEY") or "DEMO_KEY"


def _get_json(url, params):
    """Send one request to NASA and return the decoded reply."""
    try:
        response = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)
    except requests.RequestException as exc:
        raise NasaError("Could not connect to NASA. Check your internet connection.") from exc

    if response.status_code == 429:
        raise NasaError("NASA request limit reached. Please try again later or use your own key.")
    if response.status_code == 403:
        raise NasaError("NASA rejected the key. Check NASA_API_KEY in your .env file.")
    if response.status_code != 200:
        raise NasaError("NASA returned an error (status {}).".format(response.status_code))

    try:
        return response.json()
    except ValueError as exc:
        raise NasaError("NASA sent a reply that could not be read.") from exc


def fetch_apod(date=None):
    """Return the Astronomy Picture of the Day.

    date is optional text in the form YYYY-MM-DD. Without it NASA
    returns today's picture.
    """
    params = {"api_key": get_api_key()}
    if date:
        params["date"] = date

    data = _get_json(APOD_URL, params)

    return {
        "title": data.get("title", "Untitled"),
        "date": data.get("date", ""),
        "explanation": data.get("explanation", ""),
        "media_type": data.get("media_type", "image"),
        "url": data.get("url", ""),
        "hd_url": data.get("hdurl") or data.get("url", ""),
        "credit": data.get("copyright", "NASA").strip(),
    }


def fetch_mars_photos(rover="Curiosity", limit=12):
    """Return a list of Mars rover photos from the NASA Image Library."""
    if rover not in ROVERS:
        rover = ROVERS[0]

    params = {
        "q": "{} Mars rover".format(rover),
        "media_type": "image",
        "page_size": limit,
    }
    data = _get_json(IMAGE_LIBRARY_URL, params)

    photos = []
    for item in data.get("collection", {}).get("items", []):
        details = (item.get("data") or [{}])[0]
        links = item.get("links") or []
        if not links or not links[0].get("href"):
            continue
        photos.append(
            {
                "title": details.get("title", "Untitled"),
                "date": details.get("date_created", "")[:10],
                "description": details.get("description", ""),
                "image_url": links[0]["href"],
                "nasa_id": details.get("nasa_id", ""),
            }
        )
    return photos[:limit]
