"""
EV Charging Station Telemetry Simulator
Generates realistic EVSE data streams for pipeline testing
"""
import random
import time
from datetime import datetime
from dataclasses import dataclass


@dataclass
class EVSETelemetry:
    station_id: str
    timestamp: str
    voltage_v: float
    current_a: float
    power_kw: float
    temperature_c: float
    state_of_charge_pct: float
    fault_code: int  # 0 = nominal, 1 = overvoltage, 2 = overcurrent, 3 = overtemp


STATIONS = ["EVSE-001", "EVSE-002", "EVSE-003", "EVSE-004", "EVSE-005"]

FAULT_PROFILES = {
    "nominal":      {"voltage": (220, 240), "current": (10, 32), "temp": (20, 45), "fault": 0},
    "overvoltage":  {"voltage": (260, 280), "current": (10, 32), "temp": (20, 45), "fault": 1},
    "overcurrent":  {"voltage": (220, 240), "current": (36, 45), "temp": (20, 45), "fault": 2},
    "overtemp":     {"voltage": (220, 240), "current": (10, 32), "temp": (75, 95), "fault": 3},
}


def generate_reading(station_id: str, inject_fault: str = "nominal") -> EVSETelemetry:
    profile = FAULT_PROFILES[inject_fault]
    voltage = round(random.uniform(*profile["voltage"]), 2)
    current = round(random.uniform(*profile["current"]), 2)
    power = round((voltage * current) / 1000, 3)
    temp = round(random.uniform(*profile["temp"]), 1)
    soc = round(random.uniform(5, 95), 1)

    return EVSETelemetry(
        station_id=station_id,
        timestamp=datetime.utcnow().isoformat(),
        voltage_v=voltage,
        current_a=current,
        power_kw=power,
        temperature_c=temp,
        state_of_charge_pct=soc,
        fault_code=profile["fault"],
    )


def stream_telemetry(n: int = 100, fault_rate: float = 0.1):
    """Generate n telemetry readings with configurable fault injection rate"""
    readings = []
    fault_types = ["overvoltage", "overcurrent", "overtemp"]

    for _ in range(n):
        station = random.choice(STATIONS)
        if random.random() < fault_rate:
            fault = random.choice(fault_types)
        else:
            fault = "nominal"
        readings.append(generate_reading(station, fault))

    return readings
