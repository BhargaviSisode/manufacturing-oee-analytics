import duckdb

# Connect to in-memory DuckDB
con = duckdb.connect()

# Create a view pointing to your processed mart CSV,
# named to match what the SQL file expects
con.execute("""
    CREATE OR REPLACE VIEW shift_production_logs AS 
    SELECT * FROM read_csv_auto('data/processed/plant_oee_analytical_mart.csv')
""")

print("\n=== KPI 1: OEE by Production Line ===\n")
kpi1 = con.execute("""
    SELECT 
        SUBSTRING(machine_id, 1, 6) AS production_line,
        COUNT(shift_log_id) AS total_shifts,
        ROUND(AVG(operating_time_min::DOUBLE / planned_time_min) * 100, 2) AS avg_availability_pct,
        ROUND(AVG(total_units::DOUBLE / NULLIF(operating_time_min * 2.0, 0)) * 100, 2) AS avg_performance_pct,
        ROUND(AVG(good_units::DOUBLE / NULLIF(total_units, 0)) * 100, 2) AS avg_quality_pct,
        ROUND(
            AVG(operating_time_min::DOUBLE / planned_time_min) * 
            AVG(total_units::DOUBLE / NULLIF(operating_time_min * 2.0, 0)) * 
            AVG(good_units::DOUBLE / NULLIF(total_units, 0)) * 100, 
            2
        ) AS line_oee_pct
    FROM shift_production_logs
    GROUP BY 1
    ORDER BY line_oee_pct ASC
""").df()
print(kpi1)

print("\n=== KPI 2: Pareto Downtime Root-Cause Analysis ===\n")
kpi2 = con.execute("""
    WITH stoppage_totals AS (
        SELECT 
            downtime_reason,
            COUNT(*) AS stoppage_events,
            SUM(downtime_min) AS total_lost_minutes
        FROM shift_production_logs
        WHERE downtime_reason <> 'None'
        GROUP BY downtime_reason
    ),
    pareto_calc AS (
        SELECT 
            downtime_reason,
            stoppage_events,
            total_lost_minutes,
            ROUND((total_lost_minutes::DOUBLE / SUM(total_lost_minutes) OVER ()) * 100, 2) AS pct_share_of_downtime,
            ROUND(
                SUM(total_lost_minutes) OVER (ORDER BY total_lost_minutes DESC)::DOUBLE / 
                SUM(total_lost_minutes) OVER () * 100, 
                2
            ) AS cumulative_pct
        FROM stoppage_totals
    )
    SELECT 
        downtime_reason,
        stoppage_events,
        total_lost_minutes,
        pct_share_of_downtime,
        cumulative_pct,
        CASE 
            WHEN cumulative_pct <= 80.0 THEN 'Primary Focus (Top 80%)'
            ELSE 'Secondary Minor Cause'
        END AS maintenance_triage_priority
    FROM pareto_calc
    ORDER BY total_lost_minutes DESC
""").df()
print(kpi2)

# Optionally save results to CSV
kpi1.to_csv("data/processed/kpi1_oee_by_line.csv", index=False)
kpi2.to_csv("data/processed/kpi2_pareto_downtime.csv", index=False)
print("\n[✔] Results saved to data/processed/")