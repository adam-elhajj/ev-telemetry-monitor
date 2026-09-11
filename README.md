# EV Telemetry Monitor

A production-grade Python data pipeline for real-time EV charging station (EVSE) health monitoring, automated fault detection, and operator alerting — built as a technical extension of [GridPulse](https://github.com/adam-elhajj/gridpulse), my Google Cloud Rapid Agent Hackathon project.

![CI](https://github.com/adam-elhajj/ev-telemetry-monitor/actions/workflows/test.yml/badge.svg)
![Python](https://img.shields.io/badge/Python-3.11-blue)
![Coverage](https://img.shields.io/badge/coverage-94%25-brightgreen)
![Tests](https://img.shields.io/badge/tests-27%20passing-brightgreen)

---

## The Problem

EV charging stations fail silently. A station running at 265V instead of 230V, or drawing 40A instead of the IEC 61851 safe limit of 32A, can damage vehicles, trip breakers, or cause thermal failures — but operators only find out after something breaks. Most EVSE deployments have no automated monitoring layer catching these deviations in real time.

This pipeline is that monitoring layer.

---

## What It Does

Ingests EVSE telemetry continuously, scores every reading against IEC 61851 electrical thresholds, fires prioritized alerts when a station exceeds safe parameters, and aggregates fleet-wide health via SQL queries on a live dashboard.

---

## Results

| Metric | Value |
|---|---|
| Automated unit tests | 27 |
| Code coverage | 94% |
| Coverage on database.py + simulator.py | 100% |
| Pipeline runtime (200 readings, 5 stations) | 1.13 seconds |
| CI/CD coverage gate | 80% minimum enforced on every push |

![pytest output](https://github.com/user-attachments/assets/fc0c4b5a-adf0-4048-85da-98bf93bb866a)

---

## Technical Stack

| Layer | Technology |
|---|---|
| Language | Python 3.11 |
| Database | SQLite with SQL aggregation queries |
| Testing | pytest — 27 tests, 94% coverage |
| CI/CD | GitHub Actions — 80% coverage gate on every push |
| Containerization | Docker |
| Dashboard | Streamlit |
| Standards | IEC 61851 EVSE fault thresholds |

---

## Project Structure

---

## Key Technical Decisions

**Decoupled architecture** — 4 independent modules each with a single responsibility and its own test file. Mirrors production data pipeline design patterns used in industrial IoT monitoring systems.

**IEC 61851 compliance** — fault thresholds (overvoltage >250V, overcurrent >32A, critical temperature >75°C) are based on the international standard for EV conductive charging systems, not arbitrary values.

**Coverage-gated CI/CD** — GitHub Actions enforces a minimum 80% test coverage threshold. Any push that drops below it fails the pipeline automatically. This ensures the codebase is always in a verified, testable state.

**SQL-first data layer** — all analytics (per-station aggregation, fault filtering, alert logging) are handled via SQL queries rather than in-memory operations, reflecting how real telemetry backends store and query time-series data at scale.

---

## Run Locally

```bash
git clone https://github.com/adam-elhajj/ev-telemetry-monitor.git
cd ev-telemetry-monitor
pip install -r requirements.txt

# Run the pipeline
python main.py

# Run the full test suite with coverage
python -m pytest tests/ -v --cov=src --cov-report=term-missing
```

## Run with Docker

```bash
docker build -t ev-telemetry-monitor .
docker run -p 8501:8501 ev-telemetry-monitor
```

---

## Related Projects

[GridPulse](https://github.com/adam-elhajj/gridpulse) — Autonomous EV charging fault-detection agent built with Vertex AI, Gemini 2.0, and Google Cloud Pub/Sub — Google Cloud Rapid Agent Hackathon, May 2026

---

## About

Built by **Adam El Hajj** — ECE Co-op student at the University of Windsor. Research Assistant at AIRC under Dr. Shahpour Alirezaee. Electrical Hardware Designer, UWindsor Rover Team.

[LinkedIn](https://linkedin.com/in/adam-elhajj) · [GitHub](https://github.com/adam-elhajj) · [GridPulse](https://github.com/adam-elhajj/gridpulse)
