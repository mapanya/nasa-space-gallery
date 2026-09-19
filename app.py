"""NASA Space Gallery - the web application.
This file defines the pages of the site. The NASA calls themselves are in nasa_client.py."""

import os
from datetime import date, datetime

from dotenv import load_dotenv
from flask import Flask, render_template, request

import nasa_client

# Read NASA_API_KEY from the private .env file.
load_dotenv()

# NASA's first Astronomy Picture of the Day was published on this date.
FIRST_APOD_DATE = "1995-06-16"


def is_valid_date(text):
    """Return True when text is a real date between the first picture and today."""
    try:
        chosen = datetime.strptime(text, "%Y-%m-%d").date()
    except ValueError:
        return False
    first = datetime.strptime(FIRST_APOD_DATE, "%Y-%m-%d").date()
    return first <= chosen <= date.today()


def create_app():
    """Build and return the web application."""
    app = Flask(__name__)

    @app.route("/")
    def picture_of_the_day():
        chosen_date = request.args.get("date", "").strip()
        picture = None
        error = None

        if chosen_date and not is_valid_date(chosen_date):
            error = "Please choose a date between {} and today.".format(FIRST_APOD_DATE)
        else:
            try:
                picture = nasa_client.fetch_apod(chosen_date or None)
            except nasa_client.NasaError as exc:
                error = str(exc)

        return render_template(
            "apod.html",
            picture=picture,
            error=error,
            chosen_date=chosen_date,
            first_date=FIRST_APOD_DATE,
            today=date.today().isoformat(),
        )

    @app.route("/mars")
    def mars_photos():
        rover = request.args.get("rover", nasa_client.ROVERS[0])
        if rover not in nasa_client.ROVERS:
            rover = nasa_client.ROVERS[0]

        photos = []
        error = None
        try:
            photos = nasa_client.fetch_mars_photos(rover)
        except nasa_client.NasaError as exc:
            error = str(exc)

        return render_template(
            "mars.html",
            photos=photos,
            error=error,
            rover=rover,
            rovers=nasa_client.ROVERS,
        )

    @app.route("/health")
    def health():
        """A tiny page that Kubernetes calls to confirm the app is alive."""
        return {"status": "ok"}

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5001")), debug=False)
