"""
pytest tests for telemetry simulator
"""
import pytest
from src.simulator import generate_reading, stream_telemetry, STATIONS, EVSETelemetry


def test_generate_reading_returns_correct_type():
    reading = generate_reading("EVSE-001")
    assert isinstance(reading, EVSETelemetry)


def test_generate_reading_nominal_voltage_in_range():
    for _ in range(50):
        reading = generate_reading("EVSE-001", "nominal")
        assert 220 <= reading.voltage_v <= 240


def test_generate_reading_overvoltage_fault():
    for _ in range(20):
        reading = generate_reading("EVSE-001", "overvoltage")
        assert reading.voltage_v > 240
        assert reading.fault_code == 1


def test_generate_reading_overcurrent_fault():
    for _ in range(20):
        reading = generate_reading("EVSE-001", "overcurrent")
        assert reading.current_a > 32
        assert reading.fault_code == 2


def test_generate_reading_overtemp_fault():
    for _ in range(20):
        reading = generate_reading("EVSE-001", "overtemp")
        assert reading.temperature_c > 60
        assert reading.fault_code == 3


def test_generate_reading_power_calculated_correctly():
    reading = generate_reading("EVSE-001", "nominal")
    expected_power = round((reading.voltage_v * reading.current_a) / 1000, 3)
    assert abs(reading.power_kw - expected_power) < 0.001


def test_generate_reading_soc_in_valid_range():
    for _ in range(50):
        reading = generate_reading("EVSE-001")
        assert 0 <= reading.state_of_charge_pct <= 100


def test_stream_telemetry_returns_correct_count():
    readings = stream_telemetry(n=100)
    assert len(readings) == 100


def test_stream_telemetry_all_valid_stations():
    readings = stream_telemetry(n=200)
    for r in readings:
        assert r.station_id in STATIONS


def test_stream_telemetry_zero_fault_rate_all_nominal():
    readings = stream_telemetry(n=100, fault_rate=0.0)
    assert all(r.fault_code == 0 for r in readings)


def test_stream_telemetry_full_fault_rate_no_nominal():
    readings = stream_telemetry(n=100, fault_rate=1.0)
    assert all(r.fault_code != 0 for r in readings)
