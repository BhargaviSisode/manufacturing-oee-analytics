import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

print("[-] Generating Industrial Manufacturing Dataset...")
os.makedirs("data/raw", exist_ok=True)

np.random.seed(42)
n_telemetry = 8000
n_shifts = 1200

# 1. Machine Master & Telemetry
machine_ids = [f"MCH_L{line}_{m:02d}" for line in [1, 2, 3] for m in range(1, 6)] # 15 machines across 3 lines
timestamps = [datetime(2023, 1, 1) + timedelta(minutes=30 * i) for i in range(n_telemetry)]

assigned_machines = np.random.choice(machine_ids, n_telemetry)
air_temps = np.round(np.random.normal(loc=300.0, scale=2.5, size=n_telemetry), 2)  # Kelvin
process_temps = np.round(air_temps + np.random.normal(loc=10.0, scale=1.2, size=n_telemetry), 2)
rotational_speeds = np.random.normal(loc=1500, scale=120, size=n_telemetry).astype(int)
torques = np.round(np.random.normal(loc=40.0, scale=8.5, size=n_telemetry), 2)
tool_wear_min = np.random.randint(0, 240, size=n_telemetry)

failure_types = ["No Failure", "Heat Dissipation", "Power Failure", "Tool Wear", "Overstrain"]
failure_probs = [0.93, 0.025, 0.015, 0.015, 0.015]
assigned_failures = np.random.choice(failure_types, n_telemetry, p=failure_probs)
is_failure = np.where(assigned_failures == "No Failure", 0, 1)

telemetry = pd.DataFrame({
    "log_id": [f"LOG_{i:07d}" for i in range(1, n_telemetry + 1)],
    "machine_id": assigned_machines,
    "timestamp": timestamps,
    "air_temperature_k": air_temps,
    "process_temperature_k": process_temps,
    "rotational_speed_rpm": rotational_speeds,
    "torque_nm": torques,
    "tool_wear_minutes": tool_wear_min,
    "failure_type": assigned_failures,
    "machine_failed": is_failure
})

# 2. Shift Production & Downtime Logs (OEE Base)
shift_dates = [datetime(2023, 1, 1) + timedelta(hours=8 * i) for i in range(n_shifts)]
shifts = ["Shift A (Morning)", "Shift B (Evening)", "Shift C (Night)"]

production_logs = []
for i in range(n_shifts):
    m_id = np.random.choice(machine_ids)
    s_type = shifts[i % 3]
    planned_mins = 480 # Standard 8-hour shift
    
    # 30% chance of unplanned stoppage
    has_stop = np.random.choice([0, 1], p=[0.70, 0.30])
    downtime_mins = int(np.random.exponential(scale=40)) if has_stop else 0
    downtime_mins = min(downtime_mins, 360) # cap at 6 hours max
    operating_mins = planned_mins - downtime_mins
    
    ideal_run_rate = 2.0 # 2 parts/min theoretical maximum
    actual_produced = int(operating_mins * ideal_run_rate * np.random.uniform(0.88, 0.98))
    defective = int(actual_produced * np.random.uniform(0.01, 0.05))
    good_units = actual_produced - defective
    
    downtime_reason = "None"
    if downtime_mins > 0:
        downtime_reason = np.random.choice([
            "Tool Breakdown", 
            "Material Starvation", 
            "Calibration Lag", 
            "Pressure Loss"
        ], p=[0.40, 0.25, 0.20, 0.15])
        
    production_logs.append({
        "shift_log_id": f"SFT_{i:05d}",
        "machine_id": m_id,
        "shift_start": shift_dates[i],
        "shift_type": s_type,
        "planned_time_min": planned_mins,
        "operating_time_min": operating_mins,
        "downtime_min": downtime_mins,
        "downtime_reason": downtime_reason,
        "total_units": actual_produced,
        "good_units": good_units,
        "defective_units": defective
    })

shifts_df = pd.DataFrame(production_logs)

telemetry.to_csv("data/raw/machine_telemetry.csv", index=False)
shifts_df.to_csv("data/raw/shift_production_logs.csv", index=False)

print("[✓] Raw manufacturing datasets created successfully!")
print(f"    - Telemetry records: {len(telemetry):,}")
print(f"    - Shift production logs: {len(shifts_df):,}")