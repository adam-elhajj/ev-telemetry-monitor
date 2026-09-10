# EV Telemetry Monitor

Production-grade Python data pipeline for real-time EV charging station health monitoring.

## Stack
- Python — core pipeline
- SQLite — telemetry storage and SQL querying
- pytest — 27 automated tests, 94% code coverage
- GitHub Actions — CI/CD runs tests on every push
- Docker — containerized deployment
- Streamlit — monitoring dashboard

## Run the pipeline
pip install pytest pytest-cov streamlit
python main.py

## Run tests
python -m pytest tests/ -v --cov=src

## Architecture
Telemetry Simulator → SQLite Database → Health Scoring Engine → Streamlit Dashboard

Built by Adam El Hajj — github.com/adam-elhajj
Extends GridPulse (Google Cloud Rapid Agent Hackathon)
