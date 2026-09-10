"""
pytest tests for database layer
Tests SQL insertion, querying, and data integrity
"""
import pytest
import os
from pathlib import Path
from src.simulator import generate_reading, stream_telemetry
from src import database


@pytest.fixture(autouse=True)
def clean_db(tmp_path, monkeypatch):
    """Use a temporary database for each test"""
    test_db = tmp_path / "test_telemetry.db"
    monkeypatch.setattr(database, "DB_PATH", test_db)
    database.init_db()
    yield
    if test_db.exists():
        test_db.unlink()


def test_init_db_creates_tables():
    """Database initializes with correct tables"""
    conn = database.get_connection()
    tables = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    ).fetchall()
    table_names = [t[0] for t in tables]
    assert "telemetry" in table_names
    assert "alerts" in table_names


def test_insert_readings_returns_correct_count():
    readings = stream_telemetry(n=50)
    count = database.insert_readings(readings)
    assert count == 50


def test_insert_readings_data_persists():
    readings = stream_telemetry(n=10)
    database.insert_readings(readings)
    total = database.get_total_readings()
    assert total == 10


def test_get_station_summary_groups_correctly():
    readings = stream_telemetry(n=100, fault_rate=0.0)
    database.insert_readings(readings)
    summary = database.get_station_summary()
    assert len(summary) <= 5  # max 5 stations
    for row in summary:
        assert "station_id" in row
        assert "avg_voltage" in row
        assert "fault_count" in row


def test_get_fault_readings_only_returns_faults():
    readings = stream_telemetry(n=100, fault_rate=1.0)
    database.insert_readings(readings)
    faults = database.get_fault_readings()
    assert len(faults) > 0
    for f in faults:
        assert f["fault_code"] != 0


def test_insert_alert_persists():
    database.insert_alert("EVSE-001", "2026-08-01T12:00:00",
                          "OVERVOLTAGE", "CRITICAL", 265.0, 250.0)
    alerts = database.get_recent_alerts()
    assert len(alerts) == 1
    assert alerts[0]["alert_type"] == "OVERVOLTAGE"
    assert alerts[0]["severity"] == "CRITICAL"


def test_get_total_readings_empty_db():
    assert database.get_total_readings() == 0


def test_batch_insert_then_query_consistency():
    readings = stream_telemetry(n=75)
    database.insert_readings(readings)
    assert database.get_total_readings() == 75
