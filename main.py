"""
Main pipeline runner
Run this to simulate telemetry ingestion and processing
"""
from src.simulator import stream_telemetry
from src.database import init_db, insert_readings, get_station_summary, get_total_readings
from src.health_engine import process_batch


def run_pipeline(n_readings: int = 200, fault_rate: float = 0.15):
    print("=" * 55)
    print("  EV Telemetry Monitor — Pipeline Run")
    print("=" * 55)

    # Initialize database
    init_db()
    print(f"\n[1/4] Database initialized")

    # Generate simulated telemetry
    readings = stream_telemetry(n=n_readings, fault_rate=fault_rate)
    print(f"[2/4] Generated {len(readings)} telemetry readings ({fault_rate*100:.0f}% fault rate)")

    # Store in SQLite
    count = insert_readings(readings)
    print(f"[3/4] Stored {count} readings in SQLite (total: {get_total_readings()})")

    # Score and alert
    nominal, warning, critical = process_batch(readings)
    print(f"[4/4] Health scoring complete:")
    print(f"       NOMINAL:  {nominal}")
    print(f"       WARNING:  {warning}")
    print(f"       CRITICAL: {critical}")

    # Station summary via SQL
    print("\n--- Station Summary (SQL Query) ---")
    for row in get_station_summary():
        print(f"  {row['station_id']}: {row['total_readings']} readings | "
              f"avg {row['avg_voltage']}V / {row['avg_current']}A | "
              f"{row['fault_count']} faults")

    print("\nPipeline complete. Run `streamlit run dashboard.py` to view dashboard.")
    print("Run `pytest tests/ -v` to execute test suite.")


if __name__ == "__main__":
    run_pipeline()
