import os
import pandas as pd
import numpy as np

def run_oee_pipeline():
    print("[-] Processing Manufacturing Operational Data...")
    
    raw_dir = os.path.join("data", "raw")
    processed_dir = os.path.join("data", "processed")
    os.makedirs(processed_dir, exist_ok=True)
    
    shifts = pd.read_csv(os.path.join(raw_dir, "shift_production_logs.csv"))
    
    # 1. Availability = Operating Time / Planned Time
    shifts["availability_pct"] = np.round((shifts["operating_time_min"] / shifts["planned_time_min"]) * 100, 2)
    
    # 2. Performance = Actual Output / (Operating Time * Ideal Run Rate)
    shifts["expected_units"] = shifts["operating_time_min"] * 2.0
    shifts["performance_pct"] = np.where(
        shifts["expected_units"] > 0,
        np.round((shifts["total_units"] / shifts["expected_units"]) * 100, 2),
        0.0
    )
    
    # 3. Quality = Good Units / Total Units Produced
    shifts["quality_pct"] = np.where(
        shifts["total_units"] > 0,
        np.round((shifts["good_units"] / shifts["total_units"]) * 100, 2),
        0.0
    )
    
    # 4. Overall Equipment Effectiveness (OEE) = Availability * Performance * Quality
    shifts["oee_pct"] = np.round(
        (shifts["availability_pct"] / 100.0) * 
        (shifts["performance_pct"] / 100.0) * 
        (shifts["quality_pct"] / 100.0) * 100, 
        2
    )
    
    # Production Line ID
    shifts["production_line"] = shifts["machine_id"].str.slice(0, 6) # e.g. MCH_L1
    
    # Classification category
    conditions = [
        (shifts["oee_pct"] >= 85.0),
        (shifts["oee_pct"] >= 65.0) & (shifts["oee_pct"] < 85.0),
        (shifts["oee_pct"] < 65.0)
    ]
    labels = ["World Class (≥85%)", "Acceptable (65-84%)", "Critical Bottleneck (<65%)"]
    shifts["oee_health_status"] = np.select(conditions, labels, default="Acceptable")
    
    output_path = os.path.join(processed_dir, "plant_oee_analytical_mart.csv")
    shifts.to_csv(output_path, index=False)
    
    print(f"[✓] OEE Analytical Mart created at: {output_path}")
    print(f"    Avg Plant Availability: {shifts['availability_pct'].mean():.2f}%")
    print(f"    Avg Plant Performance:  {shifts['performance_pct'].mean():.2f}%")
    print(f"    Avg Plant Quality:      {shifts['quality_pct'].mean():.2f}%")
    print(f"    Avg Overall OEE:        {shifts['oee_pct'].mean():.2f}%")

if __name__ == "__main__":
    run_oee_pipeline()