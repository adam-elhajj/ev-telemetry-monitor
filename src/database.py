"""
SQLite Database Layer
Handles all telemetry storage and SQL querying
"""
import sqlite3
from pathlib import Path
from typing import List, Optional
from src.simulator import EVSETelemetry

DB_PATH = Path("data/telemetry.db")


def get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Create tables if they don't exist"""
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS telemetry (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                station_id  TEXT    NOT NULL,
                timestamp   TEXT    NOT NULL,
                voltage_v   REAL    NOT NULL,
                current_a   REAL    NOT NULL,
                power_kw    REAL    NOT NULL,
                temperature_c REAL  NOT NULL,
                soc_pct     REAL    NOT NULL,
                fault_code  INTEGER NOT NULL DEFAULT 0
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS alerts (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                station_id  TEXT    NOT NULL,
                timestamp   TEXT    NOT NULL,
                alert_type  TEXT    NOT NULL,
                severity    TEXT    NOT NULL,
                value       REAL    NOT NULL,
                threshold   REAL    NOT NULL
            )
        """)
        conn.commit()


def insert_readings(readings: List[EVSETelemetry]) -> int:
    """Batch insert telemetry readings. Returns count inserted."""
    with get_connection() as conn:
        conn.executemany("""
            INSERT INTO telemetry
            (station_id, timestamp, voltage_v, current_a, power_kw, temperature_c, soc_pct, fault_code)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, [
            (r.station_id, r.timestamp, r.voltage_v, r.current_a,
             r.power_kw, r.temperature_c, r.state_of_charge_pct, r.fault_code)
            for r in readings
        ])
        conn.commit()
        return len(readings)


def insert_alert(station_id: str, timestamp: str, alert_type: str,
                 severity: str, value: float, threshold: float) -> None:
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO alerts (station_id, timestamp, alert_type, severity, value, threshold)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (station_id, timestamp, alert_type, severity, value, threshold))
        conn.commit()


def get_station_summary() -> List[dict]:
    """SQL query: average metrics per station"""
    with get_connection() as conn:
        rows = conn.execute("""
            SELECT
                station_id,
                COUNT(*)            AS total_readings,
                ROUND(AVG(voltage_v), 2)    AS avg_voltage,
                ROUND(AVG(current_a), 2)    AS avg_current,
                ROUND(AVG(power_kw), 3)     AS avg_power_kw,
                ROUND(AVG(temperature_c), 1) AS avg_temp,
                SUM(CASE WHEN fault_code != 0 THEN 1 ELSE 0 END) AS fault_count
            FROM telemetry
            GROUP BY station_id
            ORDER BY fault_count DESC
        """).fetchall()
        return [dict(r) for r in rows]


def get_fault_readings(limit: int = 50) -> List[dict]:
    """SQL query: most recent fault readings"""
    with get_connection() as conn:
        rows = conn.execute("""
            SELECT * FROM telemetry
            WHERE fault_code != 0
            ORDER BY timestamp DESC
            LIMIT ?
        """, (limit,)).fetchall()
        return [dict(r) for r in rows]


def get_recent_alerts(limit: int = 20) -> List[dict]:
    with get_connection() as conn:
        rows = conn.execute("""
            SELECT * FROM alerts
            ORDER BY timestamp DESC
            LIMIT ?
        """, (limit,)).fetchall()
        return [dict(r) for r in rows]


def get_total_readings() -> int:
    with get_connection() as conn:
        return conn.execute("SELECT COUNT(*) FROM telemetry").fetchone()[0]
