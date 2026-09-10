"""
Health Scoring Engine
Analyzes telemetry and generates alerts based on thresholds
Directly extends GridPulse fault-detection logic
"""
from dataclasses import dataclass
from typing import List, Tuple
from src.simulator import EVSETelemetry
from src import database

# IEC 61851 / industry thresholds
THRESHOLDS = {
    "voltage_high":  250.0,   # V
    "voltage_low":   200.0,   # V
    "current_high":  32.0,    # A (standard Level 2 max)
    "temp_warning":  60.0,    # °C
    "temp_critical": 75.0,    # °C
    "power_max":     7.2,     # kW (Level 2 standard)
}


@dataclass
class HealthScore:
    station_id: str
    score: float        # 0-100, higher is healthier
    status: str         # NOMINAL / WARNING / CRITICAL
    alerts: List[str]


def score_reading(reading: EVSETelemetry) -> HealthScore:
    """Score a single telemetry reading 0-100"""
    score = 100.0
    alerts = []

    # Voltage checks
    if reading.voltage_v > THRESHOLDS["voltage_high"]:
        penalty = min(40, (reading.voltage_v - THRESHOLDS["voltage_high"]) * 2)
        score -= penalty
        alerts.append(f"OVERVOLTAGE: {reading.voltage_v}V > {THRESHOLDS['voltage_high']}V")
        database.insert_alert(reading.station_id, reading.timestamp,
                              "OVERVOLTAGE", "CRITICAL", reading.voltage_v, THRESHOLDS["voltage_high"])

    if reading.voltage_v < THRESHOLDS["voltage_low"]:
        penalty = min(30, (THRESHOLDS["voltage_low"] - reading.voltage_v) * 1.5)
        score -= penalty
        alerts.append(f"UNDERVOLTAGE: {reading.voltage_v}V < {THRESHOLDS['voltage_low']}V")
        database.insert_alert(reading.station_id, reading.timestamp,
                              "UNDERVOLTAGE", "WARNING", reading.voltage_v, THRESHOLDS["voltage_low"])

    # Current checks
    if reading.current_a > THRESHOLDS["current_high"]:
        penalty = min(40, (reading.current_a - THRESHOLDS["current_high"]) * 3)
        score -= penalty
        alerts.append(f"OVERCURRENT: {reading.current_a}A > {THRESHOLDS['current_high']}A")
        database.insert_alert(reading.station_id, reading.timestamp,
                              "OVERCURRENT", "CRITICAL", reading.current_a, THRESHOLDS["current_high"])

    # Temperature checks
    if reading.temperature_c > THRESHOLDS["temp_critical"]:
        score -= 50
        alerts.append(f"CRITICAL TEMP: {reading.temperature_c}°C > {THRESHOLDS['temp_critical']}°C")
        database.insert_alert(reading.station_id, reading.timestamp,
                              "OVERTEMP", "CRITICAL", reading.temperature_c, THRESHOLDS["temp_critical"])
    elif reading.temperature_c > THRESHOLDS["temp_warning"]:
        score -= 20
        alerts.append(f"HIGH TEMP: {reading.temperature_c}°C > {THRESHOLDS['temp_warning']}°C")
        database.insert_alert(reading.station_id, reading.timestamp,
                              "HIGH_TEMP", "WARNING", reading.temperature_c, THRESHOLDS["temp_warning"])

    score = max(0.0, round(score, 1))

    if score >= 80:
        status = "NOMINAL"
    elif score >= 50:
        status = "WARNING"
    else:
        status = "CRITICAL"

    return HealthScore(
        station_id=reading.station_id,
        score=score,
        status=status,
        alerts=alerts,
    )


def process_batch(readings: List[EVSETelemetry]) -> Tuple[int, int, int]:
    """Process a batch of readings. Returns (nominal, warning, critical) counts."""
    nominal = warning = critical = 0
    for reading in readings:
        result = score_reading(reading)
        if result.status == "NOMINAL":
            nominal += 1
        elif result.status == "WARNING":
            warning += 1
        else:
            critical += 1
    return nominal, warning, critical
