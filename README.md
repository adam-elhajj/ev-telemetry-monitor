Let me write both properly.**README — paste this into your GitHub README.md file:**

---

# EV Telemetry Monitor

A production-grade Python data pipeline for real-time EV charging station (EVSE) health monitoring, automated fault detection, and operator alerting — built as a technical extension of [GridPulse](https://github.com/adam-elhajj/gridpulse), my Google Cloud Rapid Agent Hackathon project.

![CI](https://github.com/adam-elhajj/ev-telemetry-monitor/actions/workflows/test.yml/badge.svg)
![Python](https://img.shields.io/badge/Python-3.11-blue)
![Coverage](https://img.shields.io/badge/coverage-94%25-brightgreen)
![Tests](https://img.shields.io/badge/tests-27%20passing-brightgreen)

---

## What it does

Ingests simulated EVSE telemetry streams (voltage, current, temperature, fault codes), stores readings in a structured SQLite database, scores each reading against IEC 61851 electrical safety thresholds, generates prioritized alerts, and displays real-time station health on a Streamlit dashboard.

```
Telemetry Simulator → SQLite Ingestion Layer → Health Scoring Engine → Alert System → Streamlit Dashboard
```

---

## Technical Stack

| Layer | Technology |
|---|---|
| Language | Python 3.11 |
| Database | SQLite with SQL aggregation queries |
| Testing | pytest — 27 tests, 94% code coverage |
| CI/CD | GitHub Actions — enforces 80% coverage gate on every push |
| Containerization | Docker |
| Dashboard | Streamlit |
| Standards | IEC 61851 EVSE fault thresholds |

---

## Project Structure

```
ev-telemetry-monitor/
├── src/
│   ├── simulator.py        # EVSE telemetry stream generator with fault injection
│   ├── database.py         # SQLite data layer — insert, query, aggregate
│   └── health_engine.py    # IEC 61851 threshold scoring and alert generation
├── tests/
│   ├── test_simulator.py   # 11 unit tests — fault profiles, data validity
│   ├── test_database.py    # 8 unit tests — SQL integrity, batch insert, alerting
│   └── test_health_engine.py # 8 unit tests — threshold logic, scoring accuracy
├── dashboard.py            # Streamlit real-time monitoring dashboard
├── main.py                 # Pipeline entry point
├── Dockerfile              # Containerized deployment
└── .github/workflows/
    └── test.yml            # CI/CD — full test suite runs on every push to main
```

---

## Key Technical Decisions

**Decoupled architecture** — 4 independent modules each with a single responsibility and its own test file. Mirrors production data pipeline design patterns used in industrial IoT systems.

**IEC 61851 compliance** — fault thresholds (overvoltage >250V, overcurrent >32A, critical temperature >75°C) are based on the international standard for EV conductive charging systems.

**Coverage-gated CI/CD** — GitHub Actions enforces a minimum 80% coverage threshold. Any push that drops below it fails the pipeline automatically.

**SQL-first data layer** — all analytics handled via SQL queries, reflecting how real telemetry backends store and query time-series data.

---

## Results

- 27 automated tests across 3 modules
- 94% code coverage on all source files
- 100% coverage on database.py and simulator.py
- Processes 200 telemetry readings across 5 stations in under 1 second

---

## Run Locally

```bash
git clone https://github.com/adam-elhajj/ev-telemetry-monitor.git
cd ev-telemetry-monitor
pip install -r requirements.txt
python main.py
python -m pytest tests/ -v --cov=src --cov-report=term-missing
```

## Run with Docker

```bash
docker build -t ev-telemetry-monitor .
docker run -p 8501:8501 ev-telemetry-monitor
```

---

## Related Projects

[GridPulse](https://github.com/adam-elhajj/gridpulse) — Autonomous EV charging fault-detection agent built with Vertex AI, Gemini 2.0, and Google Cloud Pub/Sub (Google Cloud Rapid Agent Hackathon, May 2026)

---

## About

Built by **Adam El Hajj** — 2nd-year ECE Co-op student at the University of Windsor. Research Assistant at AIRC under Dr. Shahpour Alirezaee. Electrical Hardware Designer, UWindsor Rover Team.

[LinkedIn](https://linkedin.com/in/adam-elhajj) · [GitHub](https://github.com/adam-elhajj) · [GridPulse](https://github.com/adam-elhajj/gridpulse)

