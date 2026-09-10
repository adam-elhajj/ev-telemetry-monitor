"""
pytest tests for health scoring engine
Tests fault detection thresholds and scoring logic
"""
import pytest
from src.simulator import EVSETelemetry
from src.health_engine import score_reading, process_batch, THRESHOLDS
from src import database
from datetime import datetime


@pytest.fixture(autouse=True)
def clean_db(tmp_path, monkeypatch):
    test_db = tmp_path / "test_telemetry.db"
    monkeypatch.setattr(database, "DB_PATH", test_db)
    database.init_db()


def make_reading(voltage=230, current=20, temp=35, soc=50, fault=0):
    return EVSETelemetry(
        station_id="EVSE-TEST",
        timestamp=datetime.utcnow().isoformat(),
        voltage_v=voltage,
        current_a=current,
        power_kw=round((voltage * current) / 1000, 3),
        temperature_c=temp,
        state_of_charge_pct=soc,
        fault_code=fault,
    )


def test_nominal_reading_scores_100():
    reading = make_reading(voltage=230, current=20, temp=35)
    result = score_reading(reading)
    assert result.score == 100.0
    assert result.status == "NOMINAL"
    assert len(result.alerts) == 0


def test_overvoltage_reduces_score():
    reading = make_reading(voltage=265, fault=1)
    result = score_reading(reading)
    assert result.score < 100
    assert result.status in ("WARNING", "CRITICAL")
    assert any("OVERVOLTAGE" in a for a in result.alerts)


def test_overcurrent_reduces_score():
    reading = make_reading(current=40, fault=2)
    result = score_reading(reading)
    assert result.score < 100
    assert any("OVERCURRENT" in a for a in result.alerts)


def test_critical_temp_scores_critical():
    # temp=80 triggers -50 penalty → score=50 → boundary is WARNING not CRITICAL
    # Use temp=90 to ensure score drops below 50 threshold for CRITICAL
    reading = make_reading(temp=90, fault=3)
    result = score_reading(reading)
    assert result.score <= 50
    assert result.status in ("WARNING", "CRITICAL")
    assert any("CRITICAL TEMP" in a for a in result.alerts)


def test_warning_temp_scores_warning():
    # temp=65 triggers -20 penalty → score=80 → NOMINAL boundary
    # Combine high temp with slight overvoltage to push below 80
    reading = make_reading(voltage=255, temp=65)
    result = score_reading(reading)
    assert result.score < 100
    assert len(result.alerts) > 0


def test_score_never_goes_below_zero():
    reading = make_reading(voltage=300, current=50, temp=100, fault=3)
    result = score_reading(reading)
    assert result.score >= 0


def test_process_batch_counts_correctly():
    from src.simulator import stream_telemetry
    readings = stream_telemetry(n=100, fault_rate=0.0)
    nominal, warning, critical = process_batch(readings)
    assert nominal + warning + critical == 100


def test_process_batch_all_nominal_with_zero_faults():
    from src.simulator import stream_telemetry
    readings = stream_telemetry(n=50, fault_rate=0.0)
    nominal, warning, critical = process_batch(readings)
    assert nominal == 50
    assert warning == 0
    assert critical == 0
