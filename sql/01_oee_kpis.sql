-- sql/01_oee_kpis.sql: Industrial Production Analytics & Pareto Downtime

-- KPI 1: Overall Equipment Effectiveness (OEE) by Production Line
SELECT 
    SUBSTRING(machine_id FROM 1 FOR 6) AS production_line,
    COUNT(shift_log_id) AS total_shifts,
    ROUND(AVG(operating_time_min::numeric / planned_time_min) * 100, 2) AS avg_availability_pct,
    ROUND(AVG(total_units::numeric / NULLIF(operating_time_min * 2.0, 0)) * 100, 2) AS avg_performance_pct,
    ROUND(AVG(good_units::numeric / NULLIF(total_units, 0)) * 100, 2) AS avg_quality_pct,
    ROUND(
        AVG(operating_time_min::numeric / planned_time_min) * 
        AVG(total_units::numeric / NULLIF(operating_time_min * 2.0, 0)) * 
        AVG(good_units::numeric / NULLIF(total_units, 0)) * 100, 
        2
    ) AS line_oee_pct
FROM shift_production_logs
GROUP BY 1
ORDER BY line_oee_pct ASC;

-- KPI 2: Pareto Root-Cause Analysis on Stoppage Minutes (80/20 Rule)
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
        ROUND((total_lost_minutes::numeric / SUM(total_lost_minutes) OVER ()) * 100, 2) AS pct_share_of_downtime,
        ROUND(
            SUM(total_lost_minutes) OVER (ORDER BY total_lost_minutes DESC)::numeric / 
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
ORDER BY total_lost_minutes DESC;