"""Tests for the web pages in app.py."""

from unittest.mock import patch

import pytest

import nasa_client
from app import create_app

SAMPLE_PICTURE = {
    "title": "The Horsehead Nebula",
    "date": "2024-01-15",
    "explanation": "A dark cloud in Orion.",
    "media_type": "image",
    "url": "https://example.com/small.jpg",
    "hd_url": "https://example.com/large.jpg",
    "credit": "NASA",
}

SAMPLE_PHOTOS = [
    {
        "title": "Rover selfie",
        "date": "2021-03-01",
        "description": "",
        "image_url": "https://example.com/selfie.jpg",
        "nasa_id": "A1",
    }
]


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    return app.test_client()


def test_health_page(client):
    reply = client.get("/health")
    assert reply.status_code == 200
    assert reply.get_json() == {"status": "ok"}


@patch("app.nasa_client.fetch_apod", return_value=SAMPLE_PICTURE)
def test_home_page_shows_picture(mock_fetch, client):
    reply = client.get("/")
    assert reply.status_code == 200
    assert b"The Horsehead Nebula" in reply.data


@patch("app.nasa_client.fetch_apod", return_value=SAMPLE_PICTURE)
def test_home_page_passes_chosen_date(mock_fetch, client):
    client.get("/?date=2024-01-15")
    mock_fetch.assert_called_once_with("2024-01-15")


@patch("app.nasa_client.fetch_apod")
def test_home_page_rejects_bad_date(mock_fetch, client):
    reply = client.get("/?date=1990-01-01")
    assert b"Please choose a date" in reply.data
    mock_fetch.assert_not_called()


@patch("app.nasa_client.fetch_apod", side_effect=nasa_client.NasaError("Could not connect to NASA."))
def test_home_page_shows_friendly_error(mock_fetch, client):
    reply = client.get("/")
    assert reply.status_code == 200
    assert b"Could not connect to NASA." in reply.data


@patch("app.nasa_client.fetch_mars_photos", return_value=SAMPLE_PHOTOS)
def test_mars_page_shows_photos(mock_fetch, client):
    reply = client.get("/mars?rover=Perseverance")
    assert reply.status_code == 200
    assert b"Rover selfie" in reply.data
    mock_fetch.assert_called_once_with("Perseverance")


@patch("app.nasa_client.fetch_mars_photos", return_value=[])
def test_mars_page_handles_no_photos(mock_fetch, client):
    reply = client.get("/mars")
    assert b"No photos were found" in reply.data
