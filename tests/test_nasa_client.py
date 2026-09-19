"""Tests for nasa_client.py.
These tests never contact NASA. They replace the internet call with a
pretend reply, so they give the same result anywhere, even offline."""

from unittest.mock import Mock, patch

import pytest
import requests

import nasa_client


def fake_reply(status_code=200, json_data=None):
    reply = Mock()
    reply.status_code = status_code
    reply.json.return_value = json_data or {}
    return reply


def test_api_key_defaults_to_demo_key(monkeypatch):
    monkeypatch.delenv("NASA_API_KEY", raising=False)
    assert nasa_client.get_api_key() == "DEMO_KEY"


def test_api_key_is_read_from_environment(monkeypatch):
    monkeypatch.setenv("NASA_API_KEY", "my-secret-key")
    assert nasa_client.get_api_key() == "my-secret-key"


@patch("nasa_client.requests.get")
def test_fetch_apod_returns_clean_data(mock_get):
    mock_get.return_value = fake_reply(
        json_data={
            "title": "The Horsehead Nebula",
            "date": "2024-01-15",
            "explanation": "A dark cloud in Orion.",
            "media_type": "image",
            "url": "https://example.com/small.jpg",
            "hdurl": "https://example.com/large.jpg",
        }
    )

    picture = nasa_client.fetch_apod("2024-01-15")

    assert picture["title"] == "The Horsehead Nebula"
    assert picture["hd_url"] == "https://example.com/large.jpg"
    assert picture["credit"] == "NASA"
    assert mock_get.call_args.kwargs["params"]["date"] == "2024-01-15"


@patch("nasa_client.requests.get")
def test_rate_limit_gives_clear_message(mock_get):
    mock_get.return_value = fake_reply(status_code=429)

    with pytest.raises(nasa_client.NasaError, match="limit"):
        nasa_client.fetch_apod()


@patch("nasa_client.requests.get")
def test_connection_failure_gives_clear_message(mock_get):
    mock_get.side_effect = requests.ConnectionError()

    with pytest.raises(nasa_client.NasaError, match="Could not connect"):
        nasa_client.fetch_apod()


@patch("nasa_client.requests.get")
def test_fetch_mars_photos_skips_items_without_image(mock_get):
    mock_get.return_value = fake_reply(
        json_data={
            "collection": {
                "items": [
                    {
                        "data": [{"title": "Rover selfie", "date_created": "2021-03-01T00:00:00Z", "nasa_id": "A1"}],
                        "links": [{"href": "https://example.com/selfie.jpg"}],
                    },
                    {"data": [{"title": "No picture here"}], "links": []},
                ]
            }
        }
    )

    photos = nasa_client.fetch_mars_photos("Curiosity")

    assert len(photos) == 1
    assert photos[0]["title"] == "Rover selfie"
    assert photos[0]["date"] == "2021-03-01"


@patch("nasa_client.requests.get")
def test_unknown_rover_falls_back_to_first_rover(mock_get):
    mock_get.return_value = fake_reply(json_data={"collection": {"items": []}})

    nasa_client.fetch_mars_photos("NotARover")

    assert "Curiosity" in mock_get.call_args.kwargs["params"]["q"]
