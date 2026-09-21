# NASA Space Gallery

A small web app that shows NASA's Astronomy Picture of the Day and photos from the Mars rovers. Built as Project 1 (Engineering Foundations & DevOps for AI Systems) for Module 1 of the CFDE Pro program.

The project shows a complete delivery path: Git, Docker, Jenkins and Kubernetes on Minikube.

## Features

- Astronomy Picture of the Day, with a date picker to look back to 1995
- Mars Rover photo gallery for Curiosity, Perseverance, Opportunity and Spirit
- Clear messages when NASA cannot be reached
- Automated tests that run without an internet connection
- Health check page at `/health` for Kubernetes

## Project structure

```
nasa-space-gallery/
|-- app.py                 Web pages (routes)
|-- nasa_client.py         All calls to NASA's services
|-- templates/             HTML pages (base, apod, mars)
|-- static/style.css       Look and feel
|-- tests/                 Automated tests
|-- docs/                  Screenshots and architecture diagram
|-- Dockerfile             How to package the app as a container
|-- Jenkinsfile            Pipeline: checkout, build, test, deploy
|-- jenkins/Dockerfile     Jenkins image with the Docker command added
|-- k8s/                   Kubernetes deployment and service
|-- requirements.txt       Libraries needed to run
|-- requirements-dev.txt   Extra libraries needed to test
|-- .env.example           Template for your private settings
```

## Run on your computer

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env        # then put your NASA key in .env
python app.py
```

Open http://localhost:5001

Port 5001 is used because port 5000 is taken by AirPlay Receiver on macOS.

## Run the tests

```bash
python -m pytest -v
```

## Run with Docker

```bash
docker build -t nasa-space-gallery:1.0 .
docker run -d --name nasa-space-gallery -p 5001:5001 --env-file .env nasa-space-gallery:1.0
```

## Run the Jenkins pipeline

```bash
docker build -t jenkins-docker ./jenkins
docker run -d --name jenkins -p 8080:8080 -p 50000:50000 \
  -v jenkins_home:/var/jenkins_home \
  -v /var/run/docker.sock:/var/run/docker.sock \
  jenkins-docker
```

Create a Pipeline job that uses "Pipeline script from SCM", points at this repository, branch `*/main`, script path `Jenkinsfile`.

## Run on Kubernetes (Minikube)

```bash
minikube start --driver=docker
minikube image load nasa-space-gallery:1.0
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
minikube service nasa-space-gallery-service --url
```

## NASA services used

- Astronomy Picture of the Day: https://api.nasa.gov/planetary/apod
- NASA Image and Video Library: https://images-api.nasa.gov

Get a free key at https://api.nasa.gov. Without a key the app uses NASA's shared `DEMO_KEY`, which allows only a few requests per hour. Only the Picture of the Day page needs a key.

The Mars page uses the Image and Video Library rather than NASA's Mars Rover Photos service. That service was archived by its maintainer in October 2025, so this project uses the library instead. Two things follow from that choice. The rover selection is a search rather than a strict filter, so a result may occasionally be mission artwork or a team photo rather than a surface image. The date shown under each photo is the date NASA published the image, not the date the rover took it.