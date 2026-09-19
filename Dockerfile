# Start from a small official Python image.
FROM python:3.12-slim

# Do not write .pyc files and show log messages straight away.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install the libraries first so Docker can reuse this step
# when only the application code changes.
COPY requirements.txt requirements-dev.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
# Make sure the ordinary user below can read the application files,
# whatever permissions they had on the computer that built the image.
RUN chmod -R a+rX /app

# Run as an ordinary user instead of the all-powerful root user.
RUN useradd --create-home appuser
USER appuser

EXPOSE 5001

# gunicorn is a production-grade server for Python web apps.
CMD ["gunicorn", "--bind", "0.0.0.0:5001", "--workers", "2", "app:app"]
